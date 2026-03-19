import { ref, computed } from 'vue'
import { contentApi } from '@/api'

export function useLesson(lessonId) {
  const questions        = ref([])
  const currentIndex     = ref(0)
  const selectedAnswer   = ref(null)
  const feedback         = ref(null)
  const correctCount     = ref(0)
  const xpEarned         = ref(0)
  const loading          = ref(true)
  const finished         = ref(false)
  const error            = ref(null)
  const languageCode     = ref(null)   // for TTS
  // Phase 2
  const audioIntroUrl       = ref(null)
  const culturalNote        = ref(null)
  const culturalNoteTitle   = ref(null)
  const pendingCulturalNote = ref(false)
  // Gap 3 — per-question accuracy tracking
  const questionResults = ref([])

  const typedAnswer      = ref('')    // for translate questions where student types
  const currentQuestion = computed(() => questions.value[currentIndex.value] ?? null)

  const progressPercent = computed(() =>
    questions.value.length
      ? (currentIndex.value / questions.value.length) * 100
      : 0
  )

  const correctOptionText = computed(() => {
    if (!feedback.value || feedback.value.correct) return ''
    return (
      currentQuestion.value?.options?.find(
        (o) => o.id === feedback.value.correct_answer_id
      )?.text ?? ''
    )
  })

  function selectAnswer(optionId) {
    if (!feedback.value) selectedAnswer.value = optionId
  }

  // For translate questions: find option ID whose text matches what was typed
  function _resolveTypedAnswer() {
    if (!typedAnswer.value.trim()) return null
    const typed = typedAnswer.value.trim().toLowerCase()
    const match = currentQuestion.value?.options?.find(
      o => (o.text ?? '').toLowerCase() === typed
    )
    return match?.id ?? null
  }

  async function checkAnswer() {
    // For translate questions with typed input, resolve text → option ID
    if (currentQuestion.value?.type === 'translate' && typedAnswer.value.trim()) {
      const resolved = _resolveTypedAnswer()
      // submit as the matched option ID, or use a sentinel that will be wrong
      selectedAnswer.value = resolved ?? '__typed_wrong__'
      if (!resolved) {
        // no option matched — mark wrong immediately without API call
        const correctId = currentQuestion.value.correct_answer_id
        feedback.value = { correct: false, correct_answer_id: correctId }
        questionResults.value.push({
          question_id: currentQuestion.value.id,
          correct: false,
          answer_given: typedAnswer.value.trim(),
          correct_answer: correctId,
        })
        return
      }
    }
    if (!selectedAnswer.value) return
    try {
      const { data } = await contentApi.submitAnswer({
        lesson_id: lessonId,
        question_id: currentQuestion.value.id,
        answer_id: selectedAnswer.value,
      })
      feedback.value = data
      if (data.correct) {
        correctCount.value++
        xpEarned.value += data.xp_earned ?? 0
      }
      // Track per-question result (Gap 3)
      questionResults.value.push({
        question_id: currentQuestion.value.id,
        correct: data.correct,
        answer_given: selectedAnswer.value,
        correct_answer: data.correct_answer_id,
      })
    } catch (err) {
      console.error('Answer submission failed:', err)
      error.value = 'Could not submit answer. Check your connection.'
    }
  }

  async function nextQuestion() {
    if (currentIndex.value < questions.value.length - 1) {
      currentIndex.value++
      selectedAnswer.value = null
      typedAnswer.value = ''
      feedback.value = null
    } else {
      await _finishLesson()
    }
  }

  async function _finishLesson() {
    const score = questions.value.length
      ? Math.round((correctCount.value / questions.value.length) * 100)
      : 0
    try {
      await contentApi.completeLesson(lessonId, score, questionResults.value)
    } catch { /* non-blocking */ }

    if (culturalNote.value) {
      pendingCulturalNote.value = true
    } else {
      finished.value = true
    }
  }

  function dismissCulturalNote() {
    pendingCulturalNote.value = false
    finished.value = true
  }

  function answerClass(optionId) {
    if (!feedback.value) {
      return selectedAnswer.value === optionId
        ? 'border-emerald-500 bg-emerald-50 text-emerald-800'
        : 'border-slate-100 text-slate-700 hover:border-emerald-200 hover:bg-emerald-50'
    }
    if (optionId === feedback.value.correct_answer_id)
      return 'border-emerald-500 bg-emerald-50 text-emerald-800'
    if (optionId === selectedAnswer.value && !feedback.value.correct)
      return 'border-red-400 bg-red-50 text-red-700'
    return 'border-slate-100 text-slate-400'
  }

  async function load() {
    loading.value = true
    try {
      const { data } = await contentApi.getLesson(lessonId)
      questions.value         = data?.questions ?? []
      audioIntroUrl.value     = data?.audio_intro_url ?? null
      culturalNote.value      = data?.cultural_note ?? null
      culturalNoteTitle.value = data?.cultural_note_title ?? null
      languageCode.value      = data?.language_code ?? null
    } catch (err) {
      error.value = 'Failed to load lesson.'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  return {
    questions, currentIndex, currentQuestion, selectedAnswer, typedAnswer,
    feedback, correctCount, xpEarned, correctOptionText,
    loading, finished, error, progressPercent,
    audioIntroUrl, culturalNote, culturalNoteTitle, pendingCulturalNote,
    languageCode, questionResults,
    selectAnswer, checkAnswer, nextQuestion, dismissCulturalNote, answerClass, load,
  }
}

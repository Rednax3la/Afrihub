import { ref, computed } from 'vue'
import { contentApi } from '@/api'
import { loadLessonState, saveLessonState, clearLessonState } from '@/utils/lessonState'

/**
 * Lesson flow: collect answers locally, then submit once.
 *
 * correct_answer_id is stripped from the lesson the client receives, so no
 * right/wrong is shown and no XP moves while the lesson is in progress. The
 * learner can move back and forth and change any answer freely; a single
 * submit sends everything to the server, which grades it and awards XP exactly
 * once per lesson. That is what makes editing an earlier answer safe.
 */
export function useLesson(lessonId, userId = null) {
  const questions = ref([])
  const currentIndex = ref(0)
  // question_id -> { answer_id } | { answer_text }
  const answers = ref({})
  const loading = ref(true)
  const submitting = ref(false)
  const reviewing = ref(false)   // the "Review answers" step
  const finished = ref(false)
  const error = ref(null)
  const submitError = ref(null)
  const resumed = ref(false)
  const languageCode = ref(null)
  const languageId = ref(null)

  const lessonType = ref('quiz')
  const lessonTitle = ref('')
  const readingContent = ref(null)

  const audioIntroUrl = ref(null)
  const culturalNote = ref(null)
  const culturalNoteTitle = ref(null)
  const pendingCulturalNote = ref(false)

  // Populated only by the completion response.
  const results = ref([])
  const completionScore = ref(0)
  const completionBadges = ref([])
  const completionStreak = ref(null)
  const completionXp = ref(0)
  const xpAlreadyAwarded = ref(false)
  const nextLessonId = ref(null)
  const nextLessonTitle = ref(null)
  const courseComplete = ref(false)

  const currentQuestion = computed(() => questions.value[currentIndex.value] ?? null)
  const total = computed(() => questions.value.length)
  const isLastQuestion = computed(() => currentIndex.value >= total.value - 1)
  const answeredCount = computed(() => Object.keys(answers.value).length)
  const allAnswered = computed(() => total.value > 0 && answeredCount.value >= total.value)

  // Position through the lesson, not a score — nothing is graded yet.
  const progressPercent = computed(() =>
    total.value ? Math.round(((currentIndex.value + 1) / total.value) * 100) : 0
  )

  const correctCount = computed(() => results.value.filter(r => r.correct).length)

  function isAnswered(questionId) {
    return questionId in answers.value
  }

  function answerFor(questionId) {
    return answers.value[questionId] ?? null
  }

  /** The selected option id for a question, if the answer was a choice. */
  function selectedFor(questionId) {
    return answers.value[questionId]?.answer_id ?? null
  }

  function typedFor(questionId) {
    return answers.value[questionId]?.answer_text ?? ''
  }

  function resultFor(questionId) {
    return results.value.find(r => r.question_id === questionId) ?? null
  }

  function optionText(question, optionId) {
    return (question?.options ?? []).find(o => o.id === optionId)?.text ?? ''
  }

  function _persist() {
    if (finished.value) return
    saveLessonState(userId, lessonId, {
      currentIndex: currentIndex.value,
      answers: answers.value,
      reviewing: reviewing.value,
    })
  }

  function selectAnswer(optionId) {
    const question = currentQuestion.value
    if (!question) return
    answers.value = { ...answers.value, [question.id]: { answer_id: optionId } }
    _persist()
  }

  function setTypedAnswer(text) {
    const question = currentQuestion.value
    if (!question) return
    const next = { ...answers.value }
    if (text?.trim()) next[question.id] = { answer_text: text }
    else delete next[question.id]
    answers.value = next
    _persist()
  }

  function clearAnswer(questionId) {
    const next = { ...answers.value }
    delete next[questionId]
    answers.value = next
    _persist()
  }

  function goTo(index) {
    if (index < 0 || index >= total.value) return
    reviewing.value = false
    currentIndex.value = index
    _persist()
  }

  function previous() {
    if (reviewing.value) {
      reviewing.value = false
      currentIndex.value = Math.max(0, total.value - 1)
    } else if (currentIndex.value > 0) {
      currentIndex.value--
    }
    _persist()
  }

  /** Advance, or open the review step after the final question. */
  function next() {
    if (isLastQuestion.value) reviewing.value = true
    else currentIndex.value++
    _persist()
  }

  async function submit() {
    if (submitting.value) return
    submitting.value = true
    submitError.value = null
    try {
      const payload = questions.value
        .filter(q => isAnswered(q.id))
        .map(q => ({ question_id: q.id, ...answers.value[q.id] }))
      const { data } = await contentApi.completeLesson(lessonId, { answers: payload })
      _applyCompletion(data)
      return true
    } catch (err) {
      submitError.value =
        err.response?.data?.detail || 'Could not submit your answers. Check your connection.'
      return false
    } finally {
      submitting.value = false
    }
  }

  function _applyCompletion(data) {
    results.value = data?.results ?? []
    completionScore.value = data?.score ?? 0
    completionXp.value = data?.xp_earned ?? 0
    xpAlreadyAwarded.value = data?.xp_already_awarded ?? false
    completionStreak.value = data?.streak ?? 0
    completionBadges.value = data?.new_badges ?? []
    nextLessonId.value = data?.next_lesson_id ?? null
    nextLessonTitle.value = data?.next_lesson_title ?? null
    courseComplete.value = data?.course_complete ?? false
    if (data?.language_id) languageId.value = data.language_id

    // The saved resume point is no longer meaningful once the lesson is done.
    clearLessonState(userId, lessonId)
    reviewing.value = false

    if (culturalNote.value) pendingCulturalNote.value = true
    else finished.value = true

    // Refresh the user so XP, streak and badges are current everywhere.
    import('@/stores/auth').then(({ useAuthStore }) => useAuthStore().fetchMe())
  }

  function dismissCulturalNote() {
    pendingCulturalNote.value = false
    finished.value = true
  }

  async function completeReading() {
    if (submitting.value) return
    submitting.value = true
    submitError.value = null
    try {
      const { data } = await contentApi.completeLesson(lessonId, { score: 100 })
      _applyCompletion(data)
    } catch (err) {
      submitError.value = err.response?.data?.detail || 'Could not save your progress.'
    } finally {
      submitting.value = false
    }
  }

  /** Tailwind classes for an option button. Pre-submit: selection only. */
  function answerClass(question, optionId) {
    const result = resultFor(question.id)
    if (!result) {
      return selectedFor(question.id) === optionId
        ? 'border-[#00A3C1] bg-[#A7FFEB]/30 text-[#003B5C]'
        : 'border-slate-100 text-slate-700 hover:border-[#00A3C1] hover:bg-[#A7FFEB]/20'
    }
    if (optionId === result.correct_answer_id) return 'border-[#00A3C1] bg-[#A7FFEB]/30 text-[#003B5C]'
    if (optionId === result.answer_given && !result.correct) return 'border-red-400 bg-red-50 text-red-700'
    return 'border-slate-100 text-slate-400'
  }

  async function load() {
    loading.value = true
    try {
      const { data } = await contentApi.getLesson(lessonId)
      questions.value = data?.questions ?? []
      audioIntroUrl.value = data?.audio_intro_url ?? null
      culturalNote.value = data?.cultural_note ?? null
      culturalNoteTitle.value = data?.cultural_note_title ?? null
      languageCode.value = data?.language_code ?? null
      languageId.value = data?.language_id ?? null
      lessonType.value = data?.lesson_type ?? 'quiz'
      lessonTitle.value = data?.title ?? ''
      readingContent.value = data?.reading_content ?? null

      const saved = loadLessonState(userId, lessonId)
      if (saved && questions.value.length) {
        const validIds = new Set(questions.value.map(q => q.id))
        const restored = Object.fromEntries(
          Object.entries(saved.answers ?? {}).filter(([id]) => validIds.has(id))
        )
        answers.value = restored
        currentIndex.value = Math.min(saved.currentIndex ?? 0, questions.value.length - 1)
        reviewing.value = !!saved.reviewing
        resumed.value = Object.keys(restored).length > 0 || currentIndex.value > 0
      }
    } catch (err) {
      error.value =
        err.response?.status === 403
          ? 'This unit requires Premium. Upgrade from your dashboard to continue.'
          : 'Failed to load lesson. Check your connection.'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  return {
    questions, currentIndex, currentQuestion, answers, results,
    total, isLastQuestion, answeredCount, allAnswered, progressPercent, correctCount,
    loading, submitting, reviewing, finished, error, submitError, resumed,
    languageCode, languageId, lessonType, lessonTitle, readingContent,
    audioIntroUrl, culturalNote, culturalNoteTitle, pendingCulturalNote,
    completionScore, completionBadges, completionStreak, completionXp, xpAlreadyAwarded,
    nextLessonId, nextLessonTitle, courseComplete,
    isAnswered, answerFor, selectedFor, typedFor, resultFor, optionText,
    selectAnswer, setTypedAnswer, clearAnswer,
    goTo, previous, next, submit, answerClass,
    dismissCulturalNote, completeReading, load,
  }
}

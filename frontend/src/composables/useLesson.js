/**
 * useLesson — composable that drives quiz state for LessonView.
 *
 * Separates all quiz logic from the view template so it's
 * easy to test, reuse, or swap out the question engine later.
 */
import { ref, computed } from 'vue'
import { contentApi } from '@/api'

export function useLesson(lessonId) {
  const questions   = ref([])
  const currentIndex = ref(0)
  const selectedAnswer = ref(null)
  const feedback    = ref(null)   // { correct, correct_answer_id, xp_earned }
  const correctCount = ref(0)
  const xpEarned   = ref(0)
  const loading    = ref(true)
  const finished   = ref(false)
  const error      = ref(null)

  // ── Computed ────────────────────────────────────────────────────────────────
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

  // ── Actions ─────────────────────────────────────────────────────────────────
  function selectAnswer(optionId) {
    if (!feedback.value) selectedAnswer.value = optionId
  }

  async function checkAnswer() {
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
    } catch (err) {
      console.error('Answer submission failed:', err)
      error.value = 'Could not submit answer. Check your connection.'
    }
  }

  async function nextQuestion() {
    if (currentIndex.value < questions.value.length - 1) {
      currentIndex.value++
      selectedAnswer.value = null
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
      await contentApi.completeLesson(lessonId, score)
    } catch { /* non-blocking */ }
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

  // ── Init ────────────────────────────────────────────────────────────────────
  async function load() {
    loading.value = true
    try {
      const { data } = await contentApi.getLesson(lessonId)
      questions.value = data?.questions ?? []
    } catch (err) {
      error.value = 'Failed to load lesson.'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  return {
    questions,
    currentIndex,
    currentQuestion,
    selectedAnswer,
    feedback,
    correctCount,
    xpEarned,
    correctOptionText,
    loading,
    finished,
    error,
    progressPercent,
    selectAnswer,
    checkAnswer,
    nextQuestion,
    answerClass,
    load,
  }
}

<template>
  <section class="min-h-screen bg-[#FDFCFB] flex flex-col md:pl-64">
    <div class="flex-1 flex flex-col max-w-xl mx-auto w-full">

      <!-- Loading -->
      <div v-if="lesson.loading" class="flex-1 flex items-center justify-center">
        <div class="w-10 h-10 border-4 border-[#A7FFEB] border-t-[#00A3C1] rounded-full animate-spin"></div>
      </div>

      <!-- Error -->
      <div v-else-if="lesson.error" class="flex-1 flex flex-col items-center justify-center p-8 text-center">
        <span class="material-icons-outlined text-4xl text-slate-300 mb-3">error_outline</span>
        <p class="text-slate-500 font-medium mb-6">{{ lesson.error }}</p>
        <RouterLink to="/dashboard" class="bg-[#003B5C] text-white px-6 py-3 rounded-2xl font-bold">Back to Dashboard</RouterLink>
      </div>

      <!-- Cultural Note screen -->
      <div v-else-if="showCulturalNote" class="flex-1 flex flex-col p-6 justify-center">
        <div class="w-14 h-14 bg-amber-100 rounded-2xl flex items-center justify-center mb-5">
          <span class="material-icons-outlined text-amber-600 text-3xl">auto_stories</span>
        </div>
        <p class="text-xs font-bold tracking-widest text-amber-600 uppercase mb-2">Cultural Note</p>
        <h2 class="text-2xl font-bold text-slate-900 mb-4 leading-snug">
          {{ lesson.culturalNoteTitle || 'Did you know?' }}
        </h2>
        <p class="text-slate-600 leading-relaxed text-base">{{ lesson.culturalNote }}</p>
        <button
          @click="lesson.dismissCulturalNote()"
          class="mt-8 w-full py-5 rounded-3xl font-bold text-lg bg-[#003B5C] text-white shadow-lg shadow-[#003B5C]/20 active:scale-95 transition-transform"
        >
          Continue
        </button>
      </div>

      <!-- Badge Celebration Overlay -->
      <div v-else-if="lesson.finished && showBadgeCelebration" class="flex-1 flex flex-col items-center justify-center p-8 text-center">
        <div class="animate-badge-pop text-8xl mb-6">{{ lesson.completionBadges[badgeIndex].icon }}</div>
        <p class="text-xs font-bold tracking-widest text-[#00A3C1] uppercase mb-2">New Badge Unlocked!</p>
        <h2 class="text-3xl font-bold text-slate-900 mb-3">{{ lesson.completionBadges[badgeIndex].name }}</h2>
        <p class="text-slate-500 mb-10">Keep up the great work!</p>
        <button
          @click="nextBadge"
          class="w-full max-w-xs bg-[#003B5C] text-white py-5 rounded-3xl font-bold text-lg shadow-lg shadow-[#003B5C]/20 active:scale-95 transition-transform"
        >
          Continue
        </button>
      </div>

      <!-- Finished Screen -->
      <div v-else-if="lesson.finished" class="flex-1 flex flex-col items-center justify-center p-8 text-center">
        <div class="w-24 h-24 bg-[#A7FFEB]/50 rounded-full flex items-center justify-center mb-6">
          <span class="material-icons-outlined text-[#00A3C1] text-5xl">emoji_events</span>
        </div>
        <h2 class="text-3xl font-bold text-slate-900 mb-2">Lesson Complete!</h2>
        <p class="text-slate-500 mb-8">You answered {{ lesson.correctCount }} of {{ lesson.questions.length }} correctly.</p>

        <div class="flex gap-4 mb-10 w-full max-w-xs">
          <div class="flex-1 bg-[#A7FFEB]/30 rounded-3xl p-4 text-center border border-[#00A3C1]/20">
            <p class="text-2xl font-bold text-[#003B5C]">+{{ animatedXP }}</p>
            <p class="text-xs text-[#00A3C1] font-bold uppercase tracking-wider">XP Earned</p>
          </div>
          <div class="flex-1 bg-amber-50 rounded-3xl p-4 text-center border border-amber-100">
            <p class="text-2xl font-bold text-amber-700">
              {{ lesson.questions.length ? Math.round((lesson.correctCount / lesson.questions.length) * 100) : 0 }}%
            </p>
            <p class="text-xs text-amber-600 font-bold uppercase tracking-wider">Accuracy</p>
          </div>
          <div class="flex-1 bg-orange-50 rounded-3xl p-4 text-center border border-orange-100">
            <p class="text-2xl font-bold text-orange-600">
              <span class="material-icons-outlined text-xl align-middle">local_fire_department</span>{{ lesson.completionStreak ?? 0 }}
            </p>
            <p class="text-xs text-orange-500 font-bold uppercase tracking-wider">Streak</p>
          </div>
        </div>

        <RouterLink
          to="/dashboard"
          class="w-full max-w-xs bg-[#003B5C] text-white py-5 rounded-3xl font-bold text-lg text-center shadow-lg shadow-[#003B5C]/20 block"
        >
          Continue
        </RouterLink>
      </div>

      <!-- Quiz Screen -->
      <template v-else-if="lesson.currentQuestion">
        <!-- Header -->
        <header class="px-6 pt-6 pb-4 flex items-center gap-4">
          <RouterLink to="/dashboard" class="w-10 h-10 flex items-center justify-center text-slate-400 shrink-0">
            <span class="material-icons-outlined">close</span>
          </RouterLink>
          <div class="flex-1 h-3 bg-slate-100 rounded-full overflow-hidden">
            <div
              class="h-full bg-[#00A3C1] rounded-full transition-all duration-500"
              :style="{ width: `${lesson.progressPercent}%` }"
            ></div>
          </div>
          <div class="flex items-center gap-1 shrink-0 bg-amber-50 px-3 py-1.5 rounded-full">
            <span class="material-icons-outlined text-amber-500 text-sm">bolt</span>
            <span class="font-bold text-amber-700 text-sm">{{ lesson.xpEarned }}</span>
          </div>
        </header>

        <!-- Lesson intro audio (first question only) -->
        <div v-if="lesson.audioIntroUrl && lesson.currentIndex === 0" class="px-6 mb-2">
          <AudioPlayer :src="lesson.audioIntroUrl" label="Lesson Introduction" />
        </div>

        <main class="flex-1 px-6 py-4 flex flex-col">
          <!-- Question type label -->
          <p class="text-xs font-bold tracking-widest text-[#00A3C1] uppercase mb-4">
            {{ questionTypeLabel }}
          </p>

          <!-- ── LISTEN ──────────────────────────────────────────────────────── -->
          <template v-if="lesson.currentQuestion.type === 'listen'">
            <div class="bg-[#A7FFEB]/30 border border-[#00A3C1]/20 rounded-[2rem] p-6 mb-6 flex flex-col items-center gap-4 shadow-sm">
              <AudioPlayer :src="lesson.currentQuestion.audio_url" label="Play & Listen" />
              <p class="text-slate-500 text-sm italic">Listen, then choose the correct translation below</p>
            </div>
          </template>

          <!-- ── LISTEN COMPREHENSION ────────────────────────────────────────── -->
          <template v-else-if="lesson.currentQuestion.type === 'listen_comprehension'">
            <div class="bg-blue-50 border border-blue-100 rounded-[2rem] p-6 mb-4 flex flex-col items-center gap-4 shadow-sm">
              <AudioPlayer :src="lesson.currentQuestion.audio_url" label="Listen to the dialogue" />
              <p class="text-slate-500 text-sm italic">Listen carefully, then answer the question</p>
            </div>
            <div class="bg-slate-50 border border-slate-100 rounded-[2rem] p-5 mb-4 text-center">
              <p class="text-lg font-bold text-slate-800">{{ lesson.currentQuestion.prompt }}</p>
            </div>
          </template>

          <!-- ── IMAGE ──────────────────────────────────────────────────────── -->
          <template v-else-if="lesson.currentQuestion.type === 'image'">
            <div class="bg-slate-50 border border-slate-100 rounded-[2rem] overflow-hidden mb-6 shadow-sm">
              <img
                :src="lesson.currentQuestion.image_url"
                :alt="lesson.currentQuestion.prompt"
                class="w-full max-h-52 object-cover"
              />
              <div class="p-4 text-center">
                <p class="text-sm font-semibold text-slate-700">{{ lesson.currentQuestion.prompt }}</p>
              </div>
            </div>
          </template>

          <!-- ── IMAGE TRANSLATE ─────────────────────────────────────────────── -->
          <template v-else-if="lesson.currentQuestion.type === 'image_translate'">
            <div class="bg-slate-50 border border-slate-100 rounded-[2rem] overflow-hidden mb-6 shadow-sm">
              <img
                :src="lesson.currentQuestion.image_url"
                :alt="lesson.currentQuestion.prompt"
                class="w-full max-h-52 object-cover"
              />
              <div class="p-4 text-center">
                <p class="text-sm font-semibold text-slate-700">{{ lesson.currentQuestion.prompt }}</p>
              </div>
            </div>
          </template>

          <!-- ── IMAGE MATCH ─────────────────────────────────────────────────── -->
          <template v-else-if="lesson.currentQuestion.type === 'image_match'">
            <div class="bg-[#A7FFEB]/30 border border-[#00A3C1]/20 rounded-[2rem] p-5 mb-4 text-center shadow-sm">
              <p class="text-2xl font-bold text-[#003B5C]">{{ lesson.currentQuestion.prompt }}</p>
              <p v-if="lesson.currentQuestion.native_text" class="text-slate-400 text-sm mt-1 italic">
                {{ lesson.currentQuestion.native_text }}
              </p>
            </div>
            <div class="grid grid-cols-2 gap-3 flex-1 mb-4">
              <button
                v-for="option in lesson.currentQuestion.options"
                :key="option.id"
                @click="lesson.selectAnswer(option.id)"
                :disabled="!!lesson.feedback"
                class="rounded-2xl border-2 overflow-hidden transition-all"
                :class="imageMatchClass(option.id)"
              >
                <img
                  v-if="option.image_url"
                  :src="option.image_url"
                  :alt="option.text || option.id"
                  class="w-full h-28 object-cover"
                />
                <div v-else class="w-full h-28 bg-slate-100 flex items-center justify-center">
                  <span class="text-slate-400 text-sm">{{ option.text }}</span>
                </div>
              </button>
            </div>
            <div
              v-if="lesson.feedback"
              class="mb-4 p-4 rounded-2xl flex items-start gap-3"
              :class="lesson.feedback.correct ? 'bg-[#A7FFEB]/30 border border-[#00A3C1]/30' : 'bg-red-50 border border-red-200'"
            >
              <span class="material-icons-outlined text-xl mt-0.5" :class="lesson.feedback.correct ? 'text-[#00A3C1]' : 'text-red-500'">
                {{ lesson.feedback.correct ? 'check_circle' : 'cancel' }}
              </span>
              <p class="font-bold" :class="lesson.feedback.correct ? 'text-[#003B5C]' : 'text-red-600'">
                {{ lesson.feedback.correct ? 'Correct!' : 'Not quite — look for the right image' }}
              </p>
            </div>
            <footer class="pb-8 pt-2">
              <button
                v-if="!lesson.feedback"
                @click="lesson.checkAnswer()"
                :disabled="!lesson.selectedAnswer"
                class="w-full py-5 rounded-3xl font-bold text-lg transition-all"
                :class="lesson.selectedAnswer ? 'bg-[#003B5C] text-white shadow-lg shadow-[#003B5C]/20 active:scale-95' : 'bg-slate-100 text-slate-400 cursor-not-allowed'"
              >Check</button>
              <button v-else @click="lesson.nextQuestion()" class="w-full py-5 rounded-3xl font-bold text-lg bg-[#003B5C] text-white shadow-lg shadow-[#003B5C]/20 active:scale-95 transition-transform">
                {{ lesson.currentIndex < lesson.questions.length - 1 ? 'Next' : 'Finish' }}
              </button>
            </footer>
          </template>

          <!-- ── TRANSLATE / MULTIPLE CHOICE ───────────────────────────────── -->
          <template v-else>
            <div class="bg-[#A7FFEB]/30 border border-[#00A3C1]/20 rounded-[2rem] p-6 mb-4 text-center shadow-sm">
              <div class="flex justify-center mb-3 gap-2">
                <AudioPlayer v-if="lesson.currentQuestion.audio_url" :src="lesson.currentQuestion.audio_url" label="Hear Pronunciation" />
                <button
                  v-else-if="lesson.currentQuestion.type === 'translate'"
                  @click="fetchTTS(lesson.currentQuestion.prompt)"
                  :disabled="ttsLoading"
                  class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-sm font-semibold bg-white border border-[#00A3C1]/30 text-[#003B5C] hover:bg-[#A7FFEB]/30 transition-all disabled:opacity-50"
                >
                  <span class="material-icons-outlined text-base">{{ ttsLoading ? 'hourglass_empty' : 'volume_up' }}</span>
                  {{ ttsLoading ? 'Loading…' : 'Hear pronunciation' }}
                </button>
              </div>
              <AudioPlayer v-if="ttsAudioUrl && !lesson.currentQuestion.audio_url" :src="ttsAudioUrl" :autoplay="true" label="Pronunciation" />
              <p class="text-2xl font-bold text-[#003B5C] leading-relaxed">
                {{ lesson.currentQuestion.prompt }}
              </p>
              <p v-if="lesson.currentQuestion.native_text" class="text-slate-400 text-sm mt-2 italic">
                {{ lesson.currentQuestion.native_text }}
              </p>
            </div>
          </template>

          <!-- Answer options (shared, hidden for image_match) -->
          <template v-if="lesson.currentQuestion.type !== 'image_match'">
            <div v-if="lesson.currentQuestion.type === 'translate' && !lesson.feedback" class="flex-1 space-y-2">
              <label class="text-xs font-bold text-slate-400 uppercase tracking-wider">Type your answer</label>
              <input
                v-model="lesson.typedAnswer"
                :disabled="!!lesson.feedback"
                @keydown.enter="lesson.typedAnswer.trim() && lesson.checkAnswer()"
                class="w-full border-2 border-slate-200 rounded-2xl px-4 py-3 text-base font-semibold focus:outline-none focus:border-[#00A3C1] transition-colors"
                placeholder="Type the translation…"
                autocomplete="off"
                autocorrect="off"
                spellcheck="false"
              />
              <SpecialCharKeyboard
                :language-code="lesson.languageCode"
                :model-value="lesson.typedAnswer"
                @update:model-value="lesson.typedAnswer = $event"
              />
            </div>
            <div v-else class="space-y-3 flex-1">
              <button
                v-for="option in lesson.currentQuestion.options"
                :key="option.id"
                @click="lesson.selectAnswer(option.id)"
                :disabled="!!lesson.feedback"
                class="w-full p-4 rounded-2xl border-2 font-semibold text-left transition-all"
                :class="lesson.answerClass(option.id)"
              >
                {{ option.text }}
              </button>
            </div>

            <!-- Feedback banner -->
            <div
              v-if="lesson.feedback"
              class="mt-4 p-4 rounded-2xl flex items-start gap-3"
              :class="lesson.feedback.correct ? 'bg-[#A7FFEB]/30 border border-[#00A3C1]/30' : 'bg-red-50 border border-red-200'"
            >
              <span
                class="material-icons-outlined text-xl mt-0.5"
                :class="lesson.feedback.correct ? 'text-[#00A3C1]' : 'text-red-500'"
              >
                {{ lesson.feedback.correct ? 'check_circle' : 'cancel' }}
              </span>
              <div>
                <p class="font-bold" :class="lesson.feedback.correct ? 'text-[#003B5C]' : 'text-red-600'">
                  {{ lesson.feedback.correct ? 'Correct!' : 'Not quite' }}
                </p>
                <p v-if="!lesson.feedback.correct" class="text-sm text-slate-500 mt-0.5">
                  Correct answer: <span class="font-semibold">{{ lesson.correctOptionText }}</span>
                </p>
              </div>
            </div>
          </template>
        </main>

        <!-- Footer -->
        <footer v-if="lesson.currentQuestion.type !== 'image_match'" class="px-6 pb-8 pt-2">
          <button
            v-if="!lesson.feedback"
            @click="lesson.checkAnswer()"
            :disabled="!lesson.selectedAnswer && !lesson.typedAnswer.trim()"
            class="w-full py-5 rounded-3xl font-bold text-lg transition-all"
            :class="(lesson.selectedAnswer || lesson.typedAnswer.trim())
              ? 'bg-[#003B5C] text-white shadow-lg shadow-[#003B5C]/20 active:scale-95'
              : 'bg-slate-100 text-slate-400 cursor-not-allowed'"
          >
            Check
          </button>
          <button
            v-else
            @click="lesson.nextQuestion()"
            class="w-full py-5 rounded-3xl font-bold text-lg bg-[#003B5C] text-white shadow-lg shadow-[#003B5C]/20 active:scale-95 transition-transform"
          >
            {{ lesson.currentIndex < lesson.questions.length - 1 ? 'Next' : 'Finish' }}
          </button>
        </footer>
      </template>

    </div>
  </section>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useLesson } from '@/composables/useLesson'
import { ttsApi } from '@/api'
import AudioPlayer from '@/components/AudioPlayer.vue'
import SpecialCharKeyboard from '@/components/SpecialCharKeyboard.vue'

const route = useRoute()
const lesson = useLesson(route.params.id)

// TTS state
const ttsAudioUrl = ref(null)
const ttsLoading = ref(false)

// Badge celebration state
const badgeIndex = ref(0)
const badgesDismissed = ref(false)

const showBadgeCelebration = computed(() =>
  !badgesDismissed.value && lesson.completionBadges.value.length > 0
)

function nextBadge() {
  if (badgeIndex.value < lesson.completionBadges.value.length - 1) {
    badgeIndex.value++
  } else {
    badgesDismissed.value = true
  }
}

// XP count-up animation using completionXp from the API response
const animatedXP = ref(0)
watch(() => lesson.finished.value, (isFinished) => {
  if (!isFinished) return
  const target = lesson.completionXp.value
  if (!target) return
  let current = 0
  const step = Math.max(1, Math.ceil(target / 30))
  const interval = setInterval(() => {
    current = Math.min(current + step, target)
    animatedXP.value = current
    if (current >= target) clearInterval(interval)
  }, 30)
})

// Clear TTS audio when question changes
watch(() => lesson.currentIndex.value, () => { ttsAudioUrl.value = null })

async function fetchTTS(text) {
  if (!text || ttsLoading.value) return
  ttsLoading.value = true
  try {
    const langCode = lesson.languageCode.value || 'yo'
    const { data } = await ttsApi.generate(text, langCode)
    ttsAudioUrl.value = data.audio_url
  } catch {
    // silent fail — TTS is optional
  } finally {
    ttsLoading.value = false
  }
}

const showCulturalNote = computed(() =>
  lesson.pendingCulturalNote.value && !lesson.finished.value
)

const questionTypeLabel = computed(() => {
  const type = lesson.currentQuestion.value?.type
  if (type === 'listen') return 'Listen & choose'
  if (type === 'listen_comprehension') return 'Listen & understand'
  if (type === 'image') return 'What does this show?'
  if (type === 'image_translate') return 'Name what you see'
  if (type === 'image_match') return 'Match the image'
  if (type === 'multiple_choice') return 'Choose the correct answer'
  return 'Translate this phrase'
})

function imageMatchClass(optionId) {
  if (!lesson.feedback.value) {
    return lesson.selectedAnswer.value === optionId
      ? 'border-[#00A3C1] ring-2 ring-[#00E5FF]/40'
      : 'border-slate-200 hover:border-[#00A3C1]'
  }
  if (optionId === lesson.feedback.value.correct_answer_id) return 'border-[#00A3C1] ring-2 ring-[#00E5FF]/40'
  if (optionId === lesson.selectedAnswer.value && !lesson.feedback.value.correct) return 'border-red-400 ring-2 ring-red-200'
  return 'border-slate-100 opacity-50'
}

onMounted(() => lesson.load())
</script>

<style scoped>
@keyframes badge-pop {
  0%   { transform: scale(0.3); opacity: 0; }
  70%  { transform: scale(1.15); opacity: 1; }
  100% { transform: scale(1); }
}
.animate-badge-pop {
  animation: badge-pop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}
</style>

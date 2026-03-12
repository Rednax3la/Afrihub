<template>
  <section class="min-h-screen bg-[#FDFCFB] flex flex-col md:pl-64">
    <div class="flex-1 flex flex-col max-w-xl mx-auto w-full">

      <!-- Loading -->
      <div v-if="lesson.loading" class="flex-1 flex items-center justify-center">
        <div class="w-10 h-10 border-4 border-emerald-100 border-t-emerald-600 rounded-full animate-spin"></div>
      </div>

      <!-- Error -->
      <div v-else-if="lesson.error" class="flex-1 flex flex-col items-center justify-center p-8 text-center">
        <span class="material-icons-outlined text-4xl text-slate-300 mb-3">error_outline</span>
        <p class="text-slate-500 font-medium mb-6">{{ lesson.error }}</p>
        <RouterLink to="/dashboard" class="bg-emerald-900 text-white px-6 py-3 rounded-2xl font-bold">Back to Dashboard</RouterLink>
      </div>

      <!-- Cultural Note screen (shown after last question, before results) -->
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
          class="mt-8 w-full py-5 rounded-3xl font-bold text-lg bg-emerald-900 text-white shadow-lg shadow-emerald-900/20 active:scale-95 transition-transform"
        >
          Continue
        </button>
      </div>

      <!-- Finished Screen -->
      <div v-else-if="lesson.finished" class="flex-1 flex flex-col items-center justify-center p-8 text-center">
        <div class="w-24 h-24 bg-emerald-100 rounded-full flex items-center justify-center mb-6">
          <span class="material-icons-outlined text-emerald-600 text-5xl">emoji_events</span>
        </div>
        <h2 class="text-3xl font-bold text-slate-900 mb-2">Lesson Complete!</h2>
        <p class="text-slate-500 mb-8">You answered {{ lesson.correctCount }} of {{ lesson.questions.length }} correctly.</p>

        <div class="flex gap-4 mb-10 w-full max-w-xs">
          <div class="flex-1 bg-emerald-50 rounded-3xl p-4 text-center border border-emerald-100">
            <p class="text-2xl font-bold text-emerald-700">+{{ lesson.xpEarned }}</p>
            <p class="text-xs text-emerald-600 font-bold uppercase tracking-wider">XP Earned</p>
          </div>
          <div class="flex-1 bg-amber-50 rounded-3xl p-4 text-center border border-amber-100">
            <p class="text-2xl font-bold text-amber-700">
              {{ lesson.questions.length ? Math.round((lesson.correctCount / lesson.questions.length) * 100) : 0 }}%
            </p>
            <p class="text-xs text-amber-600 font-bold uppercase tracking-wider">Accuracy</p>
          </div>
        </div>

        <RouterLink
          to="/dashboard"
          class="w-full max-w-xs bg-emerald-900 text-white py-5 rounded-3xl font-bold text-lg text-center shadow-lg shadow-emerald-900/20 block"
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
              class="h-full bg-emerald-500 rounded-full transition-all duration-500"
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
          <p class="text-xs font-bold tracking-widest text-emerald-700 uppercase mb-4">
            {{ questionTypeLabel }}
          </p>

          <!-- LISTEN: audio player as the prompt -->
          <template v-if="lesson.currentQuestion.type === 'listen'">
            <div class="bg-emerald-50 border border-emerald-100 rounded-[2rem] p-6 mb-6 flex flex-col items-center gap-4 shadow-sm">
              <AudioPlayer :src="lesson.currentQuestion.audio_url" label="Play & Listen" />
              <p class="text-slate-500 text-sm italic">Listen, then choose the correct translation below</p>
            </div>
          </template>

          <!-- IMAGE: image as the prompt -->
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

          <!-- TRANSLATE / MULTIPLE CHOICE: text prompt -->
          <template v-else>
            <div class="bg-emerald-50 border border-emerald-100 rounded-[2rem] p-6 mb-4 text-center shadow-sm">
              <div v-if="lesson.currentQuestion.audio_url" class="flex justify-center mb-3">
                <AudioPlayer :src="lesson.currentQuestion.audio_url" label="Hear Pronunciation" />
              </div>
              <p class="text-2xl font-bold text-emerald-950 leading-relaxed">
                {{ lesson.currentQuestion.prompt }}
              </p>
              <p v-if="lesson.currentQuestion.native_text" class="text-slate-400 text-sm mt-2 italic">
                {{ lesson.currentQuestion.native_text }}
              </p>
            </div>
          </template>

          <!-- Answer options -->
          <div class="space-y-3 flex-1">
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
            :class="lesson.feedback.correct ? 'bg-emerald-50 border border-emerald-200' : 'bg-red-50 border border-red-200'"
          >
            <span
              class="material-icons-outlined text-xl mt-0.5"
              :class="lesson.feedback.correct ? 'text-emerald-600' : 'text-red-500'"
            >
              {{ lesson.feedback.correct ? 'check_circle' : 'cancel' }}
            </span>
            <div>
              <p class="font-bold" :class="lesson.feedback.correct ? 'text-emerald-700' : 'text-red-600'">
                {{ lesson.feedback.correct ? 'Correct!' : 'Not quite' }}
              </p>
              <p v-if="!lesson.feedback.correct" class="text-sm text-slate-500 mt-0.5">
                Correct answer: <span class="font-semibold">{{ lesson.correctOptionText }}</span>
              </p>
            </div>
          </div>
        </main>

        <!-- Footer -->
        <footer class="px-6 pb-8 pt-2">
          <button
            v-if="!lesson.feedback"
            @click="lesson.checkAnswer()"
            :disabled="!lesson.selectedAnswer"
            class="w-full py-5 rounded-3xl font-bold text-lg transition-all"
            :class="lesson.selectedAnswer
              ? 'bg-emerald-900 text-white shadow-lg shadow-emerald-900/20 active:scale-95'
              : 'bg-slate-100 text-slate-400 cursor-not-allowed'"
          >
            Check
          </button>
          <button
            v-else
            @click="lesson.nextQuestion()"
            class="w-full py-5 rounded-3xl font-bold text-lg bg-emerald-900 text-white shadow-lg shadow-emerald-900/20 active:scale-95 transition-transform"
          >
            {{ lesson.currentIndex < lesson.questions.length - 1 ? 'Next' : 'Finish' }}
          </button>
        </footer>
      </template>

    </div>
  </section>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useLesson } from '@/composables/useLesson'
import AudioPlayer from '@/components/AudioPlayer.vue'

const route = useRoute()
const lesson = useLesson(route.params.id)

const showCulturalNote = computed(() =>
  lesson.pendingCulturalNote.value && !lesson.finished.value
)

const questionTypeLabel = computed(() => {
  const type = lesson.currentQuestion.value?.type
  if (type === 'listen') return 'Listen & choose'
  if (type === 'image') return 'What does this show?'
  if (type === 'multiple_choice') return 'Choose the correct answer'
  return 'Translate this phrase'
})

onMounted(() => lesson.load())
</script>

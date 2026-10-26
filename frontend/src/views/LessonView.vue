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
        <button class="bg-[#003B5C] text-white px-6 py-3 rounded-2xl font-bold" @click="leaveLesson">
          Back to course
        </button>
      </div>

      <!-- ── READING CARD SCREEN ──────────────────────────────────────── -->
      <div v-else-if="lesson.lessonType === 'reading' && !lesson.finished" class="flex-1 flex flex-col">
        <header class="px-6 pt-6 pb-4 flex items-center gap-4">
          <button class="w-10 h-10 flex items-center justify-center text-slate-400 shrink-0" aria-label="Back to course" @click="leaveLesson">
            <span class="material-icons-outlined">arrow_back</span>
          </button>
          <div class="flex-1 h-3 bg-slate-100 rounded-full overflow-hidden">
            <div class="h-full bg-[#00A3C1] rounded-full w-full"></div>
          </div>
        </header>

        <main class="flex-1 px-6 py-4 overflow-y-auto">
          <p class="text-xs font-bold tracking-widest text-[#0D9488] uppercase mb-4">Read &amp; Learn</p>
          <div class="bg-white border border-slate-100 rounded-[2rem] shadow-sm p-6 mb-6">
            <h2 class="text-2xl font-bold text-[#003B5C] mb-4">{{ lesson.lessonTitle }}</h2>
            <p class="text-slate-700 leading-relaxed text-base whitespace-pre-line">{{ lesson.readingContent }}</p>
          </div>

          <div v-if="lesson.questions.length" class="space-y-3">
            <p class="text-xs font-bold tracking-widest text-slate-400 uppercase mb-3">Key Vocabulary</p>
            <div
              v-for="q in lesson.questions"
              :key="q.id"
              class="bg-[#A7FFEB]/20 border border-[#00A3C1]/20 rounded-2xl p-4 flex items-center gap-4"
            >
              <div class="flex-1">
                <p class="font-bold text-[#003B5C] text-lg">{{ q.prompt }}</p>
                <p class="text-slate-500 text-sm mt-0.5">{{ q.native_text }}</p>
              </div>
              <button
                v-if="lesson.languageCode"
                class="w-10 h-10 bg-white border border-[#00A3C1]/30 rounded-xl flex items-center justify-center text-[#00A3C1] shrink-0"
                @click="fetchTTS(q.prompt)"
              >
                <span class="material-icons-outlined text-xl">volume_up</span>
              </button>
            </div>
          </div>
        </main>

        <footer class="px-6 pb-8 pt-2 safe-bottom">
          <p v-if="lesson.submitError" role="alert" class="mb-3 text-sm font-medium text-red-600">{{ lesson.submitError }}</p>
          <button
            :disabled="lesson.submitting"
            class="w-full py-5 rounded-3xl font-bold text-lg bg-[#003B5C] text-white shadow-lg shadow-[#003B5C]/20 active:scale-95 transition-transform disabled:opacity-60"
            @click="lesson.completeReading()"
          >
            {{ lesson.submitting ? 'Saving…' : 'Got it — Continue' }}
          </button>
        </footer>
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
          class="mt-8 w-full py-5 rounded-3xl font-bold text-lg bg-[#003B5C] text-white shadow-lg shadow-[#003B5C]/20 active:scale-95 transition-transform"
          @click="lesson.dismissCulturalNote()"
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
          class="w-full max-w-xs bg-[#003B5C] text-white py-5 rounded-3xl font-bold text-lg shadow-lg shadow-[#003B5C]/20 active:scale-95 transition-transform"
          @click="nextBadge"
        >
          Continue
        </button>
      </div>

      <!-- ── RESULTS SCREEN ───────────────────────────────────────────── -->
      <div v-else-if="lesson.finished" class="flex-1 flex flex-col px-6 py-8 safe-bottom">
        <div class="flex flex-col items-center text-center">
          <div class="w-20 h-20 bg-[#A7FFEB]/50 rounded-full flex items-center justify-center mb-5">
            <span class="material-icons-outlined text-[#00A3C1] text-4xl">emoji_events</span>
          </div>
          <h2 class="text-3xl font-bold text-slate-900 mb-1">Lesson Complete!</h2>
          <p class="text-slate-500 mb-7">
            You answered {{ lesson.correctCount }} of {{ lesson.questions.length }} correctly.
          </p>
        </div>

        <div class="flex gap-3 mb-8">
          <div class="flex-1 bg-[#A7FFEB]/30 rounded-3xl p-4 text-center border border-[#00A3C1]/20">
            <p class="text-2xl font-bold text-[#003B5C]">+{{ animatedXP }}</p>
            <p class="text-[10px] text-[#00A3C1] font-bold uppercase tracking-wider">XP Earned</p>
          </div>
          <div class="flex-1 bg-amber-50 rounded-3xl p-4 text-center border border-amber-100">
            <p class="text-2xl font-bold text-amber-700">{{ lesson.completionScore }}%</p>
            <p class="text-[10px] text-amber-600 font-bold uppercase tracking-wider">Accuracy</p>
          </div>
          <div class="flex-1 bg-orange-50 rounded-3xl p-4 text-center border border-orange-100">
            <p class="text-2xl font-bold text-orange-600">
              <span class="material-icons-outlined text-xl align-middle">local_fire_department</span>{{ lesson.completionStreak ?? 0 }}
            </p>
            <p class="text-[10px] text-orange-500 font-bold uppercase tracking-wider">Streak</p>
          </div>
        </div>

        <p v-if="lesson.xpAlreadyAwarded" class="-mt-5 mb-7 text-center text-xs text-slate-400">
          You already earned XP for this lesson — practising again is free.
        </p>

        <!-- Per-question breakdown, with the correct answers the server just revealed -->
        <div v-if="lesson.results.length" class="space-y-2 mb-8">
          <p class="text-xs font-bold tracking-widest text-slate-400 uppercase mb-2">Your answers</p>
          <div
            v-for="(question, index) in lesson.questions"
            :key="question.id"
            class="rounded-2xl border p-4"
            :class="lesson.resultFor(question.id)?.correct ? 'border-[#00A3C1]/30 bg-[#A7FFEB]/20' : 'border-red-200 bg-red-50'"
          >
            <div class="flex items-start gap-3">
              <span
                class="material-icons-outlined text-xl mt-0.5 shrink-0"
                :class="lesson.resultFor(question.id)?.correct ? 'text-[#00A3C1]' : 'text-red-500'"
              >{{ lesson.resultFor(question.id)?.correct ? 'check_circle' : 'cancel' }}</span>
              <div class="min-w-0 flex-1">
                <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Question {{ index + 1 }}</p>
                <p class="font-semibold text-slate-800 break-words">{{ question.prompt }}</p>
                <p class="mt-1 text-sm text-slate-600 break-words">
                  Your answer:
                  <span class="font-semibold">{{ displayAnswer(question) || '— skipped —' }}</span>
                </p>
                <p v-if="!lesson.resultFor(question.id)?.correct" class="text-sm text-slate-600 break-words">
                  Correct answer:
                  <span class="font-semibold text-[#003B5C]">{{ lesson.resultFor(question.id)?.correct_answer_text || '—' }}</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-auto space-y-3">
          <button
            class="w-full bg-[#003B5C] text-white py-5 rounded-3xl font-bold text-lg shadow-lg shadow-[#003B5C]/20 active:scale-95 transition-transform"
            @click="goToNextLesson"
          >
            {{ lesson.courseComplete ? 'Finish course' : 'Next lesson' }}
          </button>
          <button
            class="w-full bg-slate-100 text-slate-700 py-4 rounded-3xl font-bold active:scale-95 transition-transform"
            @click="leaveLesson"
          >
            Back to course
          </button>
        </div>
      </div>

      <!-- ── REVIEW ANSWERS STEP ──────────────────────────────────────── -->
      <div v-else-if="lesson.reviewing" class="flex-1 flex flex-col">
        <header class="px-6 pt-6 pb-4 flex items-center gap-4">
          <button class="w-10 h-10 flex items-center justify-center text-slate-400 shrink-0" aria-label="Back to course" @click="leaveLesson">
            <span class="material-icons-outlined">arrow_back</span>
          </button>
          <ProgressDots
            :current="-1"
            :is-answered="id => lesson.isAnswered(id)"
            :questions="lesson.questions"
            @select="lesson.goTo"
          />
        </header>

        <main class="flex-1 px-6 py-2 overflow-y-auto">
          <h2 class="text-2xl font-bold text-[#003B5C] mb-1">Review your answers</h2>
          <p class="text-slate-500 text-sm mb-5">
            Tap any question to change it. Nothing is marked until you submit.
          </p>

          <ul class="space-y-2">
            <li v-for="(question, index) in lesson.questions" :key="question.id">
              <button
                class="w-full text-left rounded-2xl border p-4 transition-colors active:scale-[0.99]"
                :class="lesson.isAnswered(question.id)
                  ? 'border-[#00A3C1]/30 bg-white hover:border-[#00A3C1]'
                  : 'border-amber-200 bg-amber-50'"
                @click="lesson.goTo(index)"
              >
                <div class="flex items-start gap-3">
                  <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-bold text-slate-600">
                    {{ index + 1 }}
                  </span>
                  <div class="min-w-0 flex-1">
                    <p class="font-semibold text-slate-800 break-words">{{ question.prompt || questionTypeLabel(question) }}</p>
                    <p
                      class="mt-0.5 text-sm break-words"
                      :class="lesson.isAnswered(question.id) ? 'text-slate-600' : 'text-amber-700 font-medium'"
                    >
                      {{ displayAnswer(question) || 'Not answered yet' }}
                    </p>
                  </div>
                  <span class="material-icons-outlined text-slate-300 shrink-0">edit</span>
                </div>
              </button>
            </li>
          </ul>
        </main>

        <footer class="px-6 pb-8 pt-3 safe-bottom">
          <p v-if="lesson.submitError" role="alert" class="mb-3 text-sm font-medium text-red-600">{{ lesson.submitError }}</p>
          <p v-else-if="!lesson.allAnswered" class="mb-3 text-sm text-amber-700">
            {{ lesson.total - lesson.answeredCount }} question{{ lesson.total - lesson.answeredCount === 1 ? '' : 's' }}
            still unanswered — skipped questions count as incorrect.
          </p>
          <div class="flex gap-3">
            <button
              class="rounded-3xl bg-slate-100 px-6 py-4 font-bold text-slate-700 active:scale-95 transition-transform"
              @click="lesson.previous()"
            >
              Back
            </button>
            <button
              :disabled="lesson.submitting"
              class="flex-1 rounded-3xl bg-[#003B5C] py-4 font-bold text-lg text-white shadow-lg shadow-[#003B5C]/20 active:scale-95 transition-transform disabled:opacity-60"
              @click="lesson.submit()"
            >
              {{ lesson.submitting ? 'Submitting…' : 'Submit answers' }}
            </button>
          </div>
        </footer>
      </div>

      <!-- ── QUESTION SCREEN ──────────────────────────────────────────── -->
      <template v-else-if="lesson.currentQuestion">
        <header class="px-6 pt-6 pb-3 flex items-center gap-3">
          <button class="w-10 h-10 flex items-center justify-center text-slate-400 shrink-0" aria-label="Back to course" @click="leaveLesson">
            <span class="material-icons-outlined">arrow_back</span>
          </button>
          <ProgressDots
            :current="lesson.currentIndex"
            :is-answered="id => lesson.isAnswered(id)"
            :questions="lesson.questions"
            @select="lesson.goTo"
          />
          <span class="shrink-0 text-xs font-bold text-slate-400 tabular-nums">
            {{ lesson.currentIndex + 1 }}/{{ lesson.total }}
          </span>
        </header>

        <p v-if="lesson.resumed" class="mx-6 mb-2 rounded-xl bg-[#A7FFEB]/30 px-3 py-2 text-xs font-semibold text-[#003B5C]">
          <span class="material-icons-outlined align-middle text-sm">history</span>
          Resumed where you left off
        </p>

        <div v-if="lesson.audioIntroUrl && lesson.currentIndex === 0" class="px-6 mb-2">
          <AudioPlayer :src="lesson.audioIntroUrl" label="Lesson Introduction" />
        </div>

        <main class="flex-1 px-6 py-3 flex flex-col">
          <p class="text-xs font-bold tracking-widest text-[#00A3C1] uppercase mb-4">
            {{ questionTypeLabel(lesson.currentQuestion) }}
          </p>

          <!-- ── LISTEN ──────────────────────────────────────────────── -->
          <template v-if="lesson.currentQuestion.type === 'listen'">
            <div class="bg-[#A7FFEB]/30 border border-[#00A3C1]/20 rounded-[2rem] p-6 mb-6 flex flex-col items-center gap-4 shadow-sm">
              <AudioPlayer :src="lesson.currentQuestion.audio_url" label="Play & Listen" />
              <p class="text-slate-500 text-sm italic text-center">Listen, then choose the correct translation below</p>
            </div>
          </template>

          <!-- ── LISTEN COMPREHENSION ────────────────────────────────── -->
          <template v-else-if="lesson.currentQuestion.type === 'listen_comprehension'">
            <div class="bg-blue-50 border border-blue-100 rounded-[2rem] p-6 mb-4 flex flex-col items-center gap-4 shadow-sm">
              <AudioPlayer :src="lesson.currentQuestion.audio_url" label="Listen to the dialogue" />
              <p class="text-slate-500 text-sm italic text-center">Listen carefully, then answer the question</p>
            </div>
            <div class="bg-slate-50 border border-slate-100 rounded-[2rem] p-5 mb-4 text-center">
              <p class="text-lg font-bold text-slate-800">{{ lesson.currentQuestion.prompt }}</p>
            </div>
          </template>

          <!-- ── IMAGE / IMAGE TRANSLATE ─────────────────────────────── -->
          <template v-else-if="['image', 'image_translate'].includes(lesson.currentQuestion.type)">
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

          <!-- ── VIDEO (75% watch gate retained) ─────────────────────── -->
          <template v-else-if="lesson.currentQuestion.type === 'video'">
            <div class="bg-slate-900 rounded-[2rem] overflow-hidden mb-4 shadow-lg">
              <VideoPlayer
                :src="lesson.currentQuestion.video_url"
                :required-progress="0.75"
                :lesson-id="route.params.id"
                :question-id="lesson.currentQuestion.id"
                @progress-met="markVideoWatched(lesson.currentQuestion.id)"
              />
            </div>
            <div class="bg-slate-50 border border-slate-100 rounded-[2rem] p-5 text-center mb-4">
              <p class="text-lg font-bold text-slate-800">{{ lesson.currentQuestion.prompt }}</p>
              <p v-if="!videoWatched" class="text-sm text-amber-600 mt-2 font-medium">
                <span class="material-icons-outlined text-sm align-middle">schedule</span>
                Watch at least 75% of the video to continue
              </p>
            </div>
          </template>

          <!-- ── IMAGE MATCH ─────────────────────────────────────────── -->
          <template v-else-if="lesson.currentQuestion.type === 'image_match'">
            <div class="bg-[#A7FFEB]/30 border border-[#00A3C1]/20 rounded-[2rem] p-5 mb-4 text-center shadow-sm">
              <p class="text-2xl font-bold text-[#003B5C]">{{ lesson.currentQuestion.prompt }}</p>
              <p v-if="lesson.currentQuestion.native_text" class="text-slate-400 text-sm mt-1 italic">
                {{ lesson.currentQuestion.native_text }}
              </p>
            </div>
            <div class="grid grid-cols-2 gap-3 mb-4">
              <button
                v-for="option in lesson.currentQuestion.options"
                :key="option.id"
                class="rounded-2xl border-2 overflow-hidden transition-all"
                :class="lesson.selectedFor(lesson.currentQuestion.id) === option.id
                  ? 'border-[#00A3C1] ring-2 ring-[#00E5FF]/40'
                  : 'border-slate-200 hover:border-[#00A3C1]'"
                @click="lesson.selectAnswer(option.id)"
              >
                <img v-if="option.image_url" :src="option.image_url" :alt="option.text || option.id" class="w-full h-28 object-cover" />
                <div v-else class="w-full h-28 bg-slate-100 flex items-center justify-center">
                  <span class="text-slate-400 text-sm">{{ option.text }}</span>
                </div>
              </button>
            </div>
          </template>

          <!-- ── TRANSLATE / MULTIPLE CHOICE prompt card ─────────────── -->
          <template v-else>
            <div class="bg-[#A7FFEB]/30 border border-[#00A3C1]/20 rounded-[2rem] p-6 mb-4 text-center shadow-sm">
              <div class="flex justify-center mb-3 gap-2">
                <AudioPlayer v-if="lesson.currentQuestion.audio_url" :src="lesson.currentQuestion.audio_url" label="Hear Pronunciation" />
                <button
                  v-else-if="lesson.currentQuestion.type === 'translate'"
                  :disabled="ttsLoading"
                  class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-sm font-semibold bg-white border border-[#00A3C1]/30 text-[#003B5C] hover:bg-[#A7FFEB]/30 transition-all disabled:opacity-50"
                  @click="fetchTTS(lesson.currentQuestion.prompt)"
                >
                  <span class="material-icons-outlined text-base">{{ ttsLoading ? 'hourglass_empty' : 'volume_up' }}</span>
                  {{ ttsLoading ? 'Loading…' : 'Hear pronunciation' }}
                </button>
              </div>
              <AudioPlayer v-if="ttsAudioUrl && !lesson.currentQuestion.audio_url" :src="ttsAudioUrl" :autoplay="true" label="Pronunciation" />
              <p class="text-2xl font-bold text-[#003B5C] leading-relaxed">{{ lesson.currentQuestion.prompt }}</p>
              <p v-if="lesson.currentQuestion.native_text" class="text-slate-400 text-sm mt-2 italic">
                {{ lesson.currentQuestion.native_text }}
              </p>
            </div>
          </template>

          <!-- ── ANSWER INPUT (shared) ───────────────────────────────── -->
          <template v-if="!['image_match'].includes(lesson.currentQuestion.type)">
            <!-- Typed answer -->
            <div v-if="lesson.currentQuestion.type === 'translate'" class="space-y-2">
              <label :for="typedInputId" class="text-xs font-bold text-slate-400 uppercase tracking-wider">Type your answer</label>
              <input
                :id="typedInputId"
                :value="lesson.typedFor(lesson.currentQuestion.id)"
                class="w-full border-2 border-slate-200 rounded-2xl px-4 py-3 text-base font-semibold focus:outline-none focus:border-[#00A3C1] transition-colors"
                placeholder="Type the translation…"
                autocomplete="off"
                autocorrect="off"
                spellcheck="false"
                @input="lesson.setTypedAnswer($event.target.value)"
                @keydown.enter.prevent="goNext"
              />
              <SpecialCharKeyboard
                :language-code="lesson.languageCode"
                :model-value="lesson.typedFor(lesson.currentQuestion.id)"
                @update:model-value="lesson.setTypedAnswer($event)"
              />
            </div>

            <!-- Choice answers. Video options stay hidden until the gate is met. -->
            <div
              v-else-if="lesson.currentQuestion.options?.length && (lesson.currentQuestion.type !== 'video' || videoWatched)"
              class="space-y-3"
            >
              <button
                v-for="option in lesson.currentQuestion.options"
                :key="option.id"
                class="w-full p-4 rounded-2xl border-2 font-semibold text-left transition-all"
                :class="lesson.answerClass(lesson.currentQuestion, option.id)"
                @click="lesson.selectAnswer(option.id)"
              >
                {{ option.text }}
              </button>
            </div>
          </template>

          <button
            v-if="lesson.isAnswered(lesson.currentQuestion.id)"
            class="mt-3 self-start text-xs font-bold text-slate-400 underline"
            @click="lesson.clearAnswer(lesson.currentQuestion.id)"
          >
            Clear my answer
          </button>
        </main>

        <!-- ── BACK / NEXT ─────────────────────────────────────────────── -->
        <footer class="px-6 pb-8 pt-3 safe-bottom flex gap-3">
          <button
            :disabled="lesson.currentIndex === 0"
            class="rounded-3xl bg-slate-100 px-6 py-4 font-bold text-slate-700 transition-transform active:scale-95 disabled:opacity-40"
            @click="lesson.previous()"
          >
            <span class="material-icons-outlined align-middle text-lg">chevron_left</span>
            Back
          </button>
          <button
            :disabled="nextDisabled"
            class="flex-1 rounded-3xl py-4 text-lg font-bold transition-all"
            :class="nextDisabled
              ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
              : 'bg-[#003B5C] text-white shadow-lg shadow-[#003B5C]/20 active:scale-95'"
            @click="goNext"
          >
            {{ nextLabel }}
          </button>
        </footer>
      </template>

    </div>
  </section>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, reactive } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { useLesson } from '@/composables/useLesson'
import { useAuthStore } from '@/stores/auth'
import { ttsApi } from '@/api'
import AudioPlayer from '@/components/AudioPlayer.vue'
import VideoPlayer from '@/components/VideoPlayer.vue'
import SpecialCharKeyboard from '@/components/SpecialCharKeyboard.vue'
import ProgressDots from '@/components/ProgressDots.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

// reactive() wraps the composable so nested refs are auto-unwrapped in the template
const lesson = reactive(useLesson(route.params.id, auth.user?.id))

const typedInputId = 'lesson-typed-answer'

// TTS state
const ttsAudioUrl = ref(null)
const ttsLoading = ref(false)

// Video gate, tracked per question so going back doesn't re-lock a watched one.
const watchedVideos = ref(new Set())
const videoWatched = computed(() =>
  lesson.currentQuestion ? watchedVideos.value.has(lesson.currentQuestion.id) : false
)
function markVideoWatched(questionId) {
  watchedVideos.value = new Set(watchedVideos.value).add(questionId)
}

// Badge celebration state
const badgeIndex = ref(0)
const badgesDismissed = ref(false)
const showBadgeCelebration = computed(() =>
  !badgesDismissed.value && lesson.completionBadges.length > 0
)
function nextBadge() {
  if (badgeIndex.value < lesson.completionBadges.length - 1) badgeIndex.value++
  else badgesDismissed.value = true
}

// XP count-up on the results screen
const animatedXP = ref(0)
watch(() => lesson.finished, (isFinished) => {
  if (!isFinished) return
  const target = lesson.completionXp
  if (!target) return
  let current = 0
  const step = Math.max(1, Math.ceil(target / 30))
  const interval = setInterval(() => {
    current = Math.min(current + step, target)
    animatedXP.value = current
    if (current >= target) clearInterval(interval)
  }, 30)
})

watch(() => lesson.currentIndex, () => { ttsAudioUrl.value = null })

async function fetchTTS(text) {
  if (!text || ttsLoading.value) return
  ttsLoading.value = true
  try {
    const { data } = await ttsApi.generate(text, lesson.languageCode || 'yo')
    ttsAudioUrl.value = data.audio_url
  } catch { /* silent — TTS is optional */ } finally {
    ttsLoading.value = false
  }
}

const showCulturalNote = computed(() => lesson.pendingCulturalNote && !lesson.finished)

const TYPE_LABELS = {
  listen: 'Listen & choose',
  listen_comprehension: 'Listen & understand',
  image: 'What does this show?',
  image_translate: 'Name what you see',
  image_match: 'Match the image',
  multiple_choice: 'Choose the correct answer',
  video: 'Watch & learn',
}
function questionTypeLabel(question) {
  return TYPE_LABELS[question?.type] ?? 'Translate this phrase'
}

/** What the learner answered, as text — used in review and results. */
function displayAnswer(question) {
  const answer = lesson.answerFor(question.id)
  if (!answer) return ''
  if (answer.answer_text) return answer.answer_text
  return lesson.optionText(question, answer.answer_id)
}

// The video gate is the only hard block; everything else may be skipped.
const nextDisabled = computed(() =>
  lesson.currentQuestion?.type === 'video' && !videoWatched.value
)
const nextLabel = computed(() => {
  if (lesson.isLastQuestion) return 'Review answers'
  return lesson.isAnswered(lesson.currentQuestion?.id) ? 'Next' : 'Skip'
})
function goNext() {
  if (nextDisabled.value) return
  lesson.next()
}

// ── Leaving the lesson ───────────────────────────────────────────────────────
// Always the language's course page, never the dashboard landing screen.
const courseRoute = computed(() =>
  lesson.languageId
    ? { name: 'language-course', params: { languageId: lesson.languageId } }
    : { name: 'dashboard' }
)

function leaveLesson() {
  // replace() so a lesson the learner has left cannot be re-entered by
  // pressing forward/back repeatedly.
  router.replace(courseRoute.value)
}

function goToNextLesson() {
  if (lesson.nextLessonId) {
    router.replace({ name: 'lesson', params: { id: lesson.nextLessonId } })
    return
  }
  // Course finished (or the next lesson is unknown): back to the language page.
  router.replace({ ...courseRoute.value, query: { completed: '1' } })
}

// The browser/phone back button inside a lesson must land on the course page
// too, rather than bouncing through the dashboard. Progress is saved, so
// leaving needs no confirmation; only audio mid-playback is worth pausing.
onBeforeRouteLeave((to) => {
  if (to.name === 'dashboard' && lesson.languageId) return courseRoute.value
  document.querySelectorAll('audio, video').forEach(el => el.pause())
  return true
})

// ── Desktop keyboard navigation ──────────────────────────────────────────────
function handleKey(event) {
  if (lesson.finished || showCulturalNote.value || lesson.loading) return
  if (['INPUT', 'TEXTAREA'].includes(event.target?.tagName)) return

  if (event.key === 'ArrowLeft') { event.preventDefault(); lesson.previous(); return }
  if (event.key === 'ArrowRight') { event.preventDefault(); goNext(); return }

  const question = lesson.currentQuestion
  if (!question || lesson.reviewing) return
  const index = Number(event.key)
  if (Number.isInteger(index) && index >= 1 && index <= 9) {
    const option = question.options?.[index - 1]
    if (option) lesson.selectAnswer(option.id)
  }
}

onMounted(() => { lesson.load(); window.addEventListener('keydown', handleKey) })
onUnmounted(() => window.removeEventListener('keydown', handleKey))
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

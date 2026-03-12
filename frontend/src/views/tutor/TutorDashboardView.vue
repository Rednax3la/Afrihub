<template>
  <div class="p-6 lg:p-8 max-w-4xl mx-auto">
    <!-- Welcome -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-slate-900">Welcome back, {{ firstName }} 👋</h1>
      <p class="text-slate-500 text-sm mt-0.5">Here's an overview of your content on Vernaculearn.</p>
    </div>

    <!-- Pending notice -->
    <div v-if="auth.user?.tutor_status === 'pending'"
      class="bg-amber-50 border border-amber-200 rounded-3xl p-6 mb-6 flex items-start gap-4"
    >
      <span class="material-icons-outlined text-amber-500 text-2xl mt-0.5">hourglass_top</span>
      <div>
        <p class="font-bold text-amber-900">Application Under Review</p>
        <p class="text-amber-700 text-sm mt-1 leading-relaxed">
          Your tutor account is pending admin approval. Once approved, you'll be able to create and upload lessons for learners on the platform.
        </p>
      </div>
    </div>

    <!-- Stats row -->
    <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
      <div class="bg-white rounded-3xl p-5 border border-slate-100 shadow-sm">
        <div class="w-10 h-10 bg-emerald-50 rounded-2xl flex items-center justify-center mb-3">
          <span class="material-icons-outlined text-emerald-600">book</span>
        </div>
        <p class="text-3xl font-bold text-slate-900">{{ tutorStore.units.length }}</p>
        <p class="text-sm text-slate-500 font-medium mt-0.5">Units Created</p>
      </div>
      <div class="bg-white rounded-3xl p-5 border border-slate-100 shadow-sm">
        <div class="w-10 h-10 bg-blue-50 rounded-2xl flex items-center justify-center mb-3">
          <span class="material-icons-outlined text-blue-600">quiz</span>
        </div>
        <p class="text-3xl font-bold text-slate-900">{{ tutorStore.lessons.length }}</p>
        <p class="text-sm text-slate-500 font-medium mt-0.5">Lessons Published</p>
      </div>
      <div class="bg-white rounded-3xl p-5 border border-slate-100 shadow-sm">
        <div class="w-10 h-10 bg-purple-50 rounded-2xl flex items-center justify-center mb-3">
          <span class="material-icons-outlined text-purple-600">quiz</span>
        </div>
        <p class="text-3xl font-bold text-slate-900">{{ totalQuestions }}</p>
        <p class="text-sm text-slate-500 font-medium mt-0.5">Total Questions</p>
      </div>
    </div>

    <!-- Voice character card -->
    <div v-if="auth.user?.voice_character" class="bg-emerald-900 rounded-3xl p-6 mb-6 text-white flex items-center gap-5">
      <div class="w-16 h-16 bg-emerald-800 rounded-2xl flex items-center justify-center shrink-0">
        <span class="material-icons-outlined text-3xl text-emerald-300">record_voice_over</span>
      </div>
      <div>
        <p class="text-xs font-bold tracking-wider text-emerald-400 uppercase mb-0.5">Voice Character</p>
        <p class="text-xl font-bold">{{ auth.user.voice_character }}</p>
        <p class="text-emerald-300 text-sm mt-0.5">Your lessons are attributed to this character in the app.</p>
      </div>
    </div>

    <!-- Languages taught -->
    <div v-if="auth.user?.languages_taught?.length" class="bg-white rounded-3xl border border-slate-100 shadow-sm p-6 mb-6">
      <h2 class="font-bold text-slate-900 mb-4">Languages You Teach</h2>
      <div class="flex gap-2 flex-wrap">
        <span
          v-for="lang in auth.user.languages_taught"
          :key="lang"
          class="px-4 py-2 bg-emerald-50 text-emerald-800 rounded-2xl text-sm font-bold capitalize"
        >
          {{ lang }}
        </span>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="bg-white rounded-3xl border border-slate-100 shadow-sm p-6">
      <h2 class="font-bold text-slate-900 mb-4">Quick Actions</h2>
      <div class="grid grid-cols-2 gap-3">
        <RouterLink to="/tutor/content"
          class="flex items-center gap-3 p-4 rounded-2xl border-2 border-dashed border-slate-200 hover:border-emerald-300 hover:bg-emerald-50 transition-all group">
          <span class="material-icons-outlined text-2xl text-slate-400 group-hover:text-emerald-700">add_circle</span>
          <span class="text-sm font-semibold text-slate-600 group-hover:text-emerald-700">Add New Lesson</span>
        </RouterLink>
        <RouterLink to="/tutor/profile"
          class="flex items-center gap-3 p-4 rounded-2xl border-2 border-dashed border-slate-200 hover:border-emerald-300 hover:bg-emerald-50 transition-all group">
          <span class="material-icons-outlined text-2xl text-slate-400 group-hover:text-emerald-700">edit</span>
          <span class="text-sm font-semibold text-slate-600 group-hover:text-emerald-700">Edit Profile</span>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useTutorStore } from '@/stores/tutor'

const auth = useAuthStore()
const tutorStore = useTutorStore()

const firstName = computed(() => auth.user?.name?.split(' ')[0] || 'Tutor')
const totalQuestions = computed(() =>
  tutorStore.lessons.reduce((sum, l) => sum + (l.questions?.length || 0), 0)
)

onMounted(() => {
  if (auth.user?.tutor_status === 'active') tutorStore.fetchContent()
})
</script>

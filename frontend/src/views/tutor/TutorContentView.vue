<template>
  <div class="p-6 lg:p-8 max-w-5xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">My Content</h1>
        <p class="text-slate-500 text-sm mt-0.5">Manage the units and lessons you've created</p>
      </div>
      <div class="flex gap-2">
        <button @click="openUnitModal()" class="flex items-center gap-1.5 px-4 py-2.5 rounded-2xl border border-slate-200 bg-white text-slate-700 text-sm font-semibold hover:bg-slate-50">
          <span class="material-icons-outlined text-lg">create_new_folder</span> New Unit
        </button>
        <button @click="openLessonModal()" class="flex items-center gap-1.5 px-4 py-2.5 rounded-2xl bg-emerald-900 text-white text-sm font-bold hover:bg-emerald-800">
          <span class="material-icons-outlined text-lg">add</span> New Lesson
        </button>
      </div>
    </div>

    <div v-if="tutorStore.loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-4 border-emerald-100 border-t-emerald-600 rounded-full animate-spin"></div>
    </div>

    <template v-else>
      <!-- Units -->
      <div v-if="tutorStore.units.length" class="mb-8">
        <h2 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Units ({{ tutorStore.units.length }})</h2>
        <div class="space-y-2">
          <div v-for="unit in tutorStore.units" :key="unit.id"
            class="bg-white rounded-2xl border border-slate-100 p-4 flex items-center gap-4 shadow-sm"
          >
            <div class="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center shrink-0">
              <span class="material-icons-outlined text-emerald-700 text-lg">{{ unit.icon || 'book' }}</span>
            </div>
            <div class="flex-1">
              <p class="font-semibold text-slate-900">{{ unit.title }}</p>
              <p class="text-xs text-slate-400">{{ unit.subtitle }} · <span class="capitalize">{{ unit.language_id }}</span></p>
            </div>
            <span class="text-xs text-slate-400">Order {{ unit.order }}</span>
            <button @click="openUnitModal(unit)" class="p-2 rounded-xl text-slate-400 hover:text-emerald-700 hover:bg-emerald-50 transition-colors">
              <span class="material-icons-outlined text-base">edit</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Lessons -->
      <div>
        <h2 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Lessons ({{ tutorStore.lessons.length }})</h2>
        <div v-if="!tutorStore.lessons.length" class="bg-white rounded-3xl border border-dashed border-slate-200 p-12 text-center">
          <span class="material-icons-outlined text-4xl text-slate-300 mb-3 block">quiz</span>
          <p class="text-slate-400 font-medium mb-4">No lessons yet</p>
          <button @click="openLessonModal()" class="px-5 py-2.5 rounded-2xl bg-emerald-900 text-white text-sm font-bold">
            Create your first lesson
          </button>
        </div>
        <div v-else class="space-y-2">
          <div v-for="lesson in tutorStore.lessons" :key="lesson.id"
            class="bg-white rounded-2xl border border-slate-100 p-4 flex items-center gap-4 shadow-sm"
          >
            <div class="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center shrink-0">
              <span class="material-icons-outlined text-blue-600 text-lg">quiz</span>
            </div>
            <div class="flex-1">
              <p class="font-semibold text-slate-900">{{ lesson.title }}</p>
              <p class="text-xs text-slate-400">{{ lesson.questions?.length || 0 }} questions · Unit: {{ lesson.unit_id }}</p>
            </div>
            <span class="text-xs bg-emerald-50 text-emerald-700 font-bold px-2 py-0.5 rounded-full">+{{ lesson.xp_reward }} XP</span>
            <div class="flex gap-1">
              <button @click="openLessonModal(lesson)" class="p-2 rounded-xl text-slate-400 hover:text-emerald-700 hover:bg-emerald-50 transition-colors">
                <span class="material-icons-outlined text-base">edit</span>
              </button>
              <button @click="deleteLessonConfirm(lesson)" class="p-2 rounded-xl text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors">
                <span class="material-icons-outlined text-base">delete</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Unit modal -->
    <Modal v-model="showUnitModal" :title="editingUnit?.id ? 'Edit Unit' : 'New Unit'" size="md">
      <form @submit.prevent="saveUnit" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">ID (slug)</label>
            <input v-model="unitForm.id" :disabled="!!editingUnit?.id" required class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400 disabled:bg-slate-50" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Language</label>
            <select v-model="unitForm.language_id" required class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400">
              <option v-for="lang in auth.user?.languages_taught" :key="lang" :value="lang" class="capitalize">{{ lang }}</option>
            </select>
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Title</label>
            <input v-model="unitForm.title" required class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Subtitle</label>
            <input v-model="unitForm.subtitle" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Icon</label>
            <input v-model="unitForm.icon" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400" placeholder="waving_hand" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Order</label>
            <input v-model.number="unitForm.order" type="number" min="1" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400" />
          </div>
        </div>
        <div class="flex gap-3 pt-2">
          <button type="button" @click="showUnitModal = false" class="flex-1 py-3 rounded-2xl bg-slate-100 text-slate-700 font-semibold">Cancel</button>
          <button type="submit" :disabled="saving" class="flex-1 py-3 rounded-2xl bg-emerald-900 text-white font-bold disabled:opacity-50">
            {{ saving ? 'Saving…' : 'Save Unit' }}
          </button>
        </div>
      </form>
    </Modal>

    <!-- Lesson modal -->
    <Modal v-model="showLessonModal" :title="editingLesson?.id ? 'Edit Lesson' : 'New Lesson'" size="lg">
      <form @submit.prevent="saveLesson" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">ID (slug)</label>
            <input v-model="lessonForm.id" :disabled="!!editingLesson?.id" required class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400 disabled:bg-slate-50" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Unit</label>
            <select v-model="lessonForm.unit_id" required class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400">
              <option v-for="u in tutorStore.units" :key="u.id" :value="u.id">{{ u.title }}</option>
            </select>
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Title</label>
            <input v-model="lessonForm.title" required class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Description</label>
            <input v-model="lessonForm.description" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Order</label>
            <input v-model.number="lessonForm.order" type="number" min="1" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">XP Reward</label>
            <input v-model.number="lessonForm.xp_reward" type="number" min="1" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400" />
          </div>
        </div>

        <!-- Questions -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <label class="text-xs font-bold text-slate-500 uppercase">Questions ({{ lessonForm.questions.length }})</label>
            <button type="button" @click="addQuestion" class="text-xs font-bold text-emerald-700 flex items-center gap-1">
              <span class="material-icons-outlined text-sm">add</span> Add Question
            </button>
          </div>
          <div class="space-y-3 max-h-72 overflow-y-auto pr-1">
            <div v-for="(q, qi) in lessonForm.questions" :key="qi" class="bg-slate-50 rounded-2xl p-4 border border-slate-200">
              <div class="flex items-center justify-between mb-3">
                <span class="text-xs font-bold text-slate-400">Q{{ qi + 1 }}</span>
                <button type="button" @click="lessonForm.questions.splice(qi, 1)" class="text-red-400 hover:text-red-600">
                  <span class="material-icons-outlined text-sm">close</span>
                </button>
              </div>
              <div class="space-y-2">
                <select v-model="q.type" class="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none">
                  <option value="translate">Translate</option>
                  <option value="multiple_choice">Multiple Choice</option>
                  <option value="listen">Listen &amp; Choose</option>
                  <option value="image">Image Question</option>
                </select>
                <input v-model="q.prompt" placeholder="Question prompt" class="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none" />
                <input v-model="q.native_text" placeholder="Native text hint (optional)" class="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none" />
                <div v-if="q.type === 'listen' || q.type === 'translate'">
                  <p class="text-[10px] font-bold text-slate-400 uppercase mb-1">{{ q.type === 'listen' ? 'Audio (required)' : 'Pronunciation Audio (optional)' }}</p>
                  <FileUpload v-model="q.audio_url" type="audio" />
                </div>
                <div v-if="q.type === 'image'">
                  <p class="text-[10px] font-bold text-slate-400 uppercase mb-1">Image (required)</p>
                  <FileUpload v-model="q.image_url" type="image" />
                </div>
                <div class="space-y-1.5">
                  <div v-for="(opt, oi) in q.options" :key="oi" class="flex gap-2 items-center">
                    <input v-model="opt.id" class="w-8 border border-slate-200 rounded-lg px-2 py-1.5 text-xs text-center font-bold focus:outline-none" />
                    <input v-model="opt.text" class="flex-1 border border-slate-200 rounded-xl px-3 py-1.5 text-xs focus:outline-none" placeholder="Answer text" />
                    <button type="button" @click="q.options.splice(oi, 1)" class="text-red-300 hover:text-red-500">
                      <span class="material-icons-outlined text-sm">remove</span>
                    </button>
                  </div>
                  <button type="button" @click="q.options.push({ id: String.fromCharCode(97 + q.options.length), text: '' })" class="text-xs text-emerald-700 font-semibold flex items-center gap-1">
                    <span class="material-icons-outlined text-sm">add</span> Add option
                  </button>
                </div>
                <div class="flex items-center gap-2">
                  <label class="text-xs text-slate-400">Correct answer ID:</label>
                  <input v-model="q.correct_answer_id" class="w-12 border border-slate-200 rounded-lg px-2 py-1 text-xs text-center font-bold focus:outline-none" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex gap-3 pt-2">
          <button type="button" @click="showLessonModal = false" class="flex-1 py-3 rounded-2xl bg-slate-100 text-slate-700 font-semibold">Cancel</button>
          <button type="submit" :disabled="saving" class="flex-1 py-3 rounded-2xl bg-emerald-900 text-white font-bold disabled:opacity-50">
            {{ saving ? 'Saving…' : 'Save Lesson' }}
          </button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useTutorStore } from '@/stores/tutor'
import { useToastStore } from '@/stores/toast'
import Modal from '@/components/Modal.vue'
import FileUpload from '@/components/FileUpload.vue'

const auth = useAuthStore()
const tutorStore = useTutorStore()
const toast = useToastStore()
const saving = ref(false)

const showUnitModal = ref(false)
const editingUnit = ref(null)
const unitForm = ref({})

const showLessonModal = ref(false)
const editingLesson = ref(null)
const lessonForm = ref({ questions: [] })

onMounted(() => tutorStore.fetchContent())

function openUnitModal(unit = null) {
  editingUnit.value = unit
  unitForm.value = unit ? { ...unit } : {
    id: '', language_id: auth.user?.languages_taught?.[0] || '', title: '', subtitle: '', icon: 'waving_hand', order: 1
  }
  showUnitModal.value = true
}

async function saveUnit() {
  saving.value = true
  try {
    if (editingUnit.value?.id) {
      await tutorStore.updateUnit(editingUnit.value.id, unitForm.value)
      toast.success('Unit updated')
    } else {
      await tutorStore.createUnit(unitForm.value)
      toast.success('Unit created')
    }
    showUnitModal.value = false
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Failed to save unit')
  } finally { saving.value = false }
}

function openLessonModal(lesson = null) {
  editingLesson.value = lesson
  lessonForm.value = lesson
    ? { ...lesson, questions: (lesson.questions || []).map(q => ({ ...q, options: [...(q.options || [])] })) }
    : { id: '', unit_id: '', title: '', description: '', order: 1, xp_reward: 15, questions: [] }
  showLessonModal.value = true
}

function addQuestion() {
  lessonForm.value.questions.push({
    id: `q${lessonForm.value.questions.length + 1}`,
    type: 'translate',
    prompt: '',
    native_text: null,
    options: [{ id: 'a', text: '' }, { id: 'b', text: '' }, { id: 'c', text: '' }],
    correct_answer_id: 'a',
  })
}

async function saveLesson() {
  saving.value = true
  try {
    if (editingLesson.value?.id) {
      await tutorStore.updateLesson(editingLesson.value.id, lessonForm.value)
      toast.success('Lesson updated')
    } else {
      await tutorStore.createLesson(lessonForm.value)
      toast.success('Lesson created')
    }
    showLessonModal.value = false
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Failed to save lesson')
  } finally { saving.value = false }
}

async function deleteLessonConfirm(lesson) {
  if (!confirm(`Delete "${lesson.title}"?`)) return
  try {
    await tutorStore.deleteLesson(lesson.id)
    toast.success('Lesson deleted')
  } catch { toast.error('Failed to delete lesson') }
}
</script>

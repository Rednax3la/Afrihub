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
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-slate-900">{{ unit.title }}</p>
              <p class="text-xs text-slate-400">{{ unit.subtitle }} · <span class="capitalize">{{ unit.language_id }}</span></p>
            </div>
            <span class="text-xs text-slate-400 shrink-0">Order {{ unit.order }}</span>
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
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <p class="font-semibold text-slate-900">{{ lesson.title }}</p>
                <span class="text-[10px] font-bold px-1.5 py-0.5 rounded-full"
                  :class="lesson.status === 'published' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'">
                  {{ lesson.status || 'published' }}
                </span>
              </div>
              <p class="text-xs text-slate-400">{{ lesson.questions?.length || 0 }} questions · Unit: {{ lesson.unit_id }}</p>
            </div>
            <span class="text-xs bg-emerald-50 text-emerald-700 font-bold px-2 py-0.5 rounded-full shrink-0">+{{ lesson.xp_reward }} XP</span>
            <div class="flex gap-1 shrink-0">
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

    <!-- Lesson modal (Gap 1 + Gap 7 mobile fix) -->
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
          <!-- Status (Gap 1) -->
          <div class="col-span-2 flex items-center gap-3 py-1">
            <label class="text-xs font-bold text-slate-500 uppercase">Status</label>
            <button type="button"
              @click="lessonForm.status = lessonForm.status === 'published' ? 'draft' : 'published'"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-colors"
              :class="lessonForm.status === 'published' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'"
            >
              <span class="material-icons-outlined text-sm">{{ lessonForm.status === 'published' ? 'visibility' : 'visibility_off' }}</span>
              {{ lessonForm.status === 'published' ? 'Published' : 'Draft' }}
            </button>
          </div>
        </div>

        <!-- Intro Audio (Gap 1) -->
        <div>
          <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Intro Audio (optional)</label>
          <FileUpload v-model="lessonForm.audio_intro_url" type="audio" />
        </div>

        <!-- Cultural Note (Gap 1 + 2C) -->
        <div class="bg-amber-50 rounded-2xl p-4 border border-amber-100 space-y-3">
          <p class="text-xs font-bold text-amber-700 uppercase tracking-wider">Cultural Note (shown after lesson)</p>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1 uppercase">Title</label>
            <input v-model="lessonForm.cultural_note_title" placeholder="e.g. The Tonal Nature of Yoruba" class="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-amber-400 bg-white" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1 uppercase">Note Body</label>
            <textarea v-model="lessonForm.cultural_note" rows="3" placeholder="Brief cultural context shown to learners after completing this lesson…" class="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-amber-400 resize-none bg-white"></textarea>
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
                <!-- Question type dropdown with all 7 types -->
                <select v-model="q.type" class="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none">
                  <option value="translate">Translate</option>
                  <option value="multiple_choice">Multiple Choice</option>
                  <option value="listen">Listen &amp; Choose</option>
                  <option value="listen_comprehension">Listen Comprehension</option>
                  <option value="image">Image Question</option>
                  <option value="image_translate">Image → Translate</option>
                  <option value="image_match">Image Match</option>
                </select>
                <input v-model="q.prompt" placeholder="Question prompt" class="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none" />
                <SpecialCharKeyboard :language-code="lessonLanguageCode" :model-value="q.prompt" @update:model-value="q.prompt = $event" />
                <input v-model="q.native_text" placeholder="Native text hint (optional)" class="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none" />
                <!-- Audio upload for listen types -->
                <div v-if="q.type === 'listen' || q.type === 'listen_comprehension' || q.type === 'translate'">
                  <p class="text-[10px] font-bold text-slate-400 uppercase mb-1">
                    {{ q.type === 'translate' ? 'Pronunciation Audio (optional)' : 'Audio (required)' }}
                  </p>
                  <FileUpload v-model="q.audio_url" type="audio" />
                </div>
                <!-- Image upload for image types -->
                <div v-if="q.type === 'image' || q.type === 'image_translate'">
                  <p class="text-[10px] font-bold text-slate-400 uppercase mb-1">Image (required)</p>
                  <FileUpload v-model="q.image_url" type="image" />
                </div>
                <!-- image_match: options have image_url -->
                <div v-if="q.type === 'image_match'" class="text-[10px] text-amber-600 bg-amber-50 rounded-lg px-2 py-1.5">
                  For Image Match, set each option's image URL using the field below.
                </div>
                <!-- Options -->
                <div class="space-y-1.5">
                  <div v-for="(opt, oi) in q.options" :key="oi" class="flex gap-2 items-start">
                    <input v-model="opt.id" class="w-8 mt-1.5 border border-slate-200 rounded-lg px-2 py-1.5 text-xs text-center font-bold focus:outline-none" />
                    <div class="flex-1 space-y-1">
                      <template v-if="q.type !== 'image_match'">
                        <input v-model="opt.text" class="w-full border border-slate-200 rounded-xl px-3 py-1.5 text-xs focus:outline-none" placeholder="Answer text" />
                        <SpecialCharKeyboard :language-code="lessonLanguageCode" :model-value="opt.text" @update:model-value="opt.text = $event" />
                      </template>
                      <input v-if="q.type === 'image_match'" v-model="opt.image_url" class="w-full border border-slate-200 rounded-xl px-3 py-1.5 text-xs focus:outline-none" placeholder="Image URL for this option" />
                      <input v-if="q.type === 'image_match'" v-model="opt.text" class="w-full border border-slate-200 rounded-xl px-3 py-1.5 text-xs focus:outline-none" placeholder="Alt text (optional)" />
                    </div>
                    <button type="button" @click="q.options.splice(oi, 1)" class="text-red-300 hover:text-red-500 mt-1.5">
                      <span class="material-icons-outlined text-sm">remove</span>
                    </button>
                  </div>
                  <button type="button" @click="q.options.push({ id: String.fromCharCode(97 + q.options.length), text: '', image_url: '' })" class="text-xs text-emerald-700 font-semibold flex items-center gap-1">
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
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useTutorStore } from '@/stores/tutor'
import { useToastStore } from '@/stores/toast'
import Modal from '@/components/Modal.vue'
import FileUpload from '@/components/FileUpload.vue'
import SpecialCharKeyboard from '@/components/SpecialCharKeyboard.vue'

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

// Derive language code from the selected unit (for SpecialCharKeyboard)
const lessonLanguageCode = computed(() => {
  const unit = tutorStore.units.find(u => u.id === lessonForm.value.unit_id)
  return unit?.language_id || ''
})

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
    ? {
        ...lesson,
        questions: (lesson.questions || []).map(q => ({ ...q, options: [...(q.options || [])] })),
        status: lesson.status || 'published',
        audio_intro_url: lesson.audio_intro_url || '',
        cultural_note: lesson.cultural_note || '',
        cultural_note_title: lesson.cultural_note_title || '',
      }
    : {
        id: '', unit_id: '', title: '', description: '', order: 1, xp_reward: 15,
        questions: [], status: 'published', audio_intro_url: '', cultural_note: '', cultural_note_title: '',
      }
  showLessonModal.value = true
}

function addQuestion() {
  lessonForm.value.questions.push({
    id: `q${lessonForm.value.questions.length + 1}`,
    type: 'translate',
    prompt: '',
    native_text: null,
    options: [{ id: 'a', text: '', image_url: '' }, { id: 'b', text: '', image_url: '' }, { id: 'c', text: '', image_url: '' }],
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

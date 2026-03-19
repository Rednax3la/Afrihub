<template>
  <div class="p-6 lg:p-8 max-w-6xl mx-auto">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-slate-900">Content CMS</h1>
      <p class="text-slate-500 text-sm mt-0.5">Manage languages, units, and lessons</p>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 bg-slate-100 rounded-2xl p-1 w-fit mb-6">
      <button
        v-for="tab in ['Languages', 'Units', 'Lessons']"
        :key="tab"
        @click="activeTab = tab"
        class="px-5 py-2 rounded-xl text-sm font-semibold transition-all"
        :class="activeTab === tab ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
      >
        {{ tab }}
      </button>
    </div>

    <!-- ── LANGUAGES ─────────────────────────────────────────────────────────── -->
    <div v-if="activeTab === 'Languages'">
      <div class="flex justify-between items-center mb-4">
        <p class="text-sm text-slate-500">{{ adminStore.languages.length }} languages</p>
        <button @click="openLanguageModal()" class="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-emerald-900 text-white text-sm font-bold hover:bg-emerald-800">
          <span class="material-icons-outlined text-lg">add</span> Add Language
        </button>
      </div>
      <div class="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-slate-100">
              <th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase">Language</th>
              <th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase">Country</th>
              <th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase">Speakers</th>
              <th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase">Access</th>
              <th class="px-6 py-4"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="lang in adminStore.languages" :key="lang.id" class="border-b border-slate-50 hover:bg-slate-50">
              <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                  <span class="text-xl">{{ lang.flag_emoji }}</span>
                  <span class="font-semibold text-slate-900">{{ lang.name }}</span>
                </div>
              </td>
              <td class="px-6 py-4 text-slate-600">{{ lang.country }}</td>
              <td class="px-6 py-4 text-slate-600">{{ lang.speaker_count }}</td>
              <td class="px-6 py-4">
                <span class="text-xs font-bold px-2 py-0.5 rounded-full" :class="lang.is_free ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'">
                  {{ lang.is_free ? 'Free' : 'Premium' }}
                </span>
              </td>
              <td class="px-6 py-4">
                <div class="flex gap-1 justify-end">
                  <button @click="openLanguageModal(lang)" class="p-2 rounded-xl text-slate-400 hover:text-emerald-700 hover:bg-emerald-50 transition-colors">
                    <span class="material-icons-outlined text-base">edit</span>
                  </button>
                  <button @click="deleteLanguage(lang)" class="p-2 rounded-xl text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors">
                    <span class="material-icons-outlined text-base">delete</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── UNITS ─────────────────────────────────────────────────────────────── -->
    <div v-else-if="activeTab === 'Units'">
      <div class="flex gap-3 items-center mb-4">
        <select v-model="selectedLangFilter" @change="adminStore.fetchUnits(selectedLangFilter)" class="border border-slate-200 rounded-2xl px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-400">
          <option value="">All Languages</option>
          <option v-for="l in adminStore.languages" :key="l.id" :value="l.id">{{ l.name }}</option>
        </select>
        <button @click="openUnitModal()" class="ml-auto flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-emerald-900 text-white text-sm font-bold hover:bg-emerald-800">
          <span class="material-icons-outlined text-lg">add</span> Add Unit
        </button>
      </div>
      <div class="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-slate-100">
              <th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase">Unit</th>
              <th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase">Language</th>
              <th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase">Order</th>
              <th class="px-6 py-4"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="unit in adminStore.units" :key="unit.id" class="border-b border-slate-50 hover:bg-slate-50">
              <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                  <span class="material-icons-outlined text-slate-400 text-lg">{{ unit.icon || 'book' }}</span>
                  <div>
                    <p class="font-semibold text-slate-900">{{ unit.title }}</p>
                    <p class="text-xs text-slate-400">{{ unit.subtitle }}</p>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 text-slate-600 capitalize">{{ unit.language_id }}</td>
              <td class="px-6 py-4 text-slate-600">{{ unit.order }}</td>
              <td class="px-6 py-4">
                <div class="flex gap-1 justify-end">
                  <button @click="openUnitModal(unit)" class="p-2 rounded-xl text-slate-400 hover:text-emerald-700 hover:bg-emerald-50 transition-colors">
                    <span class="material-icons-outlined text-base">edit</span>
                  </button>
                  <button @click="deleteUnit(unit)" class="p-2 rounded-xl text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors">
                    <span class="material-icons-outlined text-base">delete</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── LESSONS ────────────────────────────────────────────────────────────── -->
    <div v-else-if="activeTab === 'Lessons'">
      <div class="flex gap-3 items-center mb-4">
        <select v-model="selectedUnitFilter" @change="adminStore.fetchLessons(selectedUnitFilter)" class="border border-slate-200 rounded-2xl px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-400">
          <option value="">All Units</option>
          <option v-for="u in adminStore.units" :key="u.id" :value="u.id">{{ u.title }}</option>
        </select>
        <button @click="openLessonModal()" class="ml-auto flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-emerald-900 text-white text-sm font-bold hover:bg-emerald-800">
          <span class="material-icons-outlined text-lg">add</span> Add Lesson
        </button>
      </div>
      <div class="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-slate-100">
              <th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase">Lesson</th>
              <th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase">Unit</th>
              <th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase">Questions</th>
              <th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase">XP</th>
              <th class="px-6 py-4"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="lesson in adminStore.lessons" :key="lesson.id" class="border-b border-slate-50 hover:bg-slate-50">
              <td class="px-6 py-4">
                <p class="font-semibold text-slate-900">{{ lesson.title }}</p>
                <p class="text-xs text-slate-400">{{ lesson.description }}</p>
              </td>
              <td class="px-6 py-4 text-slate-600">{{ lesson.unit_id }}</td>
              <td class="px-6 py-4">
                <span class="font-bold text-slate-700">{{ lesson.questions?.length ?? 0 }}</span>
              </td>
              <td class="px-6 py-4">
                <span class="text-xs bg-emerald-50 text-emerald-700 font-bold px-2 py-0.5 rounded-full">+{{ lesson.xp_reward }}</span>
              </td>
              <td class="px-6 py-4">
                <div class="flex gap-1 justify-end">
                  <button @click="openLessonModal(lesson)" class="p-2 rounded-xl text-slate-400 hover:text-emerald-700 hover:bg-emerald-50 transition-colors">
                    <span class="material-icons-outlined text-base">edit</span>
                  </button>
                  <button @click="deleteLesson(lesson)" class="p-2 rounded-xl text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors">
                    <span class="material-icons-outlined text-base">delete</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── LANGUAGE MODAL ──────────────────────────────────────────────────────── -->
    <Modal v-model="showLanguageModal" :title="editingLang?.id ? 'Edit Language' : 'Add Language'" size="md">
      <form @submit.prevent="saveLanguage" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">ID (slug)</label>
            <input v-model="langForm.id" :disabled="!!editingLang?.id" required class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400 disabled:bg-slate-50" placeholder="e.g. yoruba" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Name</label>
            <input v-model="langForm.name" required class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400" placeholder="Yoruba" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Flag Emoji</label>
            <input v-model="langForm.flag_emoji" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400" placeholder="🇳🇬" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Country</label>
            <input v-model="langForm.country" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400" placeholder="Nigeria" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Speakers</label>
            <input v-model="langForm.speaker_count" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400" placeholder="47 million" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Color</label>
            <select v-model="langForm.color" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400">
              <option value="emerald">Emerald</option>
              <option value="blue">Blue</option>
              <option value="amber">Amber</option>
              <option value="red">Red</option>
              <option value="purple">Purple</option>
            </select>
          </div>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Description</label>
          <textarea v-model="langForm.description" rows="2" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400 resize-none" placeholder="Short description of the language..."></textarea>
        </div>
        <div class="flex items-center gap-3">
          <input v-model="langForm.is_free" type="checkbox" id="is_free" class="w-4 h-4 text-emerald-600 rounded" />
          <label for="is_free" class="text-sm font-semibold text-slate-700">Free access (unchecked = Premium only)</label>
        </div>
        <div class="flex gap-3 pt-2">
          <button type="button" @click="showLanguageModal = false" class="flex-1 py-3 rounded-2xl bg-slate-100 text-slate-700 font-semibold">Cancel</button>
          <button type="submit" :disabled="saving" class="flex-1 py-3 rounded-2xl bg-emerald-900 text-white font-bold disabled:opacity-50">
            {{ saving ? 'Saving…' : 'Save Language' }}
          </button>
        </div>
      </form>
    </Modal>

    <!-- ── UNIT MODAL ──────────────────────────────────────────────────────────── -->
    <Modal v-model="showUnitModal" :title="editingUnit?.id ? 'Edit Unit' : 'Add Unit'" size="md">
      <form @submit.prevent="saveUnit" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">ID (slug)</label>
            <input v-model="unitForm.id" :disabled="!!editingUnit?.id" required class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400 disabled:bg-slate-50" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Language</label>
            <select v-model="unitForm.language_id" required class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400">
              <option v-for="l in adminStore.languages" :key="l.id" :value="l.id">{{ l.name }}</option>
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
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Icon (Material)</label>
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

    <!-- ── LESSON MODAL ────────────────────────────────────────────────────────── -->
    <Modal v-model="showLessonModal" :title="editingLesson?.id ? 'Edit Lesson' : 'Add Lesson'" size="lg">
      <form @submit.prevent="saveLesson" class="space-y-4 max-h-[75vh] overflow-y-auto pr-1">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">ID (slug)</label>
            <input v-model="lessonForm.id" :disabled="!!editingLesson?.id" required class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400 disabled:bg-slate-50" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Unit</label>
            <select v-model="lessonForm.unit_id" required class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400">
              <option v-for="u in adminStore.units" :key="u.id" :value="u.id">{{ u.title }}</option>
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

        <!-- Intro audio -->
        <div>
          <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Intro Audio (optional)</label>
          <FileUpload v-model="lessonForm.audio_intro_url" type="audio" />
        </div>

        <!-- Cultural note -->
        <div class="grid grid-cols-2 gap-4">
          <div class="col-span-2">
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Cultural Note Title</label>
            <input v-model="lessonForm.cultural_note_title" placeholder="e.g. The Tonal Nature of Yoruba" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Cultural Note (shown after lesson)</label>
            <textarea v-model="lessonForm.cultural_note" rows="2" placeholder="Brief cultural context shown to learners after completing this lesson…" class="w-full border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-400 resize-none"></textarea>
          </div>
        </div>

        <!-- Questions editor -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <label class="text-xs font-bold text-slate-500 uppercase">Questions ({{ lessonForm.questions.length }})</label>
            <button type="button" @click="addQuestion" class="text-xs font-bold text-emerald-700 hover:text-emerald-900 flex items-center gap-1">
              <span class="material-icons-outlined text-sm">add</span> Add Question
            </button>
          </div>
          <div class="space-y-3 max-h-80 overflow-y-auto pr-1">
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
                  <option value="listen_comprehension">Listen Comprehension</option>
                  <option value="image">Image Question</option>
                  <option value="image_translate">Image → Translate</option>
                  <option value="image_match">Image Match</option>
                </select>
                <input v-model="q.prompt" placeholder="Question / phrase to translate" class="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none" />
                <SpecialCharKeyboard :language-code="adminLessonLanguageCode" :model-value="q.prompt" @update:model-value="q.prompt = $event" />
                <input v-model="q.native_text" placeholder="Native text hint (optional)" class="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none" />
                <!-- Audio upload -->
                <div v-if="q.type === 'listen' || q.type === 'listen_comprehension' || q.type === 'translate'">
                  <p class="text-[10px] font-bold text-slate-400 uppercase mb-1">
                    {{ q.type === 'translate' ? 'Pronunciation Audio (optional)' : 'Audio (required)' }}
                  </p>
                  <FileUpload v-model="q.audio_url" type="audio" />
                </div>
                <!-- Image upload -->
                <div v-if="q.type === 'image' || q.type === 'image_translate'">
                  <p class="text-[10px] font-bold text-slate-400 uppercase mb-1">Image (required)</p>
                  <FileUpload v-model="q.image_url" type="image" />
                </div>
                <div class="space-y-1.5">
                  <div v-for="(opt, oi) in q.options" :key="oi" class="flex gap-2 items-start">
                    <input v-model="opt.id" class="w-8 mt-1.5 border border-slate-200 rounded-lg px-2 py-1.5 text-xs text-center font-bold focus:outline-none" placeholder="a" />
                    <div class="flex-1">
                      <input v-model="opt.text" class="w-full border border-slate-200 rounded-xl px-3 py-1.5 text-xs focus:outline-none" placeholder="Answer text" />
                      <SpecialCharKeyboard :language-code="adminLessonLanguageCode" :model-value="opt.text" @update:model-value="opt.text = $event" />
                    </div>
                    <button type="button" @click="q.options.splice(oi, 1)" class="text-red-300 hover:text-red-500 shrink-0 mt-1.5">
                      <span class="material-icons-outlined text-sm">remove</span>
                    </button>
                  </div>
                  <button type="button" @click="q.options.push({ id: String.fromCharCode(97 + q.options.length), text: '' })"
                    class="text-xs text-emerald-700 font-semibold flex items-center gap-1">
                    <span class="material-icons-outlined text-sm">add</span> Add option
                  </button>
                </div>
                <div>
                  <label class="text-xs text-slate-400">Correct answer ID:</label>
                  <input v-model="q.correct_answer_id" class="ml-2 w-12 border border-slate-200 rounded-lg px-2 py-1 text-xs text-center font-bold focus:outline-none" placeholder="a" />
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
import { useAdminStore } from '@/stores/admin'
import { useToastStore } from '@/stores/toast'
import Modal from '@/components/Modal.vue'
import FileUpload from '@/components/FileUpload.vue'
import SpecialCharKeyboard from '@/components/SpecialCharKeyboard.vue'

const adminStore = useAdminStore()
const toast = useToastStore()
const activeTab = ref('Languages')

// Resolve lesson's language → ISO code for SpecialCharKeyboard
const adminLessonLanguageCode = computed(() => {
  const unit = adminStore.units.find(u => u.id === lessonForm.value.unit_id)
  if (!unit) return ''
  const lang = adminStore.languages.find(l => l.id === unit.language_id)
  return lang?.code ?? ''
})
const selectedLangFilter = ref('')
const selectedUnitFilter = ref('')
const saving = ref(false)

// Language modal
const showLanguageModal = ref(false)
const editingLang = ref(null)
const langForm = ref({})

// Unit modal
const showUnitModal = ref(false)
const editingUnit = ref(null)
const unitForm = ref({})

// Lesson modal
const showLessonModal = ref(false)
const editingLesson = ref(null)
const lessonForm = ref({ questions: [] })

onMounted(async () => {
  await adminStore.fetchLanguages()
  await adminStore.fetchUnits()
  await adminStore.fetchLessons()
})

// Language
function openLanguageModal(lang = null) {
  editingLang.value = lang
  langForm.value = lang ? { ...lang } : { id: '', name: '', flag_emoji: '', country: '', speaker_count: '', color: 'emerald', description: '', is_free: true }
  showLanguageModal.value = true
}
async function saveLanguage() {
  saving.value = true
  try {
    if (editingLang.value?.id) {
      await adminStore.updateLanguage(editingLang.value.id, langForm.value)
      toast.success('Language updated')
    } else {
      await adminStore.createLanguage(langForm.value)
      toast.success('Language created')
    }
    showLanguageModal.value = false
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Failed to save language')
  } finally { saving.value = false }
}
async function deleteLanguage(lang) {
  if (!confirm(`Delete "${lang.name}"? This cannot be undone.`)) return
  try {
    await adminStore.deleteLanguage(lang.id)
    toast.success('Language deleted')
  } catch { toast.error('Failed to delete') }
}

// Unit
function openUnitModal(unit = null) {
  editingUnit.value = unit
  unitForm.value = unit ? { ...unit } : { id: '', language_id: '', title: '', subtitle: '', icon: 'waving_hand', order: 1 }
  showUnitModal.value = true
}
async function saveUnit() {
  saving.value = true
  try {
    if (editingUnit.value?.id) {
      await adminStore.updateUnit(editingUnit.value.id, unitForm.value)
      toast.success('Unit updated')
    } else {
      await adminStore.createUnit(unitForm.value)
      toast.success('Unit created')
    }
    showUnitModal.value = false
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Failed to save unit')
  } finally { saving.value = false }
}
async function deleteUnit(unit) {
  if (!confirm(`Delete unit "${unit.title}"?`)) return
  try {
    await adminStore.deleteUnit(unit.id)
    toast.success('Unit deleted')
  } catch { toast.error('Failed to delete') }
}

// Lesson
function openLessonModal(lesson = null) {
  editingLesson.value = lesson
  lessonForm.value = lesson
    ? { ...lesson, questions: lesson.questions ? lesson.questions.map(q => ({ ...q, options: [...(q.options || [])] })) : [] }
    : { id: '', unit_id: '', language_id: '', title: '', description: '', order: 1, xp_reward: 15, questions: [], status: 'published', audio_intro_url: '', cultural_note: '', cultural_note_title: '' }
  showLessonModal.value = true
}
function addQuestion() {
  lessonForm.value.questions.push({
    id: `q${lessonForm.value.questions.length + 1}`,
    type: 'translate',
    prompt: '',
    native_text: null,
    options: [
      { id: 'a', text: '' },
      { id: 'b', text: '' },
      { id: 'c', text: '' },
    ],
    correct_answer_id: 'a',
  })
}
async function saveLesson() {
  saving.value = true
  try {
    if (editingLesson.value?.id) {
      await adminStore.updateLesson(editingLesson.value.id, lessonForm.value)
      toast.success('Lesson updated')
    } else {
      await adminStore.createLesson(lessonForm.value)
      toast.success('Lesson created')
    }
    showLessonModal.value = false
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Failed to save lesson')
  } finally { saving.value = false }
}
async function deleteLesson(lesson) {
  if (!confirm(`Delete lesson "${lesson.title}"?`)) return
  try {
    await adminStore.deleteLesson(lesson.id)
    toast.success('Lesson deleted')
  } catch { toast.error('Failed to delete') }
}
</script>

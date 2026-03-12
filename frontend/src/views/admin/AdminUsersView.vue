<template>
  <div class="p-6 lg:p-8 max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Users</h1>
        <p class="text-slate-500 text-sm mt-0.5">{{ adminStore.users.length }} registered students</p>
      </div>
      <div class="relative">
        <span class="material-icons-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-lg">search</span>
        <input v-model="search" placeholder="Search users..." class="pl-9 pr-4 py-2.5 border border-slate-200 rounded-2xl text-sm focus:outline-none focus:border-emerald-400 w-56" />
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
      <div v-if="adminStore.loading" class="flex justify-center py-16">
        <div class="w-8 h-8 border-4 border-emerald-100 border-t-emerald-600 rounded-full animate-spin"></div>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-slate-100">
              <th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">User</th>
              <th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Location</th>
              <th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">XP</th>
              <th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Premium</th>
              <th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Joined</th>
              <th class="px-6 py-4"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in filteredUsers"
              :key="user.id"
              class="border-b border-slate-50 hover:bg-slate-50 transition-colors"
            >
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <img
                    :src="user.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=065F46&color=fff&rounded=true&size=64`"
                    class="w-9 h-9 rounded-full object-cover border border-slate-100"
                  />
                  <div>
                    <p class="font-semibold text-slate-900">{{ user.name }}</p>
                    <p class="text-xs text-slate-400">{{ user.email }}</p>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 text-slate-600">{{ user.location || '—' }}</td>
              <td class="px-6 py-4">
                <span class="font-bold text-emerald-700">{{ user.xp }}</span>
              </td>
              <td class="px-6 py-4">
                <button
                  @click="togglePremium(user)"
                  class="px-3 py-1 rounded-full text-xs font-bold transition-colors"
                  :class="user.is_premium
                    ? 'bg-amber-100 text-amber-700 hover:bg-amber-200'
                    : 'bg-slate-100 text-slate-500 hover:bg-slate-200'"
                >
                  {{ user.is_premium ? 'Premium' : 'Free' }}
                </button>
              </td>
              <td class="px-6 py-4 text-slate-400 text-xs">{{ formatDate(user.created_at) }}</td>
              <td class="px-6 py-4">
                <button
                  @click="confirmDelete(user)"
                  class="p-2 rounded-xl text-slate-300 hover:text-red-500 hover:bg-red-50 transition-colors"
                >
                  <span class="material-icons-outlined text-base">delete</span>
                </button>
              </td>
            </tr>
            <tr v-if="!filteredUsers.length">
              <td colspan="6" class="px-6 py-12 text-center text-slate-400">No users found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Delete confirm modal -->
    <Modal v-model="showDeleteModal" title="Delete User" size="sm">
      <p class="text-slate-600 mb-6">Are you sure you want to delete <strong>{{ selectedUser?.name }}</strong>? This cannot be undone.</p>
      <div class="flex gap-3">
        <button @click="showDeleteModal = false" class="flex-1 py-3 rounded-2xl bg-slate-100 text-slate-700 font-semibold">Cancel</button>
        <button @click="executeDelete" :disabled="deleting" class="flex-1 py-3 rounded-2xl bg-red-600 text-white font-semibold disabled:opacity-50">
          {{ deleting ? 'Deleting…' : 'Delete' }}
        </button>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { useToastStore } from '@/stores/toast'
import Modal from '@/components/Modal.vue'

const adminStore = useAdminStore()
const toast = useToastStore()
const search = ref('')
const showDeleteModal = ref(false)
const selectedUser = ref(null)
const deleting = ref(false)

onMounted(() => adminStore.fetchUsers())

const filteredUsers = computed(() =>
  adminStore.users.filter(u =>
    u.name.toLowerCase().includes(search.value.toLowerCase()) ||
    u.email.toLowerCase().includes(search.value.toLowerCase())
  )
)

async function togglePremium(user) {
  try {
    await adminStore.updateUser(user.id, { is_premium: !user.is_premium })
    toast.success(`${user.name} is now ${!user.is_premium ? 'Premium' : 'Free'}`)
  } catch {
    toast.error('Failed to update user')
  }
}

function confirmDelete(user) {
  selectedUser.value = user
  showDeleteModal.value = true
}

async function executeDelete() {
  deleting.value = true
  try {
    await adminStore.deleteUser(selectedUser.value.id)
    toast.success('User deleted')
    showDeleteModal.value = false
  } catch {
    toast.error('Failed to delete user')
  } finally {
    deleting.value = false
  }
}

function formatDate(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>

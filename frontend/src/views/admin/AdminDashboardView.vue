<template>
  <div class="p-6 lg:p-8 max-w-6xl mx-auto">
    <!-- Page header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-slate-900">Dashboard</h1>
      <p class="text-slate-500 text-sm mt-1">Platform overview at a glance</p>
    </div>

    <!-- Stats grid -->
    <div class="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
      <div v-for="stat in statCards" :key="stat.label"
        class="bg-white rounded-3xl p-5 border border-slate-100 shadow-sm"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="w-10 h-10 rounded-2xl flex items-center justify-center" :class="stat.bgClass">
            <span class="material-icons-outlined text-xl" :class="stat.iconClass">{{ stat.icon }}</span>
          </div>
          <span v-if="stat.badge" class="text-xs font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">
            {{ stat.badge }}
          </span>
        </div>
        <p class="text-3xl font-bold text-slate-900">{{ stat.value ?? '—' }}</p>
        <p class="text-sm text-slate-500 font-medium mt-0.5">{{ stat.label }}</p>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="bg-white rounded-3xl border border-slate-100 shadow-sm p-6 mb-6">
      <h2 class="font-bold text-slate-900 mb-4">Quick Actions</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <RouterLink
          v-for="action in quickActions"
          :key="action.label"
          :to="action.to"
          class="flex flex-col items-center gap-2 p-4 rounded-2xl border-2 border-dashed border-slate-200 hover:border-emerald-300 hover:bg-emerald-50 transition-all group"
        >
          <span class="material-icons-outlined text-2xl text-slate-400 group-hover:text-emerald-700">{{ action.icon }}</span>
          <span class="text-xs font-semibold text-slate-500 group-hover:text-emerald-700 text-center">{{ action.label }}</span>
        </RouterLink>
      </div>
    </div>

    <!-- Pending tutors alert -->
    <div v-if="adminStore.stats?.pending_tutors > 0"
      class="bg-amber-50 border border-amber-200 rounded-3xl p-5 flex items-start gap-4"
    >
      <span class="material-icons-outlined text-amber-600 text-2xl mt-0.5">pending_actions</span>
      <div class="flex-1">
        <p class="font-bold text-amber-900">
          {{ adminStore.stats.pending_tutors }} tutor {{ adminStore.stats.pending_tutors === 1 ? 'application' : 'applications' }} pending review
        </p>
        <p class="text-amber-700 text-sm mt-0.5">New tutor registrations require your approval before they can upload content.</p>
      </div>
      <RouterLink to="/admin/tutors" class="text-sm font-bold text-amber-700 hover:text-amber-900 whitespace-nowrap">
        Review →
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'

const adminStore = useAdminStore()

onMounted(() => adminStore.fetchStats())

const statCards = computed(() => [
  {
    label: 'Registered Students',
    value: adminStore.stats?.total_students,
    icon: 'people',
    bgClass: 'bg-blue-50',
    iconClass: 'text-blue-600',
  },
  {
    label: 'Active Tutors',
    value: adminStore.stats?.total_tutors,
    icon: 'school',
    bgClass: 'bg-emerald-50',
    iconClass: 'text-emerald-600',
    badge: adminStore.stats?.pending_tutors > 0 ? `${adminStore.stats.pending_tutors} pending` : null,
  },
  {
    label: 'Languages',
    value: adminStore.stats?.total_languages,
    icon: 'language',
    bgClass: 'bg-purple-50',
    iconClass: 'text-purple-600',
  },
  {
    label: 'Total Units',
    value: adminStore.stats?.total_units,
    icon: 'book',
    bgClass: 'bg-amber-50',
    iconClass: 'text-amber-600',
  },
  {
    label: 'Total Lessons',
    value: adminStore.stats?.total_lessons,
    icon: 'quiz',
    bgClass: 'bg-rose-50',
    iconClass: 'text-rose-600',
  },
])

const quickActions = [
  { label: 'Manage Users', icon: 'manage_accounts', to: '/admin/users' },
  { label: 'Review Tutors', icon: 'how_to_reg', to: '/admin/tutors' },
  { label: 'Add Language', icon: 'add_circle', to: '/admin/content' },
  { label: 'Edit Content', icon: 'edit_note', to: '/admin/content' },
]
</script>

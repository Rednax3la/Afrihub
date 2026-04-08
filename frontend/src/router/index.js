import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  // ── Public ──────────────────────────────────────────────────────────────────
  { path: '/', name: 'splash', component: () => import('@/views/SplashView.vue') },
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
  { path: '/register', name: 'register', component: () => import('@/views/RegisterView.vue') },
  { path: '/register/tutor', name: 'tutor-register', component: () => import('@/views/TutorRegisterView.vue') },

  // ── Student ──────────────────────────────────────────────────────────────────
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true, role: 'student' },
  },
  {
    path: '/courses',
    name: 'courses',
    component: () => import('@/views/CoursesView.vue'),
    meta: { requiresAuth: true, role: 'student' },
  },
  {
    path: '/lesson/:id',
    name: 'lesson',
    component: () => import('@/views/LessonView.vue'),
    meta: { requiresAuth: true, role: 'student' },
  },
  {
    path: '/leaderboard',
    name: 'leaderboard',
    component: () => import('@/views/LeaderboardView.vue'),
    meta: { requiresAuth: true, role: 'student' },
  },
  {
    path: '/subscription',
    name: 'subscription',
    component: () => import('@/views/SubscriptionView.vue'),
    meta: { requiresAuth: true, role: 'student' },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true, role: 'student' },
  },

  // ── Admin ────────────────────────────────────────────────────────────────────
  {
    path: '/admin',
    component: () => import('@/views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'admin-dashboard', component: () => import('@/views/admin/AdminDashboardView.vue') },
      { path: 'users', name: 'admin-users', component: () => import('@/views/admin/AdminUsersView.vue') },
      { path: 'tutors', name: 'admin-tutors', component: () => import('@/views/admin/AdminTutorsView.vue') },
      { path: 'content', name: 'admin-content', component: () => import('@/views/admin/AdminContentView.vue') },
      { path: 'review', name: 'admin-review', component: () => import('@/views/admin/AdminReviewView.vue') },
    ],
  },

  // ── Tutor ────────────────────────────────────────────────────────────────────
  {
    path: '/tutor',
    component: () => import('@/views/tutor/TutorLayout.vue'),
    meta: { requiresAuth: true, role: 'tutor' },
    children: [
      { path: '', redirect: '/tutor/dashboard' },
      { path: 'dashboard', name: 'tutor-dashboard', component: () => import('@/views/tutor/TutorDashboardView.vue') },
      { path: 'content', name: 'tutor-content', component: () => import('@/views/tutor/TutorContentView.vue') },
      { path: 'profile', name: 'tutor-profile', component: () => import('@/views/tutor/TutorProfileView.vue') },
      { path: 'review', name: 'tutor-review', component: () => import('@/views/tutor/TutorReviewView.vue') },
      { path: 'recordings', name: 'tutor-recordings', component: () => import('@/views/tutor/TutorRecordingView.vue') },
    ],
  },

  // ── 404 ──────────────────────────────────────────────────────────────────────
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFoundView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // Redirect away from splash if already logged in
  if (to.name === 'splash' && auth.isLoggedIn) {
    if (auth.isAdmin) return { path: '/admin/dashboard' }
    if (auth.isTutor) return { path: '/tutor/dashboard' }
    return { name: 'dashboard' }
  }

  if (!to.meta.requiresAuth) return true

  if (!auth.isLoggedIn) return { name: 'splash' }

  // Role-based route guards
  const requiredRole = to.meta.role
  if (requiredRole === 'admin' && !auth.isAdmin) {
    return auth.isTutor ? { path: '/tutor/dashboard' } : { name: 'dashboard' }
  }
  if (requiredRole === 'tutor' && !auth.isTutor) {
    return auth.isAdmin ? { path: '/admin/dashboard' } : { name: 'dashboard' }
  }
  if (requiredRole === 'student' && (auth.isAdmin || auth.isTutor)) {
    return auth.isAdmin ? { path: '/admin/dashboard' } : { path: '/tutor/dashboard' }
  }

  return true
})

export default router

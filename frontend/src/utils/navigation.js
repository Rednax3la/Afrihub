export const studentNavigation = [
  { to: '/dashboard', icon: 'home', label: 'Home' },
  { to: '/courses', icon: 'map', label: 'Courses' },
  { to: '/leaderboard', icon: 'emoji_events', label: 'Leaderboard' },
  { to: '/explore', icon: 'explore', label: 'Explore' },
  { to: '/profile', icon: 'person', label: 'Profile' },
]
export const exploreFeatures = [
  { name: 'Games', icon: 'sports_esports', description: 'Language challenges to put your learning into practice.' },
  { name: 'AI Chat', icon: 'forum', description: 'Conversation practice in the languages you are learning.' },
  { name: 'Videos', icon: 'smart_display', description: 'Short stories about language and culture.' },
  { name: 'Dictionary', icon: 'translate', description: 'Look up words and their English meanings.', to: '/dictionary' },
]
export const isNavigationActive = (path, to) => path === to || (to === '/explore' && path === '/dictionary')
export const subscriptionLabel = user => user?.is_premium ? 'Manage subscription' : 'Go Premium'

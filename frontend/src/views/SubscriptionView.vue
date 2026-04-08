<template>
  <section class="min-h-screen bg-[#003B5C] text-white relative overflow-hidden md:pl-64">
    <div class="absolute top-0 right-0 w-80 h-80 bg-[#00A3C1] rounded-full blur-[100px] opacity-20 -mr-40 -mt-40"></div>
    <div class="absolute bottom-0 left-0 w-64 h-64 bg-[#00E5FF] rounded-full blur-[120px] opacity-10 -ml-20 -mb-20"></div>

    <div class="max-w-xl mx-auto">
      <header class="p-6 flex justify-between items-center">
        <RouterLink to="/dashboard" class="w-10 h-10 flex items-center justify-center">
          <span class="material-icons-outlined">close</span>
        </RouterLink>
        <h3 class="font-bold tracking-widest text-xs uppercase">Premium Access</h3>
        <div class="w-10"></div>
      </header>

      <div class="px-8 mt-4 text-center">
        <div class="w-20 h-20 bg-amber-500 rounded-3xl mx-auto mb-6 flex items-center justify-center shadow-2xl shadow-amber-500/40 rotate-12">
          <span class="material-icons-outlined text-4xl">auto_awesome</span>
        </div>
        <h2 class="text-3xl font-bold serif mb-4">Master Your Heritage</h2>
        <p class="text-white/60 text-lg mb-10">Unlock all 50+ African vernaculars with lessons from native tutors.</p>
      </div>

      <div class="px-6 space-y-4 mb-10">
        <!-- Yearly -->
        <div
          @click="selectedPlan = 'yearly'"
          class="p-6 rounded-[2rem] flex justify-between items-center cursor-pointer relative overflow-hidden border-2 transition-all"
          :class="selectedPlan === 'yearly' ? 'bg-white/15 border-amber-400' : 'bg-white/10 border-[#00A3C1]/50'"
        >
          <div class="absolute top-0 right-0 bg-[#00A3C1] text-[10px] font-bold px-4 py-1 rounded-bl-xl">POPULAR</div>
          <div>
            <h4 class="font-bold text-xl">Yearly Access</h4>
            <p class="text-white/50 text-sm">Best for fluent mastery</p>
          </div>
          <div class="text-right">
            <p class="text-2xl font-bold">KES 4,999</p>
            <p class="text-xs text-white/50">/year</p>
            <p class="text-xs text-white/40 mt-0.5">≈ $49.99 USD</p>
          </div>
        </div>

        <!-- Monthly -->
        <div
          @click="selectedPlan = 'monthly'"
          class="p-6 rounded-[2rem] flex justify-between items-center cursor-pointer border-2 transition-all"
          :class="selectedPlan === 'monthly' ? 'bg-white/15 border-amber-400' : 'bg-white/5 border-white/10'"
        >
          <div>
            <h4 class="font-bold text-xl">Monthly</h4>
            <p class="text-white/50 text-sm">Flexible learning</p>
          </div>
          <div class="text-right">
            <p class="text-2xl font-bold">KES 599</p>
            <p class="text-xs text-white/50">/month</p>
            <p class="text-xs text-white/40 mt-0.5">≈ $5.99 USD</p>
          </div>
        </div>
      </div>

      <div class="px-8 space-y-4">
        <div v-for="perk in perks" :key="perk" class="flex items-center gap-3">
          <span class="material-icons-outlined text-[#00E5FF]">verified</span>
          <span class="text-sm text-white/80">{{ perk }}</span>
        </div>
      </div>

      <div class="p-6 mt-10">
        <button
          @click="subscribe"
          class="w-full bg-amber-500 text-[#003B5C] py-5 rounded-3xl font-bold text-lg shadow-xl shadow-amber-500/20 active:scale-95 transition-transform"
        >
          Try 7 Days Free
        </button>
        <p class="text-center text-xs text-white/30 mt-6">Cancel anytime. Terms and conditions apply.</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const toast = useToastStore()
const selectedPlan = ref('yearly')

const perks = [
  'Revenue directly supports native-speaking tutors',
  'Unlimited Hearts & Practice sessions',
  'Offline lessons for remote travel',
  'All 50+ African languages unlocked',
  'Ad-free, distraction-free learning',
  'Downloadable completion certificates',
]

function subscribe() {
  toast.info('Payment integration launching soon! Join the waitlist to be first.')
  router.push({ path: '/dashboard', query: { waitlist_plan: selectedPlan.value } })
}
</script>

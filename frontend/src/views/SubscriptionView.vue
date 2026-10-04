<template>
  <section class="min-h-screen bg-[#003B5C] text-white relative overflow-hidden md:pl-64 overflow-y-auto">
    <div class="absolute top-0 right-0 w-80 h-80 bg-[#00A3C1] rounded-full blur-[100px] opacity-20 -mr-40 -mt-40"></div>
    <div class="absolute bottom-0 left-0 w-64 h-64 bg-[#00E5FF] rounded-full blur-[120px] opacity-10 -ml-20 -mb-20"></div>

    <div class="max-w-xl mx-auto">
      <header class="p-6 flex justify-between items-center">
        <RouterLink to="/profile" aria-label="Back to profile" class="w-10 h-10 flex items-center justify-center">
          <span class="material-icons-outlined">arrow_back</span>
        </RouterLink>
        <h3 class="font-bold tracking-widest text-xs uppercase">Premium Access</h3>
        <div class="w-10"></div>
      </header>

      <div class="px-5 sm:px-8 mt-2 sm:mt-4 text-center">
        <div class="w-14 h-14 sm:w-20 sm:h-20 bg-amber-500 rounded-3xl mx-auto mb-6 flex items-center justify-center shadow-2xl shadow-amber-500/40 rotate-12">
          <span class="material-icons-outlined text-4xl">auto_awesome</span>
        </div>
        <h2 class="text-2xl sm:text-3xl font-bold serif mb-4">Master Your Heritage</h2>
        <p class="text-white/60 text-lg mb-5 sm:mb-10">Continue beyond the first three units in available language courses.</p>
      </div>

      <div class="px-4 sm:px-6 space-y-3 sm:space-y-4 mb-5 sm:mb-10">
        <!-- Yearly -->
        <div
          @click="selectedPlan = 'yearly'"
          class="p-4 sm:p-6 rounded-[1.5rem] sm:rounded-[2rem] flex justify-between items-center cursor-pointer relative overflow-hidden border-2 transition-all"
          :class="selectedPlan === 'yearly' ? 'bg-white/15 border-amber-400' : 'bg-white/10 border-[#00A3C1]/50'"
        >
          <div class="absolute top-0 right-0 bg-[#00A3C1] text-[10px] font-bold px-4 py-1 rounded-bl-xl">POPULAR</div>
          <div>
            <h4 class="font-bold text-xl">Yearly Access</h4>
            <p class="text-white/50 text-sm">Best for fluent mastery</p>
          </div>
          <div class="text-right">
            <p class="text-2xl font-bold">KES 12,999</p>
            <p class="text-xs text-white/50">/year</p>
            <p class="text-xs text-white/40 mt-0.5">≈ $100 USD</p>
          </div>
        </div>

        <!-- Monthly -->
        <div
          @click="selectedPlan = 'monthly'"
          class="p-4 sm:p-6 rounded-[1.5rem] sm:rounded-[2rem] flex justify-between items-center cursor-pointer border-2 transition-all"
          :class="selectedPlan === 'monthly' ? 'bg-white/15 border-amber-400' : 'bg-white/5 border-white/10'"
        >
          <div>
            <h4 class="font-bold text-xl">Monthly</h4>
            <p class="text-white/50 text-sm">Flexible learning</p>
          </div>
          <div class="text-right">
            <p class="text-2xl font-bold">KES 1,299</p>
            <p class="text-xs text-white/50">/month</p>
            <p class="text-xs text-white/40 mt-0.5">≈ $10 USD</p>
          </div>
        </div>
      </div>

      <div class="px-8 space-y-4">
        <div v-for="perk in perks" :key="perk" class="flex items-center gap-3">
          <span class="material-icons-outlined text-[#00E5FF]">verified</span>
          <span class="text-sm text-white/80">{{ perk }}</span>
        </div>
      </div>

      <div class="px-4 sm:px-6 mt-5 sm:mt-10 pb-8">
        <p v-if="auth.user?.is_premium" class="mb-4 text-sm">Your subscription is active<span v-if="auth.user.expires_at"> until {{ new Date(auth.user.expires_at).toLocaleDateString() }}</span>.</p>
        <SubscriptionCheckout :tier="selectedPlan" />
        <p class="text-center text-xs text-white/30 mt-6">Payment must be confirmed before subscription access is activated.</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
import SubscriptionCheckout from '@/components/SubscriptionCheckout.vue'

const selectedPlan = ref('yearly')

const perks = ['Access to currently published units beyond unit 3', 'Monthly or yearly access at the existing plan prices']

</script>

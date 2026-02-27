<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Sidebar + header -->
    <div class="flex h-screen overflow-hidden">
      <!-- Sidebar -->
      <aside class="hidden md:flex flex-col w-56 bg-emerald-800 text-white">
        <div class="p-4 border-b border-emerald-700">
          <div class="flex items-center gap-2">
            <span class="text-2xl">🍽️</span>
            <span class="font-bold text-lg">FamilyMeal</span>
          </div>
          <div class="text-xs text-emerald-300 mt-1">Administration</div>
        </div>
        <nav class="flex-1 p-3 space-y-1">
          <NuxtLink
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition"
            :class="isActive(item.path)
              ? 'bg-emerald-600 text-white'
              : 'text-emerald-100 hover:bg-emerald-700'"
          >
            <span class="text-base">{{ item.icon }}</span>
            {{ item.label }}
          </NuxtLink>
        </nav>
        <div class="p-3 border-t border-emerald-700">
          <button @click="logout" class="flex items-center gap-2 text-sm text-emerald-300 hover:text-white w-full px-3 py-2">
            <span>🚪</span> Déconnexion
          </button>
        </div>
      </aside>

      <!-- Main content -->
      <div class="flex-1 flex flex-col overflow-hidden">
        <!-- Top bar mobile -->
        <header class="md:hidden bg-emerald-800 text-white px-4 py-3 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span>🍽️</span>
            <span class="font-bold">FamilyMeal</span>
          </div>
          <button @click="mobileMenuOpen = !mobileMenuOpen" class="text-white">☰</button>
        </header>

        <!-- Mobile menu -->
        <div v-if="mobileMenuOpen" class="md:hidden bg-emerald-700 text-white py-2">
          <NuxtLink
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            @click="mobileMenuOpen = false"
            class="flex items-center gap-3 px-4 py-2.5 text-sm"
          >
            <span>{{ item.icon }}</span> {{ item.label }}
          </NuxtLink>
        </div>

        <main class="flex-1 overflow-y-auto p-6">
          <slot />
        </main>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const mobileMenuOpen = ref(false)

const navItems = [
  { path: '/admin', icon: '📊', label: 'Tableau de bord' },
  { path: '/admin/planning', icon: '📅', label: 'Planning' },
  { path: '/admin/plats', icon: '🍲', label: 'Plats' },
  { path: '/admin/ingredients', icon: '🥦', label: 'Ingrédients' },
  { path: '/admin/membres', icon: '👨‍👩‍👧', label: 'Membres' },
  { path: '/admin/courses', icon: '🛒', label: 'Liste de courses' },
  { path: '/admin/demandes', icon: '📬', label: 'Demandes' },
  { path: '/admin/preferences', icon: '❤️', label: 'Préférences' },
  { path: '/admin/parametres', icon: '⚙️', label: 'Paramètres' },
  { path: '/admin/outils', icon: '🔧', label: 'Outils' },
]

function isActive(path: string) {
  if (path === '/admin') return route.path === '/admin'
  return route.path.startsWith(path)
}

function logout() {
  auth.logout()
  navigateTo('/login')
}
</script>

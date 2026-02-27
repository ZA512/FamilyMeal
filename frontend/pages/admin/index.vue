<template>
  <div class="space-y-6">
    <h1 class="text-xl font-bold text-gray-800">Tableau de bord</h1>

    <!-- KPIs -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl shadow p-4 text-center">
        <div class="text-3xl font-bold text-emerald-600">{{ stats.nbPlats }}</div>
        <div class="text-xs text-gray-500 mt-1">Plats</div>
      </div>
      <div class="bg-white rounded-xl shadow p-4 text-center">
        <div class="text-3xl font-bold text-emerald-600">{{ stats.nbMembres }}</div>
        <div class="text-xs text-gray-500 mt-1">Membres</div>
      </div>
      <div class="bg-white rounded-xl shadow p-4 text-center">
        <div class="text-3xl font-bold text-emerald-600">{{ stats.nbIngredients }}</div>
        <div class="text-xs text-gray-500 mt-1">Ingrédients</div>
      </div>
      <NuxtLink to="/admin/demandes" class="bg-white rounded-xl shadow p-4 text-center block hover:ring-2 ring-orange-400 transition">
        <div class="text-3xl font-bold" :class="stats.demandesEnAttente > 0 ? 'text-orange-500' : 'text-gray-400'">
          {{ stats.demandesEnAttente }}
        </div>
        <div class="text-xs text-gray-500 mt-1">Demandes en attente</div>
      </NuxtLink>
    </div>

    <!-- Semaine courante -->
    <div class="bg-white rounded-2xl shadow p-5">
      <div class="flex items-center justify-between mb-4">
        <h2 class="font-semibold text-gray-800">Planning de la semaine</h2>
        <NuxtLink to="/admin/planning" class="text-sm text-emerald-600 hover:underline">
          Gérer →
        </NuxtLink>
      </div>

      <div v-if="loadingSemaine" class="text-gray-400 text-sm">Chargement…</div>
      <div v-else-if="!semaineCourante" class="text-gray-400 text-sm py-4 text-center">
        Aucun planning publié cette semaine.
        <NuxtLink to="/admin/planning" class="text-emerald-600 hover:underline block mt-1">Générer un planning →</NuxtLink>
      </div>
      <div v-else>
        <div class="flex items-center gap-2 mb-3">
          <span class="px-2 py-0.5 rounded-full text-xs font-medium"
            :class="semaineCourante.statut === 'publie' ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-500'"
          >
            {{ semaineCourante.statut === 'publie' ? 'Publié' : 'Brouillon' }}
          </span>
          <span class="text-sm text-gray-500">du {{ formatDate(semaineCourante.date_debut) }}</span>
        </div>
        <div class="grid grid-cols-7 gap-1 text-center text-xs">
          <div v-for="jour in joursLabels" :key="jour" class="font-medium text-gray-400">{{ jour }}</div>
          <div
            v-for="cr in creneauxSemaine"
            :key="cr.key"
            class="p-1 bg-gray-50 rounded text-gray-700 leading-tight min-h-[2.5rem] flex flex-col justify-center"
          >
            <div v-if="cr.midi" class="font-medium truncate">{{ cr.midi }}</div>
            <div v-if="cr.soir" class="text-gray-400 truncate">{{ cr.soir }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Accès rapides -->
    <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
      <NuxtLink v-for="link in quickLinks" :key="link.to" :to="link.to"
        class="bg-white rounded-xl shadow p-4 flex flex-col items-center gap-2 hover:ring-2 ring-emerald-400 transition text-center"
      >
        <span class="text-2xl">{{ link.icon }}</span>
        <span class="text-sm font-medium text-gray-700">{{ link.label }}</span>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
import 'dayjs/locale/fr'
import { useApi } from '~/composables/useApi'

definePageMeta({ layout: 'admin', middleware: 'admin' })
dayjs.locale('fr')

const api = useApi()

const stats = reactive({ nbPlats: 0, nbMembres: 0, nbIngredients: 0, demandesEnAttente: 0 })
const semaineCourante = ref<any>(null)
const loadingSemaine = ref(true)

const joursLabels = ['Lun','Mar','Mer','Jeu','Ven','Sam','Dim']

const quickLinks = [
  { to: '/admin/plats', icon: '🍲', label: 'Gérer les plats' },
  { to: '/admin/membres', icon: '👨‍👩‍👧', label: 'Membres' },
  { to: '/admin/ingredients', icon: '🥦', label: 'Ingrédients' },
  { to: '/admin/courses', icon: '🛒', label: 'Liste de courses' },
  { to: '/admin/demandes', icon: '📬', label: 'Demandes' },
  { to: '/admin/parametres', icon: '⚙️', label: 'Paramètres' },
]

const creneauxSemaine = computed(() => {
  if (!semaineCourante.value?.creneaux) return []
  const debut = dayjs(semaineCourante.value.date_debut)
  return Array.from({ length: 7 }, (_, i) => {
    const date = debut.add(i, 'day').format('YYYY-MM-DD')
    const midic = semaineCourante.value.creneaux.find((c: any) => c.date === date && c.creneau === 'midi')
    const soirc = semaineCourante.value.creneaux.find((c: any) => c.date === date && c.creneau === 'soir')
    return { key: date, midi: midic?.plat_principal?.nom || '', soir: soirc?.plat_principal?.nom || '' }
  })
})

function formatDate(d: string) {
  return dayjs(d).format('D MMMM YYYY')
}

onMounted(async () => {
  const [plats, membres, ingredients, demandes, semaine] = await Promise.allSettled([
    api.get('/plats/'),
    api.get('/membres/'),
    api.get('/ingredients/'),
    api.get('/demandes/?statut=en_attente'),
    api.get('/semaines/courante/'),
  ])

  if (plats.status === 'fulfilled') { const d = plats.value as any; stats.nbPlats = Array.isArray(d) ? d.length : (d.results?.length ?? 0) }
  if (membres.status === 'fulfilled') { const d = membres.value as any; stats.nbMembres = Array.isArray(d) ? d.length : (d.results?.length ?? 0) }
  if (ingredients.status === 'fulfilled') { const d = ingredients.value as any; stats.nbIngredients = Array.isArray(d) ? d.length : (d.results?.length ?? 0) }
  if (demandes.status === 'fulfilled') { const d = demandes.value as any; stats.demandesEnAttente = Array.isArray(d) ? d.length : (d.results?.length ?? 0) }
  if (semaine.status === 'fulfilled') semaineCourante.value = semaine.value

  loadingSemaine.value = false
})
</script>

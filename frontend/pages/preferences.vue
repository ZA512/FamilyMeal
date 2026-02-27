<template>
  <div class="space-y-4">
    <h1 class="text-xl font-bold text-gray-800">Mes préférences</h1>

    <!-- Pas de membre sélectionné -->
    <div v-if="!auth.membreId" class="bg-yellow-50 border border-yellow-200 rounded-xl p-5 text-sm text-yellow-800">
      Vous devez choisir votre profil pour gérer vos préférences.
    </div>

    <template v-else>
      <!-- Onglets -->
      <div class="flex gap-1 bg-white rounded-xl shadow px-3 py-2 w-fit">
        <button
          v-for="t in onglets"
          :key="t.key"
          @click="onglet = t.key"
          class="px-4 py-1.5 rounded-lg text-sm font-medium transition"
          :class="onglet === t.key ? 'bg-emerald-600 text-white' : 'text-gray-600 hover:bg-gray-100'"
        >{{ t.label }}</button>
      </div>

      <!-- Chargement -->
      <div v-if="loading" class="text-center py-16 text-gray-400">Chargement…</div>

      <template v-else>
        <!-- Recherche (onglet tous) -->
        <div v-if="onglet === 'tous'" class="flex gap-2">
          <input
            v-model="recherche"
            type="text"
            placeholder="Rechercher un plat…"
            class="border rounded-lg px-3 py-1.5 text-sm w-64"
          />
        </div>

        <!-- Liste des plats -->
        <div class="bg-white rounded-xl shadow divide-y divide-gray-100">
          <div v-if="platsVus.length === 0" class="py-10 text-center text-gray-400 text-sm">
            Aucun plat à afficher.
          </div>
          <div
            v-for="plat in platsVus"
            :key="plat.id"
            class="flex items-center justify-between px-4 py-3 hover:bg-gray-50"
          >
            <span class="text-sm font-medium text-gray-800">{{ plat.nom }}</span>
            <div class="flex gap-1">
              <button
                v-for="opt in noteOpts"
                :key="opt.value"
                @click="setNote(plat.id, opt.value)"
                :title="opt.label"
                class="px-2 py-1 rounded text-xs font-bold transition border"
                :class="getNote(plat.id) === opt.value
                  ? opt.activeClass
                  : 'bg-white border-gray-200 text-gray-400 hover:border-gray-400'"
              >{{ opt.letter }}</button>
            </div>
          </div>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { useApi } from '~/composables/useApi'
import dayjs from 'dayjs'
import 'dayjs/locale/fr'

definePageMeta({ middleware: 'reader' })

dayjs.locale('fr')

const auth = useAuthStore()
const api = useApi()

const loading = ref(true)
const onglet = ref<'semaine' | 'tous'>('semaine')
const recherche = ref('')

const onglets = [
  { key: 'semaine', label: '📅 Cette semaine' },
  { key: 'tous',    label: '📋 Tous les plats' },
]

const platsSemaine = ref<any[]>([])
const tousLesPlats = ref<any[]>([])
const prefs = ref<Record<number, string>>({}) // plat_id → note

const noteOpts = [
  { value: 'aime',    letter: 'A', label: 'Aime',    activeClass: 'bg-emerald-100 border-emerald-500 text-emerald-700' },
  { value: 'neutre',  letter: 'N', label: 'Neutre',  activeClass: 'bg-gray-200 border-gray-500 text-gray-700' },
  { value: 'deteste', letter: 'D', label: 'Déteste', activeClass: 'bg-red-100 border-red-500 text-red-700' },
]

function normaliser(s: string) {
  return s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
}

const platsVus = computed(() => {
  let base = onglet.value === 'semaine' ? platsSemaine.value : tousLesPlats.value
  if (onglet.value === 'tous' && recherche.value.trim()) {
    const q = normaliser(recherche.value.trim())
    base = base.filter(p => normaliser(p.nom).includes(q))
  }
  return base
})

function getNote(platId: number): string {
  return prefs.value[platId] ?? 'neutre'
}

const savingSet = ref<Set<number>>(new Set())

async function setNote(platId: number, note: string) {
  if (savingSet.value.has(platId)) return
  savingSet.value.add(platId)
  prefs.value[platId] = note // optimistic
  try {
    await api.post('/preferences/set/', { plat: platId, note })
  } catch {
    // relire la vraie valeur
    const data: any = await api.get(`/preferences/?membre=${auth.membreId}`).catch(() => [])
    const list = Array.isArray(data) ? data : data.results ?? []
    list.forEach((p: any) => { prefs.value[p.plat] = p.note })
  } finally {
    savingSet.value.delete(platId)
  }
}

async function charger() {
  if (!auth.membreId) { loading.value = false; return }
  loading.value = true
  try {
    const [tousData, prefsData, semainesData] = await Promise.all([
      api.get<any>('/plats/'),
      api.get<any>(`/preferences/?membre=${auth.membreId}`),
      api.get<any>('/semaines/'),
    ])

    tousLesPlats.value = (Array.isArray(tousData) ? tousData : tousData.results ?? [])
      .filter((p: any) => p.statut === 'actif')
      .sort((a: any, b: any) => a.nom.localeCompare(b.nom))

    // Préférences du membre
    const prefsList = Array.isArray(prefsData) ? prefsData : prefsData.results ?? []
    prefsList.forEach((p: any) => { prefs.value[p.plat] = p.note })

    // Plats de la semaine courante (publiée la plus récente)
    const semaines: any[] = (Array.isArray(semainesData) ? semainesData : semainesData.results ?? [])
      .filter((s: any) => s.statut === 'publie' || s.statut === 'brouillon')
      .sort((a: any, b: any) => b.date_debut.localeCompare(a.date_debut))

    if (semaines.length > 0) {
      const detail: any = await api.get(`/semaines/${semaines[0].id}/`)
      const platsIds = new Set<number>()
      const platsMap: Record<number, any> = {}
      ;(detail.creneaux || []).forEach((c: any) => {
        if (c.plat_principal) { platsIds.add(c.plat_principal.id); platsMap[c.plat_principal.id] = c.plat_principal }
        if (c.plat_secours)  { platsIds.add(c.plat_secours.id);  platsMap[c.plat_secours.id]  = c.plat_secours }
      })
      platsSemaine.value = Array.from(platsIds).map(id => platsMap[id]).sort((a, b) => a.nom.localeCompare(b.nom))
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  auth.initFromCookies()
  charger()
})
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold text-gray-800">Préférences des membres</h1>
      <span class="text-sm text-gray-500">Les modifications sont enregistrées en temps réel</span>
    </div>

    <!-- Filtres -->
    <div class="bg-white rounded-xl shadow px-4 py-3 flex flex-wrap gap-3 items-center">
      <input
        v-model="recherche"
        type="text"
        placeholder="Rechercher un plat…"
        class="border rounded-lg px-3 py-1.5 text-sm w-56"
      />
      <select v-model="filtreStatut" class="border rounded-lg px-3 py-1.5 text-sm">
        <option value="">Tous statuts</option>
        <option value="actif">Actifs</option>
        <option value="archive">Archivés</option>
      </select>
    </div>

    <!-- Chargement -->
    <div v-if="loading" class="text-center py-16 text-gray-400">Chargement…</div>

    <!-- Tableau -->
    <div v-else class="bg-white rounded-xl shadow overflow-x-auto">
      <table class="min-w-full text-sm">
        <thead>
          <tr class="bg-gray-50 border-b border-gray-200">
            <th class="px-4 py-3 text-left font-semibold text-gray-700 sticky left-0 bg-gray-50 min-w-[200px]">
              Plat
            </th>
            <th
              v-for="m in membres"
              :key="m.id"
              class="px-3 py-3 text-center font-semibold min-w-[90px]"
            >
              <div class="flex flex-col items-center gap-1">
                <span
                  class="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold"
                  :style="{ backgroundColor: m.couleur || '#9ca3af' }"
                >{{ m.prenom.charAt(0) }}</span>
                <span class="text-gray-700 text-xs">{{ m.prenom }}</span>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="plat in platsFiltres"
            :key="plat.id"
            class="border-b border-gray-100 hover:bg-gray-50"
          >
            <td class="px-4 py-2.5 sticky left-0 bg-white hover:bg-gray-50 font-medium text-gray-800">
              {{ plat.nom }}
              <span v-if="plat.statut === 'archive'" class="ml-1 text-xs text-gray-400">(archivé)</span>
            </td>
            <td
              v-for="m in membres"
              :key="m.id"
              class="px-3 py-2 text-center"
            >
              <div class="flex gap-0.5 justify-center">
                <button
                  v-for="opt in noteOpts"
                  :key="opt.value"
                  @click="setNote(plat.id, m.id, opt.value)"
                  :title="opt.label"
                  class="px-1.5 py-0.5 rounded text-xs font-bold transition border"
                  :class="getNote(plat.id, m.id) === opt.value
                    ? opt.activeClass
                    : 'bg-white border-gray-200 text-gray-400 hover:border-gray-400'"
                >{{ opt.letter }}</button>
              </div>
            </td>
          </tr>
          <tr v-if="platsFiltres.length === 0">
            <td :colspan="membres.length + 1" class="text-center py-10 text-gray-400">
              Aucun plat trouvé.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin' })

const api = useApi()

const loading = ref(true)
const recherche = ref('')
const filtreStatut = ref('actif')

const plats = ref<any[]>([])
const membres = ref<any[]>([])
// prefs[plat_id][membre_id] = 'aime' | 'neutre' | 'deteste'
const prefs = ref<Record<number, Record<number, string>>>({})

const noteOpts = [
  { value: 'aime',    letter: 'A', label: 'Aime',    activeClass: 'bg-emerald-100 border-emerald-500 text-emerald-700' },
  { value: 'neutre',  letter: 'N', label: 'Neutre',  activeClass: 'bg-gray-200 border-gray-500 text-gray-700' },
  { value: 'deteste', letter: 'D', label: 'Déteste', activeClass: 'bg-red-100 border-red-500 text-red-700' },
]

function normaliser(s: string) {
  return s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
}

const platsFiltres = computed(() => {
  let liste = plats.value
  if (filtreStatut.value) liste = liste.filter(p => p.statut === filtreStatut.value)
  if (recherche.value.trim()) {
    const q = normaliser(recherche.value.trim())
    liste = liste.filter(p => normaliser(p.nom).includes(q))
  }
  return liste
})

function getNote(platId: number, membreId: number): string {
  return prefs.value[platId]?.[membreId] ?? 'neutre'
}

const saving = ref<Set<string>>(new Set())

async function setNote(platId: number, membreId: number, note: string) {
  const key = `${platId}_${membreId}`
  if (saving.value.has(key)) return
  saving.value.add(key)

  // Optimistic update
  if (!prefs.value[platId]) prefs.value[platId] = {}
  prefs.value[platId][membreId] = note

  try {
    await api.post('/preferences/set/', { membre: membreId, plat: platId, note })
  } catch {
    // Rollback silencieux — on relance la donnée réelle
    const data: any = await api.get('/preferences/').catch(() => null)
    if (data?.results || Array.isArray(data)) {
      const list = Array.isArray(data) ? data : data.results
      list.forEach((p: any) => {
        if (!prefs.value[p.plat]) prefs.value[p.plat] = {}
        prefs.value[p.plat][p.membre] = p.note
      })
    }
  } finally {
    saving.value.delete(key)
  }
}

async function charger() {
  loading.value = true
  try {
    const [platsData, membresData, prefsData] = await Promise.all([
      api.get<any>('/plats/'),
      api.get<any>('/membres/'),
      api.get<any>('/preferences/'),
    ])

    plats.value = (Array.isArray(platsData) ? platsData : platsData.results ?? [])
      .sort((a: any, b: any) => a.nom.localeCompare(b.nom))
    membres.value = (Array.isArray(membresData) ? membresData : membresData.results ?? [])
      .filter((m: any) => m.actif)

    const prefsList = Array.isArray(prefsData) ? prefsData : prefsData.results ?? []
    const map: Record<number, Record<number, string>> = {}
    prefsList.forEach((p: any) => {
      if (!map[p.plat]) map[p.plat] = {}
      map[p.plat][p.membre] = p.note
    })
    prefs.value = map
  } finally {
    loading.value = false
  }
}

onMounted(charger)
</script>

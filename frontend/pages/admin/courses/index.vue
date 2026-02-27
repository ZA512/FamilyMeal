<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold text-gray-800">Liste de courses</h1>
    </div>

    <!-- Sélecteur de semaine publiée -->
    <div class="flex flex-wrap items-center gap-3">
      <select v-model="semaineId" @change="chargerListe" class="border rounded-lg px-3 py-2 text-sm">
        <option value="">— Sélectionner une semaine —</option>
        <option v-for="s in semaines" :key="s.id" :value="s.id">
          Semaine du {{ formatDate(s.date_debut) }}
        </option>
      </select>
      <button
        v-if="semaineId && !liste"
        @click="generer"
        :disabled="generating"
        class="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-emerald-700 disabled:opacity-50"
      >
        {{ generating ? 'Génération…' : '🛒 Générer la liste' }}
      </button>
      <template v-if="liste">
        <span class="px-2 py-0.5 rounded-full text-xs font-medium"
          :class="liste.statut === 'validee' ? 'bg-emerald-100 text-emerald-700' : 'bg-yellow-100 text-yellow-700'"
        >{{ liste.statut }}</span>
        <button
          v-if="liste.statut === 'brouillon'"
          @click="valider"
          :disabled="validating"
          class="bg-emerald-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-emerald-700 disabled:opacity-50"
        >
          ✓ Valider les achats
        </button>
        <button @click="ajouterItem" class="bg-white border px-3 py-1.5 rounded-lg text-sm hover:bg-gray-50">
          + Ajouter un article
        </button>
      </template>
    </div>

    <!-- Liste groupée par catégorie -->
    <div v-if="loading" class="text-center py-12 text-gray-400">Chargement…</div>
    <div v-else-if="liste" class="space-y-4">
      <div v-for="(items, categorie) in itemsParCategorie" :key="categorie" class="bg-white rounded-2xl shadow overflow-hidden">
        <div class="px-4 py-2.5 bg-gray-50 border-b text-xs font-semibold text-gray-500 uppercase tracking-wide">
          {{ categorie }}
        </div>
        <ul class="divide-y divide-gray-100">
          <li v-for="item in items" :key="item.id" class="flex items-center gap-3 px-4 py-3">
            <button @click="cocherItem(item)" :disabled="couchingId === item.id"
              class="w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition"
              :class="item.coche ? 'bg-emerald-500 border-emerald-500 text-white' : 'border-gray-300'"
            >
              <span v-if="item.coche" class="text-xs">✓</span>
            </button>
            <div class="flex-1 min-w-0">
              <div class="text-sm font-medium text-gray-800" :class="item.coche ? 'line-through text-gray-400' : ''">
                {{ item.nom_libre || item.ingredient_nom }}
              </div>
              <div class="text-xs text-gray-400" v-if="item.quantite">
                {{ item.quantite }} {{ item.unite }}
              </div>
            </div>
            <div class="flex items-center gap-2">
              <!-- Lien produit en ligne -->
              <a v-if="item.url_produit" :href="item.url_produit" target="_blank" rel="noopener noreferrer"
                class="text-xs text-blue-500 hover:underline">🔗</a>
              <span class="text-xs text-gray-300">{{ sourceLabel(item.source) }}</span>
              <button @click="supprimerItem(item)" class="text-red-400 text-xs hover:text-red-600">✕</button>
            </div>
          </li>
        </ul>
      </div>

      <div v-if="Object.keys(itemsParCategorie).length === 0" class="text-center py-8 text-gray-400">
        Liste vide.
      </div>
    </div>

    <!-- Modal ajout article -->
    <div v-if="modalAjout" class="fixed inset-0 z-50 flex items-center justify-center p-4" style="background:rgba(0,0,0,0.5)">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm">
        <div class="flex items-center justify-between px-6 py-4 border-b">
          <h2 class="font-semibold text-gray-800">Ajouter un article</h2>
          <button @click="modalAjout = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div class="px-6 py-4 space-y-3">
          <div>
            <label class="label">Nom</label>
            <input v-model="ajoutForm.nom_libre" type="text" class="input" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Quantité</label>
              <input v-model.number="ajoutForm.quantite" type="number" step="0.01" class="input" />
            </div>
            <div>
              <label class="label">Unité</label>
              <input v-model="ajoutForm.unite" type="text" class="input" />
            </div>
          </div>
          <div>
            <label class="label">Notes</label>
            <input v-model="ajoutForm.notes" type="text" class="input" />
          </div>
        </div>
        <div class="flex justify-end gap-3 px-6 py-4 border-t">
          <button @click="modalAjout = false" class="text-sm text-gray-600">Annuler</button>
          <button @click="sauvegarderAjout" :disabled="ajoutSaving" class="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm disabled:opacity-50">
            {{ ajoutSaving ? '…' : 'Ajouter' }}
          </button>
        </div>
      </div>
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
const semaines = ref<any[]>([])
const semaineId = ref<any>('')
const liste = ref<any>(null)
const loading = ref(false)
const generating = ref(false)
const validating = ref(false)
const couchingId = ref<number | null>(null)
const modalAjout = ref(false)
const ajoutSaving = ref(false)

const ajoutForm = reactive({ nom_libre: '', quantite: null as number | null, unite: '', notes: '' })

function formatDate(d: string) { return dayjs(d).format('D MMM YYYY') }

const SOURCES: Record<string, string> = { plat: 'plat', systematique: 'syst.', suggestion: 'suggest.', manuel: '' }
function sourceLabel(s: string) { return SOURCES[s] ?? '' }

const itemsParCategorie = computed(() => {
  if (!liste.value?.items) return {}
  const groups: Record<string, any[]> = {}
  for (const item of liste.value.items) {
    const cat = item.categorie_nom || 'Divers'
    if (!groups[cat]) groups[cat] = []
    groups[cat].push(item)
  }
  return groups
})

async function chargerSemaines() {
  const raw = await api.get<any>('/semaines/?statut=publie')
  const data = Array.isArray(raw) ? raw : (raw.results ?? [])
  semaines.value = data.sort((a: any, b: any) => b.date_debut.localeCompare(a.date_debut))
}

async function chargerListe() {
  if (!semaineId.value) { liste.value = null; return }
  loading.value = true
  try {
    const raw = await api.get<any>(`/courses/?semaine=${semaineId.value}`)
    const data = Array.isArray(raw) ? raw : (raw.results ?? [])
    liste.value = data.length ? data[0] : null
  } finally {
    loading.value = false
  }
}

async function generer() {
  generating.value = true
  try {
    const data = await api.post('/courses/generer/', { semaine_id: semaineId.value })
    liste.value = data
  } catch {
    alert('Erreur lors de la génération de la liste.')
  } finally {
    generating.value = false
  }
}

async function valider() {
  if (!confirm('Valider les achats ? Cela archivera l\'historique et marquera la liste comme validée.')) return
  validating.value = true
  try {
    await api.post(`/courses/${liste.value.id}/valider/`, {})
    await chargerListe()
  } finally {
    validating.value = false
  }
}

async function cocherItem(item: any) {
  couchingId.value = item.id
  try {
    const data = await api.patch(`/items-courses/${item.id}/cocher/`, {})
    item.coche = data.coche
  } finally {
    couchingId.value = null
  }
}

async function supprimerItem(item: any) {
  await api.del(`/items-courses/${item.id}/`)
  liste.value.items = liste.value.items.filter((i: any) => i.id !== item.id)
}

function ajouterItem() {
  Object.assign(ajoutForm, { nom_libre: '', quantite: null, unite: '', notes: '' })
  modalAjout.value = true
}

async function sauvegarderAjout() {
  ajoutSaving.value = true
  try {
    const item = await api.post('/items-courses/', {
      liste: liste.value.id,
      nom_libre: ajoutForm.nom_libre,
      quantite: ajoutForm.quantite,
      unite: ajoutForm.unite,
      notes: ajoutForm.notes,
      source: 'manuel',
    })
    liste.value.items.push(item)
    modalAjout.value = false
  } finally {
    ajoutSaving.value = false
  }
}

onMounted(async () => {
  await chargerSemaines()
})
</script>

<style scoped>
.label { @apply block text-sm font-medium text-gray-700 mb-1; }
.input { @apply w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400; }
</style>

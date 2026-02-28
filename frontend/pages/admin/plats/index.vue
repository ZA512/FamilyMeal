<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold text-gray-800">Plats</h1>
      <button @click="ouvrirNouveau" class="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-emerald-700">
        + Nouveau plat
      </button>
    </div>

    <!-- Filtres -->
    <div class="flex flex-wrap gap-2">
      <input v-model="recherche" type="text" placeholder="Rechercher…" class="border rounded-lg px-3 py-1.5 text-sm w-48" />
      <select v-model="filtreSecours" class="border rounded-lg px-3 py-1.5 text-sm">
        <option value="">Tous les types</option>
        <option value="false">Plats principaux</option>
        <option value="true">Plats de secours</option>
      </select>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-2xl shadow overflow-hidden">
      <div v-if="loading" class="text-center py-12 text-gray-400">Chargement…</div>
      <table v-else class="min-w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Statut</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Secours</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Coût</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="plat in platsFiltres" :key="plat.id" class="hover:bg-gray-50 group">
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <img v-if="plat.photo" :src="plat.photo" alt="" class="w-8 h-8 rounded-lg object-cover flex-shrink-0" />
                <div>
                  <span class="font-medium text-sm text-gray-800">{{ plat.nom }}</span>
                  <span v-if="plat.variants?.length" class="ml-2 px-1.5 py-0.5 rounded text-xs bg-violet-100 text-violet-700">⇅ {{ plat.variants.length }} variant{{ plat.variants.length > 1 ? 's' : '' }}</span>
                </div>
              </div>
            </td>
            <td class="px-4 py-3 hidden md:table-cell">
              <span class="px-2 py-0.5 rounded-full text-xs font-medium"
                :class="statutClass(plat.statut)">
                {{ plat.statut }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm text-gray-400 hidden md:table-cell">
              {{ plat.est_secours ? '✓' : '' }}
            </td>
            <td class="px-4 py-3 text-right hidden md:table-cell">
              <span v-if="plat.cout_estime !== null" class="text-sm font-medium text-emerald-700">{{ plat.cout_estime.toFixed(2) }} €</span>
              <span v-else class="text-xs text-gray-300">—</span>
            </td>
            <td class="px-4 py-3 text-right">
              <span class="opacity-0 group-hover:opacity-100 transition-opacity inline-flex gap-3">
                <button @click="ouvrirEdition(plat)" class="text-xs text-emerald-600 hover:underline">Modifier</button>
                <button @click="dupliquerPlat(plat)" class="text-xs text-blue-500 hover:underline">Dupliquer</button>
                <button @click="supprimerPlat(plat)" class="text-xs text-red-500 hover:underline">Supprimer</button>
              </span>
            </td>
          </tr>
          <tr v-if="platsFiltres.length === 0">
            <td colspan="5" class="px-4 py-8 text-center text-gray-400 text-sm">Aucun plat trouvé.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal plat -->
    <div v-if="modal" class="fixed inset-0 z-50 flex items-start justify-center p-4 overflow-y-auto" style="background:rgba(0,0,0,0.5)">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl my-4">
        <div class="flex items-center justify-between px-6 py-4 border-b">
          <h2 class="font-semibold text-gray-800">{{ editId ? 'Modifier le plat' : 'Nouveau plat' }}</h2>
          <button @click="modal = false" class="text-gray-400 hover:text-gray-600 text-lg">✕</button>
        </div>
        <div class="px-6 py-4 space-y-4 max-h-[80vh] overflow-y-auto">
          <!-- Nom -->
          <div>
            <label class="label">Nom *</label>
            <input v-model="form.nom" type="text" required class="input" />
          </div>
          <div>
            <label class="label">Description</label>
            <textarea v-model="form.description" rows="2" class="input" />
          </div>
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="label">Statut</label>
              <select v-model="form.statut" class="input">
                <option value="actif">Actif</option>
                <option value="archive">Archivé</option>
                <option value="propose">Proposé</option>
              </select>
            </div>
            <div>
              <label class="label">Temps prépa (min)</label>
              <input v-model.number="form.temps_preparation" type="number" class="input" />
            </div>
            <div class="flex flex-col gap-2 pt-5">
              <label class="flex items-center gap-2 text-sm cursor-pointer">
                <input type="checkbox" v-model="form.est_secours" class="rounded" />
                Plat de secours
              </label>
              <label class="flex items-center gap-2 text-sm cursor-pointer">
                <input type="checkbox" v-model="form.est_obligatoire" class="rounded" />
                Toujours obligatoire
              </label>
            </div>
          </div>
          <!-- Saison -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label">Début saison (MM-JJ)</label>
              <input v-model="form.saison_debut" type="text" placeholder="ex: 06-01" class="input" />
            </div>
            <div>
              <label class="label">Fin saison (MM-JJ)</label>
              <input v-model="form.saison_fin" type="text" placeholder="ex: 08-31" class="input" />
            </div>
          </div>
          <!-- Disponibilités -->
          <div>
            <label class="label">Disponibilités</label>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <label v-for="dispo in dispoOpts" :key="dispo.key" class="flex items-center gap-1.5 text-xs cursor-pointer">
                <input type="checkbox" :value="dispo.key" v-model="form.disponibilites" class="rounded" />
                {{ dispo.label }}
              </label>
            </div>
          </div>
          <!-- Ingrédients du plat -->
          <div>
            <label class="label">Ingrédients du plat</label>
            <p class="text-xs text-gray-400 mb-2">Cochez <strong>⇅ Variant</strong> pour les ingrédients interchangeables (ex : Penne / Farfalle / Macaroni). Le planning choisira automatiquement par rotation.</p>
            <div class="space-y-2">
              <div v-for="(pi, idx) in form.plat_ingredients" :key="idx"
                :class="pi.est_variant ? 'bg-violet-50 border-violet-300' : 'bg-gray-50 border-gray-200'"
                class="flex flex-col gap-1 border rounded-lg p-2">
                <div class="flex items-center gap-2">
                  <IngredientCombobox
                    v-model="pi.ingredient"
                    :ingredients="ingredients"
                    placeholder="Rechercher un ingrédient…"
                    class="flex-1"
                  />
                  <label class="flex items-center gap-1 text-xs cursor-pointer whitespace-nowrap" :class="pi.est_variant ? 'text-violet-700 font-medium' : 'text-gray-500'">
                    <input type="checkbox" v-model="pi.est_variant" class="rounded accent-violet-600" />
                    ⇅ Variant
                  </label>
                </div>
                <div class="flex gap-2 items-center">
                  <input v-model.number="pi.quantite_par_portion" type="number" step="0.01" placeholder="Qté" class="input w-24 text-xs" />
                  <input v-model="pi.unite" placeholder="unité" class="input w-24 text-xs" />
                  <button @click="form.plat_ingredients.splice(idx, 1)" class="ml-auto text-red-400 hover:text-red-600 text-sm leading-none px-1">✕</button>
                </div>
              </div>
              <button @click="form.plat_ingredients.push({ ingredient: null, quantite_par_portion: null, unite: '', notes: '', est_variant: false })"
                class="text-xs text-emerald-600 hover:underline">+ Ajouter un ingrédient</button>
            </div>
          </div>
        </div>
        <div class="flex items-center justify-between gap-3 px-6 py-4 border-t">
          <div class="text-sm text-gray-500">
            Coût estimé :
            <span v-if="coutFormulaire !== null" class="font-semibold text-emerald-700">{{ coutFormulaire.toFixed(2) }} € / portion</span>
            <span v-else class="text-gray-300">aucun prix renseigné</span>
          </div>
          <div class="flex gap-3">
            <button @click="modal = false" class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">Annuler</button>
            <button @click="sauvegarder" :disabled="saving" class="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-emerald-700 disabled:opacity-50">
              {{ saving ? 'Sauvegarde…' : 'Sauvegarder' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useApi } from '~/composables/useApi'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const api = useApi()
const loading = ref(true)
const saving = ref(false)
const plats = ref<any[]>([])
const ingredients = ref<any[]>([])
const recherche = ref('')
const filtreSecours = ref('')
const modal = ref(false)
const editId = ref<number | null>(null)

const JOURS = ['lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche']
const JOURS_L = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
const dispoOpts = [
  ...JOURS.flatMap((j, i) => [
    { key: `${j}_midi`, label: `${JOURS_L[i]} midi` },
    { key: `${j}_soir`, label: `${JOURS_L[i]} soir` },
  ])
]

const emptyForm = () => ({
  nom: '', description: '', statut: 'actif',
  temps_preparation: null, est_secours: false, est_obligatoire: false,
  saison_debut: '', saison_fin: '', disponibilites: [] as string[],
  plat_ingredients: [] as any[],
})
const form = reactive(emptyForm())

const platsFiltres = computed(() => {
  return plats.value.filter(p => {
    const matchNom = !recherche.value || p.nom.toLowerCase().includes(recherche.value.toLowerCase())
    const matchSecours = filtreSecours.value === '' || String(p.est_secours) === filtreSecours.value
    return matchNom && matchSecours
  })
})

const coutFormulaire = computed<number | null>(() => {
  let total = 0
  let hasAny = false
  for (const pi of form.plat_ingredients) {
    const ing = ingredients.value.find(i => i.id === pi.ingredient)
    if (ing && ing.prix !== null && pi.quantite_par_portion) {
      total += Number(ing.prix) * pi.quantite_par_portion
      hasAny = true
    }
  }
  return hasAny ? Math.round(total * 100) / 100 : null
})

function statutClass(s: string) {
  if (s === 'actif') return 'bg-emerald-100 text-emerald-700'
  if (s === 'archive') return 'bg-gray-100 text-gray-500'
  return 'bg-yellow-100 text-yellow-700'
}

function ouvrirNouveau() {
  editId.value = null
  Object.assign(form, emptyForm())
  modal.value = true
}

async function ouvrirEdition(plat: any) {
  editId.value = plat.id
  const data: any = await api.get(`/plats/${plat.id}/`)
  const dispos = (data.disponibilites || []).map((d: any) => `${d.jour}_${d.creneau}`)
  const pis = (data.plat_ingredients || []).map((pi: any) => ({
    ingredient: pi.ingredient,
    quantite_par_portion: pi.quantite_par_portion,
    unite: pi.unite,
    notes: pi.notes || '',
    est_variant: pi.est_variant || false,
  }))
  Object.assign(form, {
    nom: data.nom, description: data.description || '',
    statut: data.statut, temps_preparation: data.temps_preparation,
    est_secours: data.est_secours, est_obligatoire: data.est_obligatoire,
    saison_debut: data.saison_debut || '', saison_fin: data.saison_fin || '',
    disponibilites: dispos, plat_ingredients: pis,
  })
  modal.value = true
}

async function sauvegarder() {
  saving.value = true
  try {
    const payload: any = {
      nom: form.nom, description: form.description,
      statut: form.statut, temps_preparation: form.temps_preparation || null,
      est_secours: form.est_secours, est_obligatoire: form.est_obligatoire,
      saison_debut: form.saison_debut || null, saison_fin: form.saison_fin || null,
      disponibilites: form.disponibilites.map(d => {
        const [jour, creneau] = d.split('_')
        return { jour, creneau }
      }),
      plat_ingredients: form.plat_ingredients.filter(pi => pi.ingredient),
    }
    if (editId.value) {
      await api.put(`/plats/${editId.value}/`, payload)
    } else {
      await api.post('/plats/', payload)
    }
    modal.value = false
    await charger()
  } catch (e: any) {
    alert('Erreur lors de la sauvegarde.')
  } finally {
    saving.value = false
  }
}

async function dupliquerPlat(plat: any) {
  editId.value = null
  const data: any = await api.get(`/plats/${plat.id}/`)
  const dispos = (data.disponibilites || []).map((d: any) => `${d.jour}_${d.creneau}`)
  const pis = (data.plat_ingredients || []).map((pi: any) => ({
    ingredient: pi.ingredient,
    quantite_par_portion: pi.quantite_par_portion,
    unite: pi.unite,
    notes: pi.notes || '',
    est_variant: pi.est_variant || false,
  }))
  Object.assign(form, {
    nom: `${plat.nom} (copie)`, description: data.description || '',
    statut: data.statut, temps_preparation: data.temps_preparation,
    est_secours: data.est_secours, est_obligatoire: data.est_obligatoire,
    famille: data.famille ?? null,
    saison_debut: data.saison_debut || '', saison_fin: data.saison_fin || '',
    disponibilites: dispos, plat_ingredients: pis,
  })
  modal.value = true
}

async function supprimerPlat(plat: any) {
  if (!confirm(`Supprimer « ${plat.nom} » ?`)) return
  await api.del(`/plats/${plat.id}/`)
  await charger()
}

async function charger() {
  loading.value = true
  try {
    const [platsData, ingsData] = await Promise.all([
      api.get<any>('/plats/'),
      api.get<any>('/ingredients/'),
    ])
    plats.value = Array.isArray(platsData) ? platsData : (platsData.results ?? [])
    ingredients.value = Array.isArray(ingsData) ? ingsData : (ingsData.results ?? [])
  } finally {
    loading.value = false
  }
}

onMounted(charger)
</script>

<style scoped>
.label { @apply block text-sm font-medium text-gray-700 mb-1; }
.input { @apply w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400; }
</style>

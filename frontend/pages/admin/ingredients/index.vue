<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold text-gray-800">Ingrédients</h1>
      <button @click="ouvrirNouveau" class="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-emerald-700">
        + Nouvel ingrédient
      </button>
    </div>

    <!-- Filtres -->
    <div class="flex flex-wrap gap-2">
      <input v-model="recherche" type="text" placeholder="Rechercher…" class="border rounded-lg px-3 py-1.5 text-sm w-48" />
      <select v-model="filtreCategorie" class="border rounded-lg px-3 py-1.5 text-sm">
        <option value="">Toutes les catégories</option>
        <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.nom }}</option>
      </select>
    </div>

    <div class="bg-white rounded-2xl shadow overflow-hidden">
      <div v-if="loading" class="text-center py-12 text-gray-400">Chargement…</div>
      <table v-else class="min-w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Catégorie</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Unité</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Prix</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Options</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="ing in ingredientsFiltres" :key="ing.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-sm text-gray-800">{{ ing.nom }}</td>
            <td class="px-4 py-3 text-sm text-gray-600 hidden sm:table-cell">
              {{ categorieNom(ing.categorie) }}
            </td>
            <td class="px-4 py-3 text-sm text-gray-600 hidden md:table-cell">{{ ing.unite || '—' }}</td>
            <td class="px-4 py-3 text-sm text-right hidden md:table-cell">
              <span v-if="ing.prix !== null" class="font-medium text-gray-700">{{ Number(ing.prix).toFixed(2) }} €</span>
              <span v-else class="text-gray-300">—</span>
            </td>
            <td class="px-4 py-3 text-sm text-gray-500 hidden md:table-cell space-x-2">
              <span v-if="ing.achat_systematique" class="px-1.5 py-0.5 bg-blue-100 text-blue-600 rounded text-xs">🔁 Systématique</span>
              <span v-else-if="ing.en_plat" class="px-1.5 py-0.5 bg-emerald-100 text-emerald-700 rounded text-xs">🍽 Associé à un plat</span>
              <span v-else class="px-1.5 py-0.5 bg-gray-100 text-gray-500 rounded text-xs">🛋 Divers</span>
              <a v-if="ing.url_produit" :href="ing.url_produit" target="_blank" rel="noopener noreferrer" class="px-1.5 py-0.5 bg-gray-100 text-gray-500 rounded text-xs hover:underline">🔗 URL</a>
            </td>
            <td class="px-4 py-3 text-right">
              <button @click="ouvrirEdition(ing)" class="text-xs text-emerald-600 hover:underline mr-3">Modifier</button>
              <button @click="supprimer(ing)" class="text-xs text-red-500 hover:underline">Supprimer</button>
            </td>
          </tr>
          <tr v-if="ingredientsFiltres.length === 0">
            <td colspan="6" class="px-4 py-8 text-center text-gray-400 text-sm">Aucun ingrédient trouvé.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="modal" class="fixed inset-0 z-50 flex items-center justify-center p-4" style="background:rgba(0,0,0,0.5)">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md">
        <div class="flex items-center justify-between px-6 py-4 border-b">
          <h2 class="font-semibold text-gray-800">{{ editId ? 'Modifier' : 'Nouvel ingrédient' }}</h2>
          <button @click="modal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div class="px-6 py-4 space-y-4">
          <div>
            <label class="label">Nom *</label>
            <input v-model="form.nom" type="text" required class="input" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label">Catégorie</label>
              <select v-model="form.categorie" class="input">
                <option value="">—</option>
                <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.nom }}</option>
              </select>
            </div>
            <div>
              <label class="label">Unité par défaut</label>
              <input v-model="form.unite" type="text" placeholder="kg, L, pièce…" class="input" />
            </div>
          </div>
          <div>
            <label class="label">URL produit en ligne</label>
            <input v-model="form.url_produit" type="url" class="input" />
          </div>
          <div>
            <label class="label">Prix unitaire (€)</label>
            <input v-model.number="form.prix" type="number" min="0" step="0.01" placeholder="ex : 2.49" class="input" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="flex items-center gap-2 cursor-pointer text-sm">
              <input type="checkbox" v-model="form.achat_systematique" class="rounded" />
              Achat systématique (toujours dans la liste de courses)
            </label>
          </div>
          <div v-if="error" class="text-sm text-red-600">{{ error }}</div>
        </div>
        <div class="flex justify-end gap-3 px-6 py-4 border-t">
          <button @click="modal = false" class="px-4 py-2 text-sm text-gray-600">Annuler</button>
          <button @click="sauvegarder" :disabled="saving" class="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm disabled:opacity-50">
            {{ saving ? 'Sauvegarde…' : 'Sauvegarder' }}
          </button>
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
const ingredients = ref<any[]>([])
const categories = ref<any[]>([])
const recherche = ref('')
const filtreCategorie = ref<number | ''>('')
const modal = ref(false)
const editId = ref<number | null>(null)
const error = ref('')

const emptyForm = () => ({ nom: '', categorie: '' as any, unite: '', url_produit: '', prix: null as number | null, achat_systematique: false })
const form = reactive(emptyForm())

const ingredientsFiltres = computed(() => ingredients.value.filter(i => {
  const matchNom = !recherche.value || i.nom.toLowerCase().includes(recherche.value.toLowerCase())
  const matchCat = filtreCategorie.value === '' || i.categorie === filtreCategorie.value
  return matchNom && matchCat
}))

function categorieNom(id: number) {
  return categories.value.find(c => c.id === id)?.nom || '—'
}

function ouvrirNouveau() {
  editId.value = null
  Object.assign(form, emptyForm())
  error.value = ''
  modal.value = true
}

function ouvrirEdition(ing: any) {
  editId.value = ing.id
  Object.assign(form, { nom: ing.nom, categorie: ing.categorie || '', unite: ing.unite || '', url_produit: ing.url_produit || '', prix: ing.prix !== null ? Number(ing.prix) : null, achat_systematique: ing.achat_systematique })
  error.value = ''
  modal.value = true
}

async function sauvegarder() {
  saving.value = true
  error.value = ''
  try {
    const payload = { nom: form.nom, categorie: form.categorie || null, unite: form.unite, url_produit: form.url_produit || null, prix: form.prix ?? null, achat_systematique: form.achat_systematique }
    if (editId.value) {
      await api.put(`/ingredients/${editId.value}/`, payload)
    } else {
      await api.post('/ingredients/', payload)
    }
    modal.value = false
    await charger()
  } catch {
    error.value = 'Erreur lors de la sauvegarde.'
  } finally {
    saving.value = false
  }
}

async function supprimer(ing: any) {
  if (!confirm(`Supprimer « ${ing.nom} » ?`)) return
  await api.del(`/ingredients/${ing.id}/`)
  await charger()
}

async function charger() {
  loading.value = true
  try {
    const [ingsData, catsData] = await Promise.all([api.get<any>('/ingredients/'), api.get<any>('/categories-ingredients/')])
    ingredients.value = Array.isArray(ingsData) ? ingsData : (ingsData.results ?? [])
    categories.value = Array.isArray(catsData) ? catsData : (catsData.results ?? [])
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

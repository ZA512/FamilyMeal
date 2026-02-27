<template>
  <div class="space-y-6">
    <h1 class="text-xl font-bold text-gray-800">Outils</h1>

    <!-- ─── Section Import Coursesu ───────────────────────────────────── -->
    <div class="bg-white rounded-2xl shadow p-6 space-y-5">
      <h2 class="text-lg font-semibold text-gray-700">🛒 Import Coursesu — favoris</h2>

      <!-- Étape : choix de la méthode -->
      <div v-if="etape === 'methode'" class="space-y-4">
        <p class="text-sm text-gray-500">
          Choisissez comment récupérer votre liste de favoris :
        </p>
        <div class="grid sm:grid-cols-2 gap-4">
          <!-- Connexion directe — non disponible -->
          <div class="flex flex-col items-start gap-2 rounded-xl border-2 border-gray-200 p-5 text-left opacity-50 cursor-not-allowed select-none">
            <span class="text-2xl">🔗</span>
            <span class="font-semibold text-gray-800 text-sm">Connexion directe</span>
            <span class="text-xs text-gray-500">
              Non disponible — coursesu.com protège sa page de connexion avec un CAPTCHA Cloudflare qui bloque toute automatisation.
            </span>
            <span class="text-xs text-red-500">✗ Indisponible</span>
          </div>

          <!-- Import HAR -->
          <button
            @click="etape = 'upload'"
            class="flex flex-col items-start gap-2 rounded-xl border-2 border-gray-200 p-5 text-left transition-colors hover:border-emerald-400"
          >
            <span class="text-2xl">📂</span>
            <span class="font-semibold text-gray-800 text-sm">Import fichier HAR</span>
            <span class="text-xs text-gray-500">
              Exportez les requêtes de votre navigateur (F12 › Réseau › Exporter HAR)
              et importez le fichier ici.
            </span>
          </button>
        </div>
        <p v-if="erreur" class="text-red-600 text-sm">{{ erreur }}</p>
      </div>

      <!-- Étape : upload HAR -->
      <div v-if="etape === 'upload'" class="space-y-3">
        <label
          class="flex flex-col items-center justify-center w-full border-2 border-dashed border-gray-300 rounded-xl p-8 cursor-pointer hover:border-emerald-400 transition-colors"
          @dragover.prevent
          @drop.prevent="onDrop"
        >
          <span class="text-4xl mb-2">📂</span>
          <span class="text-sm text-gray-500">
            Glissez votre fichier <code>.har</code> ici, ou cliquez pour parcourir
          </span>
          <input type="file" accept=".har,application/json" class="hidden" @change="onFileChange" />
        </label>
        <button @click="etape = 'methode'" class="text-sm text-gray-500 underline hover:text-gray-700">← Retour</button>
        <p v-if="erreur" class="text-red-600 text-sm">{{ erreur }}</p>
      </div>

      <!-- Chargement -->
      <div v-if="etape === 'chargement'" class="text-center py-10 text-gray-400">
        <div class="inline-block animate-spin text-3xl mb-3">⚙️</div>
        <p>Analyse du fichier HAR…</p>
        <p class="text-xs mt-1">Cela peut prendre quelques secondes.</p>
      </div>

      <!-- Aucun nouveau produit -->
      <div v-if="etape === 'vide'" class="space-y-3">
        <div class="bg-blue-50 border border-blue-200 rounded-xl p-5 text-sm text-blue-800">
          ℹ️ Tous vos favoris coursesu ({{ totalTrouves }}) sont déjà présents dans votre liste d'ingrédients.
        </div>
        <button @click="reinitialiser" class="text-sm text-gray-500 underline hover:text-gray-700">← Recommencer</button>
      </div>

      <!-- Sélection des produits -->
      <div v-if="etape === 'selection'" class="space-y-4">
        <div class="flex items-center justify-between gap-3 flex-wrap">
          <span class="text-sm text-gray-600">
            <strong>{{ produits.length }}</strong> nouveau(x) —
            <strong class="text-gray-400">{{ dejaImportes }}</strong> déjà importé(s) ignoré(s) —
            <strong class="text-emerald-600">{{ selectionnes }}</strong> sélectionné(s)
          </span>
          <div class="flex gap-2 flex-wrap">
            <input v-model="recherche" type="text" placeholder="Filtrer…" class="border rounded-lg px-3 py-1.5 text-sm w-44" />
            <button @click="toutCocher(true)" class="text-xs px-3 py-1.5 rounded-lg border border-gray-300 hover:bg-gray-50">Tout cocher</button>
            <button @click="toutCocher(false)" class="text-xs px-3 py-1.5 rounded-lg border border-gray-300 hover:bg-gray-50">Tout décocher</button>
            <button @click="reinitialiser" class="text-xs px-3 py-1.5 rounded-lg border border-gray-300 hover:bg-gray-50">↩ Recommencer</button>
          </div>
        </div>

        <div class="overflow-x-auto rounded-xl border">
          <table class="min-w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-3 py-2 w-8">
                  <input type="checkbox"
                    @change="toutCocher(($event.target as HTMLInputElement).checked)"
                    :checked="selectionnes === produitsFiltres.length && selectionnes > 0"
                  />
                </th>
                <th class="px-3 py-2 w-16 text-left text-xs text-gray-500 uppercase">Image</th>
                <th class="px-3 py-2 text-left text-xs text-gray-500 uppercase">Nom (modifiable)</th>
                <th class="px-3 py-2 w-36 text-center text-xs text-gray-500 uppercase hidden sm:table-cell">Achat systématique</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="p in produitsFiltres" :key="p.external_id" :class="p.selected ? '' : 'opacity-40'">
                <td class="px-3 py-2 text-center"><input type="checkbox" v-model="p.selected" /></td>
                <td class="px-3 py-2">
                  <img v-if="p.image_url" :src="p.image_url" :alt="p.name"
                    class="w-12 h-12 object-contain rounded"
                    @error="(e) => ((e.target as HTMLImageElement).style.display = 'none')"
                  />
                  <span v-else class="text-gray-300 text-xl">🖼️</span>
                </td>
                <td class="px-3 py-2">
                  <input v-model="p.name" type="text"
                    class="w-full border border-transparent hover:border-gray-300 focus:border-emerald-400 rounded px-2 py-1 text-sm focus:outline-none transition-colors"
                  />
                </td>
                <td class="px-3 py-2 text-center hidden sm:table-cell">
                  <input type="checkbox" v-model="p.achat_systematique" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <p v-if="erreur" class="text-red-600 text-sm">{{ erreur }}</p>

        <button
          @click="importer"
          :disabled="selectionnes === 0 || importing"
          class="bg-emerald-600 text-white px-6 py-2 rounded-lg text-sm hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ importing ? 'Import en cours…' : `Importer ${selectionnes} ingrédient(s)` }}
        </button>
      </div>

      <!-- Résultat -->
      <div v-if="etape === 'resultat'" class="space-y-4">
        <div class="bg-emerald-50 border border-emerald-200 rounded-xl p-5 space-y-2">
          <p class="text-emerald-800 font-semibold">✅ Import terminé !</p>
          <ul class="text-sm text-emerald-700 space-y-1">
            <li>🆕 <strong>{{ resultat.created }}</strong> ingrédient(s) créé(s)</li>
            <li>⏭️ <strong>{{ resultat.skipped }}</strong> déjà existant(s) (ignoré(s))</li>
          </ul>
          <div v-if="resultat.created_names.length" class="mt-3 text-xs text-emerald-600 max-h-32 overflow-y-auto border-t border-emerald-200 pt-2">
            <p v-for="n in resultat.created_names" :key="n" class="leading-tight">{{ n }}</p>
          </div>
        </div>
        <button @click="reinitialiser" class="text-sm text-gray-600 underline hover:text-gray-900">
          ↩ Refaire un import
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { useApi } from '~/composables/useApi'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const config = useRuntimeConfig()
const auth = useAuthStore()
const api = useApi()

type Produit = {
  external_id: string
  name: string
  image_url: string
  product_url: string
  achat_systematique: boolean
  selected: boolean
}

type Etape = 'methode' | 'upload' | 'chargement' | 'selection' | 'vide' | 'resultat'

const etape = ref<Etape>('methode')
const produits = ref<Produit[]>([])
const recherche = ref('')
const erreur = ref('')
const scraping = ref(false)
const importing = ref(false)
const dejaImportes = ref(0)
const totalTrouves = ref(0)
const resultat = ref({ created: 0, skipped: 0, created_names: [] as string[] })

const produitsFiltres = computed(() => {
  const q = recherche.value.toLowerCase()
  if (!q) return produits.value
  return produits.value.filter(p => p.name.toLowerCase().includes(q))
})

const selectionnes = computed(() => produits.value.filter(p => p.selected).length)

function toutCocher(val: boolean) {
  produitsFiltres.value.forEach(p => { p.selected = val })
}

function reinitialiser() {
  etape.value = 'methode'
  produits.value = []
  recherche.value = ''
  erreur.value = ''
  dejaImportes.value = 0
  totalTrouves.value = 0
  resultat.value = { created: 0, skipped: 0, created_names: [] }
}

function appliquerProduits(data: { products: Omit<Produit, 'selected' | 'achat_systematique'>[], count: number, total?: number, already_imported?: number }) {
  totalTrouves.value = data.total ?? data.count
  dejaImportes.value = data.already_imported ?? 0
  if (data.count === 0) {
    etape.value = 'vide'
    return
  }
  produits.value = data.products.map(p => ({ ...p, achat_systematique: false, selected: true }))
  etape.value = 'selection'
}


function onFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) analyserFichier(file)
}

function onDrop(e: DragEvent) {
  const file = e.dataTransfer?.files?.[0]
  if (file) analyserFichier(file)
}

async function analyserFichier(file: File) {
  erreur.value = ''
  etape.value = 'chargement'
  const formData = new FormData()
  formData.append('har', file)
  try {
    const res = await fetch(`${config.public.apiBase}/tools/parse-har/`, {
      method: 'POST',
      headers: { ...auth.authHeader },
      body: formData,
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: `Erreur ${res.status}` }))
      throw new Error(err.detail || JSON.stringify(err))
    }
    const data = await res.json()
    appliquerProduits(data)
  } catch (e: unknown) {
    erreur.value = (e as Error).message
    etape.value = 'upload'
  }
}

// ── Import en base ─────────────────────────────────────────────────
async function importer() {
  erreur.value = ''
  importing.value = true
  const items = produits.value
    .filter(p => p.selected && p.name.trim())
    .map(p => ({
      name: p.name.trim(),
      image_url: p.image_url,
      product_url: p.product_url,
      achat_systematique: p.achat_systematique,
    }))
  try {
    const data = await api.post<any>('/tools/import-ingredients/', { items })
    resultat.value = data
    etape.value = 'resultat'
  } catch (e: unknown) {
    erreur.value = (e as Error).message
  } finally {
    importing.value = false
  }
}


</script>

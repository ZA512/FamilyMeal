<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold text-gray-800">Membres</h1>
      <button @click="ouvrirNouveau" class="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-emerald-700">
        + Nouveau membre
      </button>
    </div>

    <div class="bg-white rounded-2xl shadow overflow-hidden">
      <div v-if="loading" class="text-center py-12 text-gray-400">Chargement…</div>
      <table v-else class="min-w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Membre</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Téléphone</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Naissance</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Actif</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="m in membres" :key="m.id" class="hover:bg-gray-50">
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <span
                  class="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0"
                  :style="{ backgroundColor: m.couleur || '#6b7280' }"
                >{{ m.prenom.charAt(0).toUpperCase() }}</span>
                <span class="font-medium text-sm">{{ m.prenom }}</span>
              </div>
            </td>
            <td class="px-4 py-3 text-sm text-gray-600 hidden sm:table-cell">{{ m.telephone || '—' }}</td>
            <td class="px-4 py-3 text-sm text-gray-600 hidden md:table-cell">{{ m.annee_naissance ?? '—' }}</td>
            <td class="px-4 py-3 hidden md:table-cell">
              <span class="px-2 py-0.5 rounded-full text-xs" :class="m.actif ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-500'">
                {{ m.actif ? 'Actif' : 'Inactif' }}
              </span>
            </td>
            <td class="px-4 py-3 text-right">
              <button @click="ouvrirEdition(m)" class="text-xs text-emerald-600 hover:underline mr-3">Modifier</button>
              <button @click="supprimer(m)" class="text-xs text-red-500 hover:underline">Supprimer</button>
            </td>
          </tr>
          <tr v-if="membres.length === 0">
            <td colspan="5" class="px-4 py-8 text-center text-gray-400 text-sm">Aucun membre.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="modal" class="fixed inset-0 z-50 flex items-center justify-center p-4" style="background:rgba(0,0,0,0.5)">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md">
        <div class="flex items-center justify-between px-6 py-4 border-b">
          <h2 class="font-semibold text-gray-800">{{ editId ? 'Modifier' : 'Nouveau membre' }}</h2>
          <button @click="modal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div class="px-6 py-4 space-y-4">
          <div>
            <label class="label">Prénom *</label>
            <input v-model="form.prenom" type="text" required class="input" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label">Année de naissance</label>
              <input v-model.number="form.annee_naissance" type="number" min="1900" :max="new Date().getFullYear()" class="input" />
            </div>
            <div>
              <label class="label">Couleur</label>
              <input v-model="form.couleur" type="color" class="w-full h-10 rounded-lg border border-gray-300" />
            </div>
          </div>
          <div>
            <label class="label">Téléphone (SMS)</label>
            <input v-model="form.telephone" type="tel" placeholder="ex: +33612345678" class="input" />
          </div>
          <label class="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" v-model="form.actif" class="rounded" />
            <span class="text-sm text-gray-700">Membre actif</span>
          </label>
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
const membres = ref<any[]>([])
const modal = ref(false)
const editId = ref<number | null>(null)
const error = ref('')

const emptyForm = () => ({ prenom: '', annee_naissance: null as number | null, couleur: '#10b981', telephone: '', actif: true })
const form = reactive(emptyForm())

function ouvrirNouveau() {
  editId.value = null
  Object.assign(form, emptyForm())
  error.value = ''
  modal.value = true
}

function ouvrirEdition(m: any) {
  editId.value = m.id
  Object.assign(form, { prenom: m.prenom, annee_naissance: m.annee_naissance, couleur: m.couleur || '#10b981', telephone: m.telephone || '', actif: m.actif })
  error.value = ''
  modal.value = true
}

async function sauvegarder() {
  saving.value = true
  error.value = ''
  try {
    const payload = { prenom: form.prenom, annee_naissance: form.annee_naissance || null, couleur: form.couleur, telephone: form.telephone || '', actif: form.actif }
    if (editId.value) {
      await api.put(`/membres/${editId.value}/`, payload)
    } else {
      await api.post('/membres/', payload)
    }
    modal.value = false
    await charger()
  } catch {
    error.value = 'Erreur lors de la sauvegarde.'
  } finally {
    saving.value = false
  }
}

async function supprimer(m: any) {
  if (!confirm(`Supprimer ${m.prenom} ?`)) return
  await api.del(`/membres/${m.id}/`)
  await charger()
}

async function charger() {
  loading.value = true
  try {
    const data = await api.get<any>('/membres/')
    membres.value = Array.isArray(data) ? data : (data.results ?? [])
  } finally { loading.value = false }
}

onMounted(charger)
</script>

<style scoped>
.label { @apply block text-sm font-medium text-gray-700 mb-1; }
.input { @apply w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400; }
</style>

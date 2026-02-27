<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold text-gray-800">Demandes</h1>
      <select v-model="filtre" @change="charger" class="border rounded-lg px-3 py-1.5 text-sm">
        <option value="en_attente">En attente</option>
        <option value="validee">Validées</option>
        <option value="refusee">Refusées</option>
        <option value="">Toutes</option>
      </select>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">Chargement…</div>

    <div v-else-if="demandes.length === 0" class="text-center py-12 text-gray-400">
      <div class="text-4xl mb-2">📬</div>
      <p>Aucune demande {{ filtre === 'en_attente' ? 'en attente' : '' }}.</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="d in demandes"
        :key="d.id"
        class="bg-white rounded-2xl shadow p-5"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1 min-w-0">
            <!-- En-tête demande -->
            <div class="flex items-center gap-2 mb-1 flex-wrap">
              <span
                class="w-6 h-6 rounded-full text-white flex items-center justify-center text-xs font-bold flex-shrink-0"
                :style="{ backgroundColor: d.membre_couleur || '#6b7280' }"
              >{{ d.membre_prenom?.charAt(0).toUpperCase() }}</span>
              <span class="font-semibold text-gray-800">{{ d.membre_prenom }}</span>
              <span class="text-gray-400">•</span>
              <span class="text-xs text-gray-500">{{ typeLabel(d.type) }}</span>
              <span class="px-2 py-0.5 rounded-full text-xs font-medium ml-auto" :class="statutClass(d.statut)">
                {{ d.statut }}
              </span>
            </div>

            <!-- Contenu demande préférence -->
            <div v-if="d.type === 'preference'" class="mt-2 text-sm text-gray-700">
              Plat : <span class="font-medium">{{ d.plat_nom }}</span>
              <span class="mx-2">·</span>
              <span>{{ noteLabel(d.ancienne_note) }}</span>
              <span class="mx-2 text-gray-400">→</span>
              <span class="font-medium" :class="noteColor(d.nouvelle_note)">{{ noteLabel(d.nouvelle_note) }}</span>
            </div>

            <!-- Contenu demande nouveau plat -->
            <div v-else-if="d.type === 'nouveau_plat'" class="mt-2 text-sm text-gray-700">
              <div v-if="d.data_json?.nom">Nouveau plat suggéré : <span class="font-medium">{{ d.data_json.nom }}</span></div>
              <div v-if="d.data_json?.description" class="text-gray-500 mt-0.5">{{ d.data_json.description }}</div>
            </div>

            <!-- Message membre -->
            <div v-if="d.message_membre" class="mt-2 p-2 bg-gray-50 rounded text-sm text-gray-600 italic">
              « {{ d.message_membre }} »
            </div>

            <!-- Message admin (si déjà traité) -->
            <div v-if="d.message_admin" class="mt-2 text-xs text-gray-400">
              Réponse admin : {{ d.message_admin }}
            </div>
          </div>
        </div>

        <!-- Actions (seulement pour les demandes en attente) -->
        <div v-if="d.statut === 'en_attente'" class="flex items-center gap-3 mt-4 pt-3 border-t border-gray-100">
          <input
            v-model="messagesAdmin[d.id]"
            type="text"
            placeholder="Message (optionnel)"
            class="flex-1 border rounded-lg px-3 py-1.5 text-sm"
          />
          <button
            @click="valider(d)"
            :disabled="actionLoading === d.id"
            class="bg-emerald-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-emerald-700 disabled:opacity-50"
          >✓ Valider</button>
          <button
            @click="refuser(d)"
            :disabled="actionLoading === d.id"
            class="bg-red-500 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-red-600 disabled:opacity-50"
          >✕ Refuser</button>
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
const demandes = ref<any[]>([])
const filtre = ref('en_attente')
const actionLoading = ref<number | null>(null)
const messagesAdmin: Record<number, string> = reactive({})

function typeLabel(t: string) {
  if (t === 'preference') return 'Changement de préférence'
  if (t === 'nouveau_plat') return 'Nouveau plat'
  return t
}

function noteLabel(n: string) {
  if (n === 'aime') return '😍 J\'aime'
  if (n === 'neutre') return '😐 Neutre'
  if (n === 'deteste') return '😒 Je n\'aime pas'
  return n || '—'
}

function noteColor(n: string) {
  if (n === 'aime') return 'text-emerald-600'
  if (n === 'deteste') return 'text-red-500'
  return 'text-gray-600'
}

function statutClass(s: string) {
  if (s === 'en_attente') return 'bg-yellow-100 text-yellow-700'
  if (s === 'validee') return 'bg-emerald-100 text-emerald-700'
  return 'bg-red-100 text-red-600'
}

async function charger() {
  loading.value = true
  try {
    const url = filtre.value ? `/demandes/?statut=${filtre.value}` : '/demandes/'
    const data = await api.get<any>(url)
    demandes.value = Array.isArray(data) ? data : (data.results ?? [])
  } finally {
    loading.value = false
  }
}

async function valider(d: any) {
  actionLoading.value = d.id
  try {
    await api.post(`/demandes/${d.id}/valider/`, { message_admin: messagesAdmin[d.id] || '' })
    await charger()
  } finally {
    actionLoading.value = null
  }
}

async function refuser(d: any) {
  actionLoading.value = d.id
  try {
    await api.post(`/demandes/${d.id}/refuser/`, { message_admin: messagesAdmin[d.id] || '' })
    await charger()
  } finally {
    actionLoading.value = null
  }
}

onMounted(charger)
</script>

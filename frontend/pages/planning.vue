<template>
  <div class="space-y-4">
    <!-- Navigation semaine -->
    <div class="flex items-center justify-between">
      <button @click="semainePrecedente" class="px-3 py-1.5 bg-white rounded-lg shadow text-sm hover:bg-gray-50">
        ← Semaine précédente
      </button>
      <h2 class="font-semibold text-gray-800 text-sm sm:text-base">
        {{ labelSemaine }}
      </h2>
      <button @click="semaineSuivante" class="px-3 py-1.5 bg-white rounded-lg shadow text-sm hover:bg-gray-50">
        Semaine suivante →
      </button>
    </div>

    <!-- Chargement -->
    <div v-if="loading" class="text-center py-16 text-gray-400">Chargement…</div>

    <!-- Pas de planning publié -->
    <div v-else-if="!semaine" class="text-center py-16 text-gray-400">
      <div class="text-4xl mb-3">📅</div>
      <p>Aucun planning publié pour cette semaine.</p>
    </div>

    <!-- Grille planning -->
    <div v-else class="overflow-x-auto">
      <table class="min-w-full bg-white rounded-2xl shadow overflow-hidden">
        <thead>
          <tr class="bg-emerald-50">
            <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide w-16"></th>
            <th
              v-for="jour in jours"
              :key="jour.date"
              class="px-3 py-3 text-center text-xs font-medium uppercase tracking-wide"
              :class="isAujourdHui(jour.date) ? 'text-emerald-700 bg-emerald-100' : 'text-gray-500'"
            >
              <div>{{ jour.nomCourt }}</div>
              <div class="font-bold text-sm">{{ jour.numero }}</div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="creneau in creneaux" :key="creneau" class="border-t border-gray-100">
            <td class="px-3 py-2 text-xs font-semibold text-gray-400 uppercase">
              {{ creneau === 'midi' ? '🌞 Midi' : '🌙 Soir' }}
            </td>
            <td
              v-for="jour in jours"
              :key="jour.date"
              class="px-2 py-2 align-top text-center border-l border-gray-100"
              :class="isAujourdHui(jour.date) ? 'bg-emerald-50' : ''"
            >
              <div v-if="getCreneauPlanning(jour.date, creneau) as cp">
                <!-- Plat principal -->
                <div class="text-sm font-semibold text-gray-800 leading-tight">
                  {{ cp.plat_principal?.nom || '—' }}
                </div>
                <!-- Photo miniature -->
                <img
                  v-if="cp.plat_principal?.photo"
                  :src="cp.plat_principal.photo"
                  alt=""
                  class="w-12 h-12 object-cover rounded-lg mx-auto mt-1 mb-1"
                />
                <!-- Plat de secours -->
                <div v-if="cp.plat_secours" class="mt-1 rounded-lg px-1 py-0.5 text-xs text-white" style="background:#6b7280">
                  <div class="font-medium">{{ cp.plat_secours.nom }}</div>
                  <div v-if="cp.membres_secours?.length" class="flex flex-wrap gap-0.5 justify-center mt-0.5">
                    <span
                      v-for="m in cp.membres_secours"
                      :key="m.id"
                      class="rounded-full w-4 h-4 inline-flex items-center justify-center text-white font-bold text-xs"
                      :style="{ backgroundColor: m.couleur || '#9ca3af' }"
                      :title="m.prenom"
                    >{{ m.prenom.charAt(0) }}</span>
                  </div>
                </div>
              </div>
              <div v-else class="text-gray-300 text-xs py-2">—</div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Bouton proposer une préférence -->
    <div class="text-right">
      <button
        @click="proposerPreference = !proposerPreference"
        class="text-sm text-emerald-600 hover:underline"
      >
        Proposer une modification de préférence
      </button>
    </div>

    <!-- Formulaire proposition préférence -->
    <div v-if="proposerPreference" class="bg-white rounded-2xl shadow p-5 space-y-4">
      <h3 class="font-semibold text-gray-800">Proposer une modification</h3>
      <div>
        <label class="block text-sm text-gray-600 mb-1">Plat</label>
        <select v-model="prefForm.plat_id" class="w-full border rounded-lg px-3 py-2 text-sm">
          <option value="" disabled>-- Sélectionner un plat --</option>
          <option v-for="p in plats" :key="p.id" :value="p.id">{{ p.nom }}</option>
        </select>
      </div>
      <div>
        <label class="block text-sm text-gray-600 mb-1">Nouvelle note</label>
        <div class="flex gap-3">
          <label v-for="opt in notesOpts" :key="opt.value" class="flex items-center gap-1 cursor-pointer">
            <input type="radio" v-model="prefForm.nouvelle_note" :value="opt.value" />
            <span class="text-sm">{{ opt.label }}</span>
          </label>
        </div>
      </div>
      <div>
        <label class="block text-sm text-gray-600 mb-1">Message (optionnel)</label>
        <textarea v-model="prefForm.message" rows="2" class="w-full border rounded-lg px-3 py-2 text-sm" />
      </div>
      <div v-if="prefError" class="text-sm text-red-600">{{ prefError }}</div>
      <div v-if="prefSuccess" class="text-sm text-emerald-600">✓ Demande envoyée, en attente de validation.</div>
      <button
        @click="envoyerPref"
        :disabled="prefLoading || !prefForm.plat_id || !prefForm.nouvelle_note"
        class="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-emerald-700 disabled:opacity-50"
      >
        {{ prefLoading ? 'Envoi…' : 'Envoyer' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
import 'dayjs/locale/fr'
import { useAuthStore } from '~/stores/auth'
import { useApi } from '~/composables/useApi'

definePageMeta({ middleware: 'reader' })

dayjs.locale('fr')

const auth = useAuthStore()
const api = useApi()

const loading = ref(true)
const semaine = ref<any>(null)
const plats = ref<any[]>([])
const offsetSemaine = ref(0) // 0 = semaine courante, -1 = précédente, etc.
const toutes = ref<any[]>([])

const creneaux = ['midi', 'soir']
const JOURS = ['lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche']
const JOURS_COURTS = ['Lun','Mar','Mer','Jeu','Ven','Sam','Dim']

const jours = computed(() => {
  if (!semaine.value) return []
  const debut = dayjs(semaine.value.date_debut)
  return Array.from({ length: 7 }, (_, i) => {
    const d = debut.add(i, 'day')
    return { date: d.format('YYYY-MM-DD'), nomCourt: JOURS_COURTS[i], numero: d.format('D') }
  })
})

const labelSemaine = computed(() => {
  if (!semaine.value) return 'Semaine non disponible'
  const debut = dayjs(semaine.value.date_debut)
  return `Semaine du ${debut.format('D MMMM YYYY')}`
})

function isAujourdHui(date: string) {
  return date === dayjs().format('YYYY-MM-DD')
}

function getCreneauPlanning(date: string, creneau: string) {
  if (!semaine.value?.creneaux) return null
  return semaine.value.creneaux.find((c: any) => c.date === date && c.creneau === creneau) || null
}

async function chargerSemaines() {
  loading.value = true
  try {
    const data = await api.get('/semaines/')
    toutes.value = data.sort((a: any, b: any) => a.date_debut.localeCompare(b.date_debut))
    // Indice courant : semaine la plus proche d'aujourd'hui
    const aujourd = dayjs().format('YYYY-MM-DD')
    let idx = toutes.value.findIndex((s: any) => s.date_debut > aujourd)
    if (idx === -1) idx = toutes.value.length - 1
    else if (idx > 0) idx -= 1
    currentIdx.value = idx + offsetSemaine.value
    await chargerSemaine()
  } catch (e) {
    semaine.value = null
  } finally {
    loading.value = false
  }
}

const currentIdx = ref(0)

async function chargerSemaine() {
  loading.value = true
  try {
    if (toutes.value.length === 0) { semaine.value = null; return }
    const idx = Math.max(0, Math.min(currentIdx.value, toutes.value.length - 1))
    const s = toutes.value[idx]
    if (!s) { semaine.value = null; return }
    const detail = await api.get(`/semaines/${s.id}/`)
    semaine.value = detail
  } catch {
    semaine.value = null
  } finally {
    loading.value = false
  }
}

async function semainePrecedente() {
  if (currentIdx.value > 0) { currentIdx.value--; await chargerSemaine() }
}
async function semaineSuivante() {
  if (currentIdx.value < toutes.value.length - 1) { currentIdx.value++; await chargerSemaine() }
}

// Proposition préférence
const proposerPreference = ref(false)
const prefForm = reactive({ plat_id: '', nouvelle_note: '', message: '' })
const prefLoading = ref(false)
const prefError = ref('')
const prefSuccess = ref(false)
const notesOpts = [
  { value: 'aime', label: '😍 J\'aime' },
  { value: 'neutre', label: '😐 Neutre' },
  { value: 'deteste', label: '😒 Je n\'aime pas' },
]

async function envoyerPref() {
  prefLoading.value = true
  prefError.value = ''
  prefSuccess.value = false
  try {
    await api.post(`/preferences/proposer_modification/`, {
      plat: prefForm.plat_id,
      nouvelle_note: prefForm.nouvelle_note,
      message: prefForm.message,
    })
    prefSuccess.value = true
    prefForm.plat_id = ''
    prefForm.nouvelle_note = ''
    prefForm.message = ''
  } catch (e: any) {
    prefError.value = 'Erreur lors de l\'envoi de la demande.'
  } finally {
    prefLoading.value = false
  }
}

onMounted(async () => {
  await chargerSemaines()
  try {
    plats.value = await api.get('/plats/')
  } catch {}
})
</script>

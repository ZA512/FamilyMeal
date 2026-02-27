<template>
  <div class="space-y-6">
    <h1 class="text-xl font-bold text-gray-800">Paramètres</h1>

    <div v-if="loading" class="text-center py-12 text-gray-400">Chargement…</div>

    <form v-else @submit.prevent="sauvegarder" class="space-y-6">
      <!-- Planning -->
      <div class="bg-white rounded-2xl shadow p-6 space-y-4">
        <h2 class="font-semibold text-gray-700">Planning</h2>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <label class="label">Jour de début de semaine</label>
            <select v-model="form.jour_debut_semaine" class="input">
              <option v-for="(j, k) in jourOptions" :key="k" :value="k">{{ j }}</option>
            </select>
          </div>
          <div>
            <label class="label">Intervalle min entre plats (jours)</label>
            <input v-model.number="form.intervalle_min_jours" type="number" min="1" class="input" />
          </div>
          <div>
            <label class="label">Nb plats aimés minimum</label>
            <input v-model.number="form.nb_plats_aimes_min" type="number" min="0" class="input" />
          </div>
        </div>

        <!-- Créneaux actifs -->
        <div>
          <label class="label">Créneaux actifs</label>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <label v-for="dispo in dispoOpts" :key="dispo.key" class="flex items-center gap-1.5 text-sm cursor-pointer">
              <input type="checkbox" :value="dispo.key" v-model="form.creneaux_actifs" class="rounded" />
              {{ dispo.label }}
            </label>
          </div>
        </div>
      </div>

      <!-- Repas -->
      <div class="bg-white rounded-2xl shadow p-6 space-y-4">
        <h2 class="font-semibold text-gray-700">Heures des repas</h2>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Heure du déjeuner</label>
            <input v-model="form.heure_midi" type="time" class="input" />
          </div>
          <div>
            <label class="label">Heure du dîner</label>
            <input v-model="form.heure_soir" type="time" class="input" />
          </div>
        </div>
      </div>

      <!-- Accès lecteurs -->
      <div class="bg-white rounded-2xl shadow p-6 space-y-4">
        <h2 class="font-semibold text-gray-700">Accès famille</h2>
        <div>
          <label class="label">Mot de passe famille</label>
          <input v-model="form.mot_de_passe_lecteur" type="text" autocomplete="off" class="input" />
          <p class="text-xs text-gray-400 mt-1">Mot de passe partagé pour l'accès lecteur.</p>
        </div>
      </div>

      <!-- SMS -->
      <div class="bg-white rounded-2xl shadow p-6 space-y-4">
        <h2 class="font-semibold text-gray-700">Notifications SMS (Brevo)</h2>
        <label class="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" v-model="form.sms_actif" class="rounded" />
          <span class="text-sm text-gray-700">Activer les SMS de rappel de repas</span>
        </label>
        <div v-if="form.sms_actif">
          <label class="label">Clé API Brevo</label>
          <input v-model="form.brevo_api_key" type="password" autocomplete="off" class="input" />
        </div>
      </div>

      <!-- Coursesu -->
      <div class="bg-white rounded-2xl shadow p-6 space-y-4">
        <h2 class="font-semibold text-gray-700">🛒 Identifiants coursesu.com</h2>
        <p class="text-xs text-amber-600 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
          ⚠️ Ces identifiants sont stockés en clair dans la base de données locale.
          Utilisez de préférence un mot de passe unique à cette application.
        </p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="label">Email coursesu.com</label>
            <input v-model="form.coursesu_login" type="email" autocomplete="off" class="input" placeholder="votre@email.com" />
          </div>
          <div>
            <label class="label">Mot de passe coursesu.com</label>
            <input v-model="form.coursesu_password" type="password" autocomplete="new-password" class="input" :placeholder="coursesuConfigured ? '★ déjà configuré — laisser vide pour conserver' : 'Mot de passe'" />
          </div>
        </div>
        <p v-if="coursesuConfigured" class="text-xs text-emerald-600">✓ Connexion coursesu configurée</p>
      </div>

      <div class="flex items-center gap-4">
        <button type="submit" :disabled="saving" class="bg-emerald-600 text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-emerald-700 disabled:opacity-50">
          {{ saving ? 'Sauvegarde…' : 'Enregistrer' }}
        </button>
        <span v-if="saved" class="text-sm text-emerald-600">✓ Paramètres enregistrés</span>
        <span v-if="saveError" class="text-sm text-red-600">{{ saveError }}</span>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { useApi } from '~/composables/useApi'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const api = useApi()
const loading = ref(true)
const saving = ref(false)
const saved = ref(false)
const saveError = ref('')

const jours = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
const JOURS_K = ['lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche']
const jourOptions: Record<string, string> = { lundi: 'Lundi', mardi: 'Mardi', mercredi: 'Mercredi', jeudi: 'Jeudi', vendredi: 'Vendredi', samedi: 'Samedi', dimanche: 'Dimanche' }
const dispoOpts = JOURS_K.flatMap((j, i) => [
  { key: `${j}_midi`, label: `${jours[i]} midi` },
  { key: `${j}_soir`, label: `${jours[i]} soir` },
])

const form = reactive({
  jour_debut_semaine: 'samedi',
  intervalle_min_jours: 7,
  nb_plats_aimes_min: 2,
  heure_midi: '12:00',
  heure_soir: '19:00',
  mot_de_passe_lecteur: '',
  sms_actif: false,
  brevo_api_key: '',
  creneaux_actifs: [] as string[],
  coursesu_login: '',
  coursesu_password: '',
})

const coursesuConfigured = ref(false)

async function charger() {
  loading.value = true
  try {
    const data = await api.get('/config/')
    const creneaux = (data.creneaux_actifs || []).map((c: any) => `${c.jour}_${c.creneau}`)
    Object.assign(form, {
      jour_debut_semaine: data.jour_debut_semaine,
      intervalle_min_jours: data.intervalle_min_jours,
      nb_plats_aimes_min: data.nb_plats_aimes_min,
      heure_midi: (data.heure_midi || '12:30').substring(0, 5),
      heure_soir: (data.heure_soir || '19:00').substring(0, 5),
      mot_de_passe_lecteur: data.mot_de_passe_lecteur || '',
      sms_actif: data.sms_actif,
      brevo_api_key: data.brevo_api_key || '',
      creneaux_actifs: creneaux,
      coursesu_login: data.coursesu_login || '',
      coursesu_password: '',
    })
    coursesuConfigured.value = data.coursesu_configured ?? false
  } finally {
    loading.value = false
  }
}

async function sauvegarder() {
  saving.value = true
  saved.value = false
  saveError.value = ''
  try {
    const payload: any = {
      jour_debut_semaine: form.jour_debut_semaine,
      intervalle_min_jours: form.intervalle_min_jours,
      nb_plats_aimes_min: form.nb_plats_aimes_min,
      heure_midi: form.heure_midi.length === 5 ? form.heure_midi + ':00' : form.heure_midi,
      heure_soir: form.heure_soir.length === 5 ? form.heure_soir + ':00' : form.heure_soir,
      mot_de_passe_lecteur: form.mot_de_passe_lecteur,
      sms_actif: form.sms_actif,
      creneaux_actifs: form.creneaux_actifs.map(k => {
        const [jour, creneau] = k.split('_')
        return { jour, creneau }
      }),
    }
    if (form.brevo_api_key) payload.brevo_api_key = form.brevo_api_key
    if (form.coursesu_login) payload.coursesu_login = form.coursesu_login
    if (form.coursesu_password) payload.coursesu_password = form.coursesu_password
    await api.patch('/config/', payload)
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch {
    saveError.value = 'Erreur lors de la sauvegarde.'
  } finally {
    saving.value = false
  }
}

onMounted(charger)
</script>

<style scoped>
.label { @apply block text-sm font-medium text-gray-700 mb-1; }
.input { @apply w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400; }
</style>

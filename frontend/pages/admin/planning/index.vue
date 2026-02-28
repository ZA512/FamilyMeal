<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold text-gray-800">Planning</h1>
      <button @click="creerSemaine" :disabled="creating" class="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-emerald-700 disabled:opacity-50">
        {{ creating ? '…' : '+ Nouvelle semaine' }}
      </button>
    </div>

    <!-- Sélecteur de semaine -->
    <div class="flex items-center gap-3 flex-wrap">
      <select v-model="semaineId" @change="chargerSemaine" class="border rounded-lg px-3 py-2 text-sm">
        <option value="">— Sélectionner une semaine —</option>
        <option v-for="s in semaines" :key="s.id" :value="s.id">
          Semaine du {{ formatDate(s.date_debut) }} — {{ s.statut }}
        </option>
      </select>
      <template v-if="semaine">
        <button
          v-if="semaine.statut === 'brouillon'"
          @click="publier"
          :disabled="actionLoading"
          class="bg-emerald-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-emerald-700 disabled:opacity-50"
        >📢 Publier</button>
        <button
          v-else
          @click="depublier"
          :disabled="actionLoading"
          class="bg-gray-400 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-gray-500 disabled:opacity-50"
        >Dépublier</button>
        <button @click="genererAuto" :disabled="actionLoading" class="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">
          ⚡ Générer auto
        </button>
      </template>
    </div>

    <!-- Grille -->
    <div v-if="loadingGrid" class="text-center py-16 text-gray-400">Chargement…</div>
    <div v-else-if="semaine" class="overflow-x-auto">
      <table class="min-w-full bg-white rounded-2xl shadow overflow-hidden text-sm">
        <thead>
          <tr class="bg-emerald-50">
            <th class="px-2 py-3 w-14"></th>
            <th v-for="jour in jours" :key="jour.date" class="px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase">
              <div>{{ jour.nomCourt }}</div>
              <div class="text-sm font-bold text-gray-700">{{ jour.numero }}</div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="creneau in ['midi', 'soir']" :key="creneau" class="border-t border-gray-100">
            <td class="px-2 py-2 text-xs font-semibold text-gray-400 uppercase text-center">
              {{ creneau === 'midi' ? '🌞' : '🌙' }}
            </td>
            <td v-for="jour in jours" :key="jour.date" class="px-1 py-2 align-top border-l border-gray-100">
              <CellPlanning
                :creneau="getCreneauPlanning(jour.date, creneau)"
                :plats="plats"
                :membres="membres"
                @update="(platId: number | null, variantId: number | null) => updateCreneau(jour.date, creneau, platId, variantId)"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="semaineId === ''" class="text-center py-12 text-gray-400">
      Sélectionnez ou créez une semaine.
    </div>

    <!-- Top 3 candidats (mode interactif) -->
    <div v-if="candidats.length" class="bg-white rounded-2xl shadow p-5">
      <h3 class="font-semibold text-gray-700 mb-3">Suggestions pour le créneau sélectionné</h3>
      <div class="flex gap-3 flex-wrap">
        <button
          v-for="c in candidats"
          :key="c.id"
          @click="choisirCandidat(c)"
          class="border-2 border-emerald-400 rounded-xl px-4 py-2 text-sm hover:bg-emerald-50 transition"
        >
          <div class="font-semibold">{{ c.nom }}</div>
          <div class="text-xs text-gray-400">score: {{ c.score?.toFixed(1) }}</div>
        </button>
      </div>
      <button @click="candidats = []; candidatSlot = null" class="text-xs text-gray-400 mt-2 hover:text-gray-600">Annuler</button>
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
const semaine = ref<any>(null)
const plats = ref<any[]>([])
const membres = ref<any[]>([])
const config = ref<any>(null)
const loadingGrid = ref(false)
const creating = ref(false)
const actionLoading = ref(false)
const candidats = ref<any[]>([])
const candidatSlot = ref<{ date: string; creneau: string } | null>(null)

// dayjs .day() : 0=Dim, 1=Lun, 2=Mar, 3=Mer, 4=Jeu, 5=Ven, 6=Sam
const JOURS_COURTS: Record<number, string> = { 0: 'Dim', 1: 'Lun', 2: 'Mar', 3: 'Mer', 4: 'Jeu', 5: 'Ven', 6: 'Sam' }
const JOUR_TO_DAY: Record<string, number> = {
  dimanche: 0, lundi: 1, mardi: 2, mercredi: 3, jeudi: 4, vendredi: 5, samedi: 6,
}

const jours = computed(() => {
  if (!semaine.value) return []
  const debut = dayjs(semaine.value.date_debut)
  return Array.from({ length: 7 }, (_, i) => {
    const d = debut.add(i, 'day')
    return { date: d.format('YYYY-MM-DD'), nomCourt: JOURS_COURTS[d.day()], numero: d.format('D') }
  })
})

function getCreneauPlanning(date: string, creneau: string) {
  return semaine.value?.creneaux?.find((c: any) => c.date === date && c.creneau === creneau) || null
}

function formatDate(d: string) { return dayjs(d).format('D MMM YYYY') }

async function chargerSemaines() {
  const raw = await api.get<any>('/semaines/')
  const data = Array.isArray(raw) ? raw : (raw.results ?? [])
  semaines.value = data.sort((a: any, b: any) => b.date_debut.localeCompare(a.date_debut))
}

async function chargerSemaine() {
  if (!semaineId.value) { semaine.value = null; return }
  loadingGrid.value = true
  try {
    semaine.value = await api.get(`/semaines/${semaineId.value}/`)
  } finally {
    loadingGrid.value = false
  }
}

async function creerSemaine() {
  creating.value = true
  try {
    // Date of next occurrence of the configured start day (at least 1 day from today)
    const jourNum = JOUR_TO_DAY[config.value?.jour_debut_semaine ?? 'lundi'] ?? 1
    const todayDay = dayjs().day()
    const daysUntil = ((jourNum - todayDay + 7) % 7) || 7
    const debut = dayjs().add(daysUntil, 'day')
    const s = await api.post('/semaines/', { date_debut: debut.format('YYYY-MM-DD') })
    await chargerSemaines()
    semaineId.value = s.id
    await chargerSemaine()
  } finally {
    creating.value = false
  }
}

async function genererAuto() {
  if (!confirm('Regénérer le planning automatiquement ? Le planning existant sera remplacé.')) return
  actionLoading.value = true
  try {
    await api.post(`/semaines/${semaineId.value}/generer/`, {})
    await chargerSemaine()
  } catch {
    alert('Erreur lors de la génération.')
  } finally {
    actionLoading.value = false
  }
}

async function publier() {
  actionLoading.value = true
  try {
    await api.post(`/semaines/${semaineId.value}/publier/`, {})
    await chargerSemaine()
  } finally {
    actionLoading.value = false
  }
}

async function depublier() {
  actionLoading.value = true
  try {
    await api.post(`/semaines/${semaineId.value}/depublier/`, {})
    await chargerSemaine()
  } finally {
    actionLoading.value = false
  }
}

async function updateCreneau(date: string, creneauType: string, platId: number | null, variantId: number | null = null) {
  const existing = getCreneauPlanning(date, creneauType)
  try {
    if (existing) {
      await api.patch(`/creneaux/${existing.id}/`, { plat_principal: platId, variant_choisi: variantId })
    } else {
      await api.post('/creneaux/', { semaine: semaineId.value, date, creneau: creneauType, plat_principal: platId, variant_choisi: variantId })
    }
    await chargerSemaine()
  } catch {
    alert('Erreur lors de la mise à jour.')
  }
}

// Interactive mode: load top 3 candidates for a slot
async function chargerCandidats(date: string, creneau: string) {
  const data = await api.post(`/semaines/${semaineId.value}/candidats/`, { date, creneau })
  candidats.value = data
  candidatSlot.value = { date, creneau }
}

async function choisirCandidat(plat: any) {
  if (!candidatSlot.value) return
  await updateCreneau(candidatSlot.value.date, candidatSlot.value.creneau, plat.id)
  candidats.value = []
  candidatSlot.value = null
}

// CellPlanning inline component for each grid cell
const CellPlanning = defineComponent({
  props: { creneau: Object, plats: Array, membres: Array },
  emits: ['update'],
  setup(props, { emit }) {
    const api = useApi()
    const editing = ref(false)
    const selected = ref<number | null>(null)
    const selectedVariant = ref<number | null>(null)

    watchEffect(() => {
      // plat_principal est un entier (PK), pas un objet
      selected.value = props.creneau?.plat_principal || null
      selectedVariant.value = props.creneau?.variant_choisi || null
    })

    const platSelectionne = computed(() =>
      (props.plats as any[] || []).find((p: any) => p.id === selected.value) || null
    )

    async function onPlatChange(e: Event) {
      const platId = Number((e.target as HTMLSelectElement).value) || null
      selected.value = platId
      selectedVariant.value = null
      if (!platId) return
      const plat = (props.plats as any[] || []).find((p: any) => p.id === platId)
      if (plat?.variants?.length) {
        try {
          const res: any = await api.get(`/plats/${platId}/suggest-variant/`)
          selectedVariant.value = res.variant_id ?? null
        } catch { /* ignore */ }
      }
    }

    // Valeurs snapshot pour pouvoir annuler
    let snapshotPlat: number | null = null
    let snapshotVariant: number | null = null

    function openEdit() {
      snapshotPlat = selected.value
      snapshotVariant = selectedVariant.value
      editing.value = true
    }

    function save() {
      emit('update', selected.value, selectedVariant.value)
      editing.value = false
    }

    function cancel() {
      selected.value = snapshotPlat
      selectedVariant.value = snapshotVariant
      editing.value = false
    }

    function onFocusout(e: FocusEvent) {
      // Si le focus reste dans le conteneur (ex: passage plat → variant), ne pas sauver
      if ((e.currentTarget as HTMLElement).contains(e.relatedTarget as Node)) return
      save()
    }

    return () => {
      if (editing.value) {
        const variants: any[] = platSelectionne.value?.variants || []
        return h('div', {
          class: 'p-1 space-y-1 outline-none',
          tabindex: '-1',
          onFocusout,
          onKeydown: (e: KeyboardEvent) => { if (e.key === 'Escape') cancel() },
        }, [
          h('select', {
            value: selected.value,
            onChange: onPlatChange,
            class: 'w-full text-xs border rounded px-1 py-0.5',
          }, [
            h('option', { value: '' }, '— Vide —'),
            ...(props.plats as any[]).filter((p: any) => !p.est_secours).map((p: any) =>
              h('option', { value: p.id }, p.nom)
            ),
          ]),
          variants.length > 0
            ? h('select', {
                value: selectedVariant.value,
                onChange: (e: Event) => { selectedVariant.value = Number((e.target as HTMLSelectElement).value) || null },
                class: 'w-full text-xs border border-violet-300 rounded px-1 py-0.5 bg-violet-50',
              }, [
                ...variants.map((v: any) => h('option', { value: v.id }, v.nom_court || v.nom)),
              ])
            : null,
          h('p', { class: 'text-[10px] text-gray-400 text-right' }, 'Clic ailleurs pour valider · Échap pour annuler'),
        ])
      }
      return h('div', {
        onClick: openEdit,
        class: 'cursor-pointer min-h-[2.5rem] p-1 rounded hover:bg-emerald-50 transition',
      }, props.creneau?.plat_principal
        ? h('div', {}, [
            h('div', { class: 'text-xs font-medium text-gray-700 leading-tight' }, props.creneau.plat_principal_detail?.nom || ''),  // plat_principal est un PK entier, le nom est dans plat_principal_detail
            props.creneau.variant_choisi_nom_court
              ? h('span', { class: 'inline-block mt-0.5 px-1 py-0.5 text-[10px] rounded bg-violet-100 text-violet-700' },
                  `⇅ ${props.creneau.variant_choisi_nom_court}`)
              : null,
          ])
        : h('div', { class: 'text-gray-300 text-xs' }, '+')
      )
    }
  }
})

onMounted(async () => {
  await Promise.all([
    chargerSemaines(),
    api.get('/plats/').then(d => plats.value = d),
    api.get('/membres/').then(d => membres.value = d),
    api.get('/config/').then(d => config.value = d),
  ])
})
</script>

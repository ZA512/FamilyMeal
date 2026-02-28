<template>
  <div ref="rootEl">
    <!-- Champ de saisie -->
    <div
      class="flex items-center gap-1 w-full border border-gray-300 rounded-lg px-2 py-1.5 text-sm focus-within:ring-2 focus-within:ring-emerald-400 bg-white cursor-text"
      @click="ouvrirEtFocuser"
    >
      <span v-if="selected" :title="selected.nom" class="flex items-center gap-1 bg-emerald-100 text-emerald-800 rounded px-1.5 py-0.5 text-xs min-w-0">
        <span class="truncate max-w-[180px]">{{ selected.nom }}</span>
        <button type="button" @click.stop="effacer" class="text-emerald-500 hover:text-emerald-700 leading-none">✕</button>
      </span>
      <input
        ref="inputEl"
        v-model="query"
        type="text"
        :placeholder="selected ? '' : placeholder"
        class="flex-1 min-w-0 outline-none bg-transparent text-sm placeholder-gray-400"
        @focus="ouvrir"
        @input="ouvrir"
        @keydown.down.prevent="deplacerSelection(1)"
        @keydown.up.prevent="deplacerSelection(-1)"
        @keydown.enter.prevent="validerSelection"
        @keydown.escape="fermer"
      />
    </div>

    <!-- Dropdown rendu dans un Teleport pour échapper au overflow:hidden du modal -->
    <Teleport to="body">
      <div
        v-if="ouvert"
        :style="dropdownStyle"
        class="fixed z-[9999] bg-white border border-gray-200 rounded-xl shadow-xl max-h-72 overflow-y-auto"
      >
        <div v-if="!query" class="px-3 py-2 text-sm text-gray-400 italic">Tapez pour rechercher…</div>
        <template v-else-if="filtres.length > 0">
          <div
            v-for="(ing, i) in filtres"
            :key="ing.id"
            class="flex items-center gap-3 px-3 py-2 text-sm cursor-pointer hover:bg-emerald-50 transition-colors"
            :class="i === idx ? 'bg-emerald-100' : ''"
            @mousedown.prevent="choisir(ing)"
          >
            <!-- Miniature avec zoom au survol -->
            <div class="shrink-0">
              <img
                v-if="ing.image_url"
                :src="ing.image_url"
                :alt="ing.nom"
                class="w-8 h-8 rounded object-cover cursor-zoom-in"
                @mouseenter="(e) => afficherPreview(e, ing.image_url!)"
                @mouseleave="cacherPreview"
              />
              <span
                v-else
                class="w-8 h-8 rounded bg-emerald-100 text-emerald-700 font-semibold text-xs flex items-center justify-center uppercase"
              >{{ initiales(ing.nom) }}</span>
            </div>
            <span class="flex-1 break-words">{{ ing.nom }}</span>
            <span v-if="ing.prix !== null" class="text-xs text-gray-400 ml-2 shrink-0">{{ Number(ing.prix).toFixed(2) }} €</span>
          </div>
        </template>
        <div v-else class="px-3 py-2 text-sm text-gray-400">Aucun ingrédient trouvé</div>
      </div>
    </Teleport>

    <!-- Preview image téléportée hors de tout overflow -->
    <Teleport to="body">
      <div
        v-if="preview.visible"
        :style="{ position: 'fixed', top: preview.y + 'px', left: preview.x + 'px', zIndex: 10001, pointerEvents: 'none' }"
        class="rounded-xl shadow-2xl border border-gray-200 bg-white overflow-hidden"
      >
        <img :src="preview.url" class="w-32 h-32 object-cover block" />
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelValue: number | null | ''
  ingredients: { id: number; nom: string; prix: number | null; image_url?: string }[]
  placeholder?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', val: number | null): void
}>()

const query = ref('')
const ouvert = ref(false)
const idx = ref(-1)
const rootEl = ref<HTMLElement | null>(null)
const inputEl = ref<HTMLInputElement | null>(null)

// Position du dropdown calculée à partir du champ
const dropdownStyle = ref<Record<string, string>>({})

// Preview image au survol
const preview = reactive({ visible: false, url: '', x: 0, y: 0 })

function afficherPreview(e: MouseEvent, url: string) {
  const previewSize = 128 + 16 // taille + marge
  const x = e.clientX + 16
  const y = e.clientY - previewSize / 2
  preview.url = url
  preview.x = Math.min(x, window.innerWidth - previewSize - 8)
  preview.y = Math.max(8, Math.min(y, window.innerHeight - previewSize - 8))
  preview.visible = true
}

function cacherPreview() {
  preview.visible = false
}

function calculerPosition() {
  if (!rootEl.value) return
  const rect = rootEl.value.getBoundingClientRect()
  const spaceBelow = window.innerHeight - rect.bottom
  const dropH = 288 // max-h-72 ≈ 288px
  const minW = Math.max(420, rect.width)
  // Éviter que le dropdown dépasse à droite de l'écran
  const left = Math.min(rect.left, window.innerWidth - minW - 8)
  if (spaceBelow >= dropH || spaceBelow >= 120) {
    // En dessous
    dropdownStyle.value = {
      top: `${rect.bottom + 4}px`,
      left: `${Math.max(4, left)}px`,
      minWidth: `${minW}px`,
    }
  } else {
    // Au dessus
    dropdownStyle.value = {
      bottom: `${window.innerHeight - rect.top + 4}px`,
      left: `${Math.max(4, left)}px`,
      minWidth: `${minW}px`,
    }
  }
}

const selected = computed(() =>
  props.modelValue ? props.ingredients.find(i => i.id === props.modelValue) ?? null : null
)

function normaliser(s: string) {
  return s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
}

const filtres = computed(() => {
  const q = normaliser(query.value.trim())
  if (!q) return []
  return props.ingredients.filter(i => normaliser(i.nom).includes(q))
})

function ouvrirEtFocuser() {
  ouvrir()
  nextTick(() => inputEl.value?.focus())
}

function ouvrir() {
  ouvert.value = true
  nextTick(calculerPosition)
}

function fermer() {
  ouvert.value = false
  idx.value = -1
}

function choisir(ing: { id: number; nom: string }) {
  emit('update:modelValue', ing.id)
  query.value = ''
  fermer()
}

function effacer() {
  emit('update:modelValue', null)
  query.value = ''
  fermer()
}

function deplacerSelection(dir: number) {
  if (!ouvert.value) { ouvrir(); return }
  idx.value = Math.max(-1, Math.min(filtres.value.length - 1, idx.value + dir))
}

function validerSelection() {
  if (idx.value >= 0 && filtres.value[idx.value]) {
    choisir(filtres.value[idx.value])
  }
}

function onClickOut(e: MouseEvent) {
  if (rootEl.value && !rootEl.value.contains(e.target as Node)) {
    fermer()
    query.value = ''
  }
}

function initiales(nom: string) {
  const mots = nom.trim().split(/\s+/)
  if (mots.length >= 2) return (mots[0][0] + mots[1][0]).toUpperCase()
  return nom.slice(0, 2).toUpperCase()
}

onMounted(() => document.addEventListener('mousedown', onClickOut))
onUnmounted(() => document.removeEventListener('mousedown', onClickOut))
</script>

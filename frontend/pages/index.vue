<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
auth.initFromCookies()

if (auth.isAdmin) {
  navigateTo('/admin')
} else if (auth.isAuthenticated) {
  navigateTo('/planning')
} else {
  navigateTo('/lecteur-login')
}
</script>

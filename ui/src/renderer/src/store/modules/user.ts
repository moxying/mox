import { defineStore, acceptHMRUpdate } from 'pinia'
import { ref } from 'vue'
export const useUserStore = defineStore('user', () => {
  const userInfo = ref({
    login: false
  })
  return { userInfo }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useUserStore, import.meta.hot))
}

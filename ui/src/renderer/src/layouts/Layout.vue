<script setup lang="ts">
import Sidebar from '@/layouts/Sidebar.vue'
import { ref } from 'vue'

defineOptions({
  name: 'Layout',
  components: {
    Sidebar
  }
})

const agentOK = ref(true)
</script>

<template>
  <v-app class="flex flex-col size-full">
    <div
      class="flex-none bg-surface-container border-b-[1px] border-solid border-inverse-on-surface h-9 w-full"
      style="-webkit-app-region: drag"
    ></div>
    <div class="flex flex-row size-full">
      <Sidebar class="flex-none w-12 h-full" />
      <div class="size-full">
        <router-view />
      </div>
    </div>
    <div class="flex flex-row flex-none bg-surface-container h-6">
      <div v-if="agentOK" class="flex flex-row w-8 bg-primary30">
        <v-icon icon="$agentOK" class="items-center ml-1 w-6 h-5 text-outline" />
      </div>
      <div v-else class="flex flex-row w-8 bg-error-container">
        <v-icon icon="$agentError" class="items-center ml-1 w-6 h-5 text-on-error-container" />
      </div>
    </div>
  </v-app>
</template>

<style lang="scss" scoped></style>

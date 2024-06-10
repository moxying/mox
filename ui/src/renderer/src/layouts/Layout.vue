<script setup lang="ts">
import Sidebar from '@/layouts/Sidebar.vue'

defineOptions({
  name: 'Layout',
  components: {
    Sidebar
  }
})
</script>

<template>
  <v-app class="flex flex-col size-full">
    <div
      class="flex-none bg-surface-container border-b-[1px] border-inverse-on-surface h-9 w-full"
      style="-webkit-app-region: drag"
    >
      123
    </div>
    <div class="flex flex-row size-full">
      <Sidebar class="flex-none w-12 h-full" />
      <div class="size-full">
        <router-view />
      </div>
    </div>
    <div class="flex-none bg-surface-container h-6">123</div>
  </v-app>
</template>

<style lang="scss" scoped></style>

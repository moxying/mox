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
      <Sidebar />
      <div class="size-full">
        <router-view />
      </div>
    </div>
    <div class="flex-none bg-surface-container h-6">123</div>
  </v-app>
</template>

<style lang="scss" scoped>
.mox-layout {
  display: flex;
  flex-direction: column;
  justify-content: start;
  width: 100%;
  height: 100%;

  .mox-layout-head {
    display: flex;
    width: 100%;
    height: 2.25rem;
    min-height: 2.25rem;
    background: rgb(var(--v-theme-surface-container));
    border-bottom: 1px solid rgb(var(--v-theme-inverse-on-surface));
    -webkit-app-region: drag;
  }

  .mox-layout-main {
    display: flex;
    flex-direction: row;
    flex: auto;
    width: 100%;
    height: 100%;

    .mox-layout-sidebar {
      width: 3rem;
      min-width: 3rem;
      height: 100%;
      background: rgb(var(--v-theme-surface-container));
      border-right: 1px solid rgb(var(--v-theme-inverse-on-surface));
    }
    .mox-layout-content {
      width: 100%;
      height: 100%;
    }
  }
  .mox-layout-footer {
    width: 100%;
    height: 1.5rem;
    min-height: 1.5rem;
    background: rgb(var(--v-theme-surface));
  }
}
</style>

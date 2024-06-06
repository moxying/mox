<script setup lang="ts">
import { ref } from 'vue'

defineOptions({
  name: 'Layout'
})

const menus = ref([{}])
</script>

<template>
  <v-locale-provider>
    <v-app>
      <v-app-bar
        color="surface-container"
        flat
        class="border-b-sm border-inverse-on-surface"
        style="-webkit-app-region: drag; height: 2.25rem"
      ></v-app-bar>
      <v-main class="d-flex flex-column" style="width: 100%; height: 100%; padding-top: 2.25rem">
        <div class="d-flex flex-row flex-fill">
          <div class="" style="height: 100%"></div>
          <div>
            <router-view />
          </div>
        </div>
        <v-footer class="flex-0-0" color="surface-container" style="height: 1.5rem">123</v-footer>
      </v-main>
    </v-app>
  </v-locale-provider>
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

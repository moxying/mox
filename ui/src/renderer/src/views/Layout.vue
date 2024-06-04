<script setup lang="ts">
defineOptions({
  name: 'Layout'
})
</script>

<template>
  <v-app>
    <div class="mox-layout">
      <div class="mox-layout-head"></div>
      <div class="mox-layout-main">
        <div class="mox-sidebar">
          <Sidebar />
        </div>
        <div class="mox-content">
          <router-view />
        </div>
      </div>
      <div class="mox-layout-footer"></div>
    </div>
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
    background: $app-header-color;
    -webkit-app-region: drag;
  }

  .mox-layout-main {
    display: flex;
    flex-direction: row;
    flex: auto;
    width: 100%;
    height: 100%;

    .mox-sidebar {
      width: 3rem;
      min-width: 3rem;
      height: 100%;
      background: $app-sidebar-color;
    }
    .mox-content {
      width: 100%;
      height: 100%;
    }
  }
  .mox-layout-footer {
    width: 100%;
    height: 1.5rem;
    min-height: 1.5rem;
    background: $app-footer-color;
  }
}
</style>

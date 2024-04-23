<script setup lang="ts">
import Sidebar from '@/views/layout/Sidebar.vue'
defineOptions({
  name: 'Layout',
  components: {
    Sidebar
  }
})
</script>

<template>
  <div class="app-layout">
    <div class="app-layout-head"></div>
    <div class="app-layout-main">
      <div class="sidebar">
        <Sidebar />
      </div>
      <div class="main-content">
        <router-view />
      </div>
    </div>
    <div class="app-layout-footer"></div>
  </div>
</template>

<style lang="scss" scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  justify-content: start;
  height: 100%;

  .app-layout-head {
    display: flex;
    height: 2.2rem;
    min-height: 2.2rem;
    background: $app-header-color;
    -webkit-app-region: drag;
  }

  $main-height: calc(100vh - 2.2rem - 1.5rem);
  .app-layout-main {
    display: flex;
    flex-direction: row;
    flex: auto;
    height: $main-height;

    .sidebar {
      width: 3rem;
      min-width: 3rem;
      background: $app-sidebar-color;
      height: $main-height;
    }
    .main-content {
      flex: auto;
      height: $main-height;
    }
  }
  .app-layout-footer {
    background: $app-footer-color;
    height: 1.5rem;
    min-height: 1.5rem;
  }
}
</style>

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
        height="36"
        flat
        class="border border-b-sm border-error-container"
      ></v-app-bar>
      <v-main>
        <div class="mox-layout">
          <div class="mox-layout-head"></div>
          <div class="mox-layout-main">
            <div class="mox-layout-sidebar">
              <v-navigation-drawer>
                <v-list>
                  <v-list-item
                    prepend-avatar="https://randomuser.me/api/portraits/women/85.jpg"
                    subtitle="sandra_a88@gmailcom"
                    title="Sandra Adams"
                  ></v-list-item>
                </v-list>
              </v-navigation-drawer>
            </div>
            <div class="mox-layout-content">
              <router-view />
            </div>
          </div>
          <div class="mox-layout-footer"></div>
        </div>
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

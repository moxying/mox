<script setup lang="ts">
import MenuItem from '@/layouts/MenuItem.vue'
import { mdiChartBubble } from '@mdi/js'

defineOptions({
  name: 'Sidebar',
  components: {
    MenuItem
  }
})
</script>

<template>
  <v-navigation-drawer
    v-model="sDrawer"
    left
    :permanent="mdAndUp"
    class="leftSidebar bg-muted border-right-0"
    elevation="10"
    app
    :temporary="mdAndDown"
    expand-on-hover
  >
    <v-icon :icon="mdiChartBubble" />
    <perfect-scrollbar class="scrollnavbar">
      <v-list class="py-5 px-4 bg-muted" density="compact">
        <template v-for="(item, i) in sidebarMenu">
          <NavItem :item="item" class="leftPadding" />
        </template>
      </v-list>
      <div>
        <BuyNow />
      </div>
    </perfect-scrollbar>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineOptions({
  name: 'Sidebar'
})

const menus = ref([
  {
    name: 'Create',
    icon: '$create'
  },
  {
    name: 'Engine',
    icon: '$engine'
  },
  {
    name: 'Personal',
    icon: '$personal'
  }
])
const activeMenu = ref(0)
const activateMenu = (index) => {
  activeMenu.value = index
}
</script>

<template>
  <div
    class="flex flex-col size-full bg-surface-container border-r-[1px] border-solid border-inverse-on-surface"
  >
    <v-list class="size-full p-0" :lines="false" bg-color="surface-container">
      <v-list-item
        v-for="(item, index) in menus"
        :key="index"
        :value="item"
        :to="{ name: item.name }"
        class="p-0 border-l-4 border-solid border-transparent"
        color="primary"
        variant="plain"
        :active="activeMenu === index"
        @click="activateMenu(index)"
      >
        <v-icon :icon="item.icon" class="ml-1 w-8 h-8" />
      </v-list-item>
    </v-list>
    <div><v-icon icon="$setting" class="ml-2 mb-2 w-8 h-8 text-outline" /></div>
  </div>
</template>

<style lang="scss" scoped>
.v-list-item--active {
  @extend %app-gradient-border-image;
  opacity: 1;
}
</style>

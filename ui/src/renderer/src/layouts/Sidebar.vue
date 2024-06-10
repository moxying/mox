<script setup lang="ts">
import { ref } from 'vue'

defineOptions({
  name: 'Sidebar'
})

const menus = ref([
  {
    name: 'Create',
    meta: {
      title: '创作',
      icon: '$create'
    }
  },
  {
    name: 'Engine',
    meta: {
      title: '引擎',
      icon: '$engine'
    }
  },
  {
    name: 'Personal',
    meta: {
      title: '我的',
      icon: '$personal'
    }
  }
])
</script>

<template>
  <div class="flex flex-col size-full">
    <v-list class="size-full p-0" :lines="false">
      <v-list-item
        v-for="(item, i) in menus"
        :key="i"
        :value="item"
        :to="{ name: item.name }"
        class="p-0 border-l-4 border-solid border-transparent"
        color="primary"
        base-color="outline"
        variant="plain"
      >
        <v-icon :icon="item.meta.icon" class="ml-1 w-8 h-8" />
      </v-list-item>
    </v-list>
    <div>123</div>
  </div>
</template>

<style lang="scss" scoped>
.v-list-item--active {
  @extend %app-gradient-border-image;
}
</style>

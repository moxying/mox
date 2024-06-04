<script setup lang="ts">
import MenuItem from '@/views/layout/MenuItem.vue'
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

defineOptions({
  name: 'Sidebar',
  components: {
    MenuItem
  }
})

const isCollapse = ref(false)
const active = ref('Create')

const menus = ref([
  // {
  //   name: 'Home',
  //   meta: {
  //     title: '首页',
  //     icon: 'iconfont icon-home'
  //   }
  // },
  {
    name: 'Create',
    meta: {
      title: '创作',
      icon: 'iconfont icon-create'
    }
  },
  {
    name: 'Personal',
    meta: {
      title: '个人',
      icon: 'iconfont icon-personal'
    }
  }
])

const selectMenuItem = (index) => {
  if (index === route.name) return
  if (index.indexOf('http://') > -1 || index.indexOf('https://') > -1) {
    window.open(index)
  } else {
    router.push({ name: index })
  }
}
</script>

<template>
  <transition :duration="{ enter: 800, leave: 100 }" mode="out-in" name="el-fade-in-linear">
    <el-menu
      :collapse="isCollapse"
      :collapse-transition="false"
      :default-active="active"
      background-color="transparent"
      active-text-color="#fff"
      text-color="#a7b2c1"
      unique-opened
      @select="selectMenuItem"
    >
      <template v-for="item in menus" :key="item.name">
        <menu-item :router-info="item" />
      </template>
    </el-menu>
  </transition>
</template>

<style lang="scss" scoped>
.el-menu {
  border-right: none;
}
</style>

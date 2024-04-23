<!-- ref: https://juejin.cn/post/7250513276236267557 -->
<script setup lang="ts">
import { ref } from 'vue'
import useContextMenu from './useContextMenu'
const containerRef = ref(null)
const { x, y, showMenu } = useContextMenu(containerRef)

interface Menu {
  label: string
}

const props = defineProps({
  // 接收传递进来的菜单项
  menu: {
    type: Array as () => Menu[],
    default: (): Menu[] => []
  }
})
// 声明一个事件，选中菜单项的时候返回数据
const emit = defineEmits(['select'])
// 菜单的点击事件
function handleClick(item) {
  // 选中菜单后关闭菜单
  showMenu.value = false
  // 并返回选中的菜单
  emit('select', item)
}
function handleBeforeEnter(el) {
  el.style.height = 0
}
function handleEnter(el) {
  el.style.height = 'auto'
  const h = el.clientHeight
  el.style.height = 0
  requestAnimationFrame(() => {
    el.style.height = h + 'px'
    el.style.transition = '.5s'
  })
}
function handleAfterEnter(el) {
  el.style.transition = 'none'
}
</script>

<template>
  <div ref="containerRef">
    <!-- 定义插槽，传递的内容就要显示在插槽之中 -->
    <slot></slot>
    <!-- 通过 Teleport 将菜单传送到 body 中  -->
    <Teleport to="body">
      <Transition
        @before-enter="handleBeforeEnter"
        @enter="handleEnter"
        @after-enter="handleAfterEnter"
      >
        <!-- 设置一个 div 用来显示菜单 -->
        <div
          v-if="showMenu"
          class="context-menu"
          :style="{
            left: x + 'px',
            top: y + 'px'
          }"
        >
          <div class="menu-list">
            <!-- 循环遍历菜单项，显示出来 -->
            <div
              v-for="item in props.menu"
              :key="item.label"
              class="menu-item"
              @click="handleClick(item)"
            >
              {{ item.label }}
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style lang="scss" scoped>
.context-menu {
  position: fixed;
}
</style>

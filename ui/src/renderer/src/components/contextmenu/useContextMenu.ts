import { onMounted, onUnmounted, ref } from 'vue'
export default function (containerRef) {
  const showMenu = ref(false)
  const x = ref(0)
  const y = ref(0)

  // 事件处理函数
  const handleContextMenu = (e) => {
    e.preventDefault() // 阻止浏览器的默认行为
    e.stopPropagation() // 阻止冒泡
    // console.log('x y >>> ', e.clientX, e.clientY)
    showMenu.value = true
    x.value = e.clientX
    y.value = e.clientY
  }
  // 注册一个事件函数用来关闭菜单
  function closeMenu() {
    showMenu.value = false
  }
  onMounted(() => {
    const div = containerRef.value
    div.addEventListener('contextmenu', handleContextMenu) // contextmenu系统事件
    // 触发 window 点击事件的时候执行函数
    // 第三个参数设置为 true 表示事件句柄在捕获阶段执行
    window.addEventListener('click', closeMenu, true)
    // 处理 window 的 contextmenu 事件，用来关闭之前打开的菜单
    window.addEventListener('contextmenu', closeMenu, true)
  })
  onUnmounted(() => {
    const div = containerRef.value
    div.removeEventListener('contextmenu', handleContextMenu)
    window.removeEventListener('click', closeMenu, true)
    window.removeEventListener('contextmenu', closeMenu, true)
  })
  return {
    showMenu,
    x,
    y
  }
}

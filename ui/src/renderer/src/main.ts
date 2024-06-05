import '@/style/reset.scss'
import { createApp } from 'vue'
import App from './App.vue'
import router from '@/router'
import store from '@/store'
import i18n from '@/plugins/i18n'
import vuetify from '@/plugins/vuetify'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

// 导入公共样式
import '@/style/common.scss'
// ElementPlus
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
// https://animate.style/
import 'animate.css'
import './assets/icons/iconfont/iconfont.css'
// ContextMenu
import '@imengyu/vue3-context-menu/lib/vue3-context-menu.css'
// dayjs
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn' // 导入本地化语言
import relativeTime from 'dayjs/plugin/relativeTime' // 导入插件
dayjs.locale('zh-cn') // 使用本地化语言
dayjs.extend(relativeTime)

const app = createApp(App)

// router
app.use(router)
await router.isReady()
// store
app.use(store)
// i18n
app.use(i18n)
// Vuetify
app.use(vuetify)
// ElementPlus
app.use(ElementPlus, {
  locale: zhCn
})

// all done
app.mount('#app')

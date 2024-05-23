import { createApp } from 'vue'
import App from './App.vue'
import router from '@/router'
import store from '@/store'
import i18n from '@/plugins/i18n'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

// 引入重置样式
import '@/style/reset.scss'
// 导入公共样式
import '@/style/common.scss'
// Vuetify
import 'vuetify/styles'
import { createVuetify, type ThemeDefinition } from 'vuetify'
import { md3 } from 'vuetify/blueprints'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
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

// Vuetify
const myCustomLightTheme: ThemeDefinition = {
  dark: true,
  colors: {
    background: '#141218',
    surface: '#141218',
    'surface-bright': '#3B383E',
    'surface-light': '#424242', // TODO
    'surface-variant': '#49454F',
    'on-surface-variant': '#CAC4D0',
    primary: '#D0BCFE',
    'primary-darken-1': '#277CC1', // TODO
    secondary: '#CCC2DC',
    'secondary-darken-1': '#48A9A6', // TODO
    error: '#F2B8B5',
    info: '#2196F3', // TODO
    success: '#4CAF50', // TODO
    warning: '#FB8C00' // TODO
  },
  variables: {
    'border-color': '#FFFFFF',
    'border-opacity': 0.12,
    'high-emphasis-opacity': 1,
    'medium-emphasis-opacity': 0.7,
    'disabled-opacity': 0.5,
    'idle-opacity': 0.1,
    'hover-opacity': 0.04,
    'focus-opacity': 0.12,
    'selected-opacity': 0.08,
    'activated-opacity': 0.12,
    'pressed-opacity': 0.16,
    'dragged-opacity': 0.08,
    'theme-kbd': '#212529',
    'theme-on-kbd': '#FFFFFF',
    'theme-code': '#343434',
    'theme-on-code': '#CCCCCC'
  }
}
const vuetify = createVuetify({
  components,
  directives,
  blueprint: md3,
  theme: {
    defaultTheme: 'myCustomLightTheme',
    themes: {
      myCustomLightTheme
    }
  }
})

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

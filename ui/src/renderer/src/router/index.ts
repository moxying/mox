import { Router, createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import remainingRouter from './modules/remaining'
import store from '@/store'

/**
 * 自动导入全部静态路由，无需再手动引入！匹配 src/router/modules 目录（任何嵌套级别）中具有 .ts 扩展名的所有文件，除了 remaining.ts 文件
 * 如何匹配所有文件请看：https://github.com/mrmlnc/fast-glob#basic-syntax
 * 如何排除文件请看：https://cn.vitejs.dev/guide/features.html#negative-patterns
 */
const modules: Record<string, any> = import.meta.glob(
  ['./modules/**/*.ts', '!./modules/**/remaining.ts'],
  {
    eager: true
  }
)

/** 原始静态路由（未做任何处理） */
const routes: Array<any> = []

Object.keys(modules).forEach((key) => {
  routes.push(modules[key].default)
})

/** 不参与菜单的路由 */
export const remainingPaths = Object.keys(remainingRouter).map((v) => {
  return remainingRouter[v].path
})

/** 创建路由实例 */
const router: Router = createRouter({
  history: createWebHashHistory(),
  routes: routes.concat(...(remainingRouter as any)),
  strict: true
})

/** 路由白名单 */
// const whiteList = ['/login']

// router.beforeEach((to: ToRouteType, _from, next) => {
//   const userStore = useUserStore(store)
//   const userInfo = userStore.userInfo
//   if (userInfo.login) {
//     console.log('userInfo: ', userInfo)
//     next()
//   } else {
//     if (to.path !== '/login') {
//       if (whiteList.indexOf(to.path) !== -1) {
//         next()
//       } else {
//         next({ path: '/login' })
//       }
//     } else {
//       next()
//     }
//   }
// })

export default router

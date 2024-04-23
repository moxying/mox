// https://github.com/electron-vite/electron-vite-vue/issues/229
import Layout from '@/views/layout/Layout.vue'
import Create from '@/views/Create.vue'
import Personal from '@/views/Personal.vue'

export default [
  {
    path: '/',
    name: 'Layout',
    component: Layout,
    redirect: '/Create',
    meta: {
      rank: 0,
      showLink: false
    },
    children: [
      {
        path: 'create',
        name: 'Create',
        component: Create
      },
      {
        path: 'personal',
        name: 'Personal',
        component: Personal
      }
    ]
  }
] as Array<RouteConfigsTable>

// https://github.com/electron-vite/electron-vite-vue/issues/229
import Layout from '@/layouts/Layout.vue'
import Launch from '@/views/Launch.vue'
import Create from '@/views/Create.vue'
import Engine from '@/views/Engine.vue'
import Personal from '@/views/Personal.vue'

export default [
  {
    path: '/',
    name: 'Layout',
    component: Layout,
    redirect: '/launch',
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
        path: 'engine',
        name: 'Engine',
        component: Engine
      },
      {
        path: 'personal',
        name: 'Personal',
        component: Personal
      }
    ]
  },
  {
    path: '/launch',
    name: 'Launch',
    component: Launch
  }
] as Array<RouteConfigsTable>

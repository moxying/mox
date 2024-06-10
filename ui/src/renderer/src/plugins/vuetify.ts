import 'vuetify/styles'
import { createVuetify, type ThemeDefinition } from 'vuetify'
import { md3 } from 'vuetify/blueprints'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg'

// icon
import {
  mdiChartBubble as create,
  mdiWidgetsOutline as engine,
  mdiAccountBoxOutline as personal,
  mdiCog as setting,
  mdiCheckUnderline as agentOK,
  mdiFilterVariantRemove as agentError
} from '@mdi/js'

const moxTheme: ThemeDefinition = {
  dark: true,
  colors: {
    background: '#141218',
    'on-background': '#E6E0E9',
    surface: '#141218',
    'on-surface': '#E6E0E9',
    primary: '#D0BCFF',
    'on-primary': '#381E72',
    secondary: '#CCC2DC',
    'on-secondary': '#332D41',
    success: '#4CAF50', // TODO
    // 'on-success': '', // TODO
    warning: '#FB8C00', // TODO
    // 'on-warning': '', //TODO
    // error: '#F2B8B5',
    'on-error': '#601410',
    info: '#2196F3', // TODO
    'on-info': '', // TODO

    'surface-bright': '#3B383E',
    'surface-light': '#424242', // TODO
    'surface-variant': '#49454F',
    'on-surface-variant': '#CAC4D0',
    'primary-darken-1': '#277CC1', // TODO
    'secondary-darken-1': '#48A9A6' // TODO
  }
}
const vuetify = createVuetify({
  ssr: true,
  components,
  directives,
  blueprint: md3,
  theme: {
    defaultTheme: 'moxTheme',
    themes: {
      moxTheme
    }
  },
  icons: {
    defaultSet: 'mdi',
    aliases: {
      ...aliases,
      create,
      engine,
      personal,
      setting,
      agentOK,
      agentError
    },
    sets: {
      mdi
    }
  }
})

export default vuetify

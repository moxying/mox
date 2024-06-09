import 'vuetify/styles'
import { createVuetify, type ThemeDefinition } from 'vuetify'
import { md3 } from 'vuetify/blueprints'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg'

const dark = {
  primary: '#D0BCFF',
  'on-primary': '#381E72',
  'primary-container': '#4F378B',
  'on-primary-container': '#EADDFF',
  'primary-fixed': '#EADDFF',
  'on-primary-fixed': '#21005D',
  'primary-fixed-dim': '#D0BCFF',
  'on-primary-fixed-variant': '#4F378B',
  secondary: '#CCC2DC',
  'on-secondary': '#332D41',
  'secondary-container': '#4A4458',
  'on-secondary-container': '#E8DEF8',
  'secondary-fixed': '#E8DEF8',
  'on-secondary-fixed': '#1D192B',
  'secondary-fixed-dim': '#CCC2DC',
  'on-secondary-fixed-variant': '#4A4458',
  tertiary: '#EFB8C8',
  'on-tertiary': '#492532',
  'tertiary-container': '#633B48',
  'on-tertiary-container': '#FFD8E4',
  'tertiary-fixed': '#FFD8E4',
  'on-tertiary-fixed': '#31111D',
  'tertiary-fixed-dim': '#EFB8C8',
  'on-tertiary-fixed-variant': '#633B48',
  error: '#F2B8B5',
  'on-error': '#601410',
  'error-container': '#8C1D18',
  'on-error-container': '#F9DEDC',
  outline: '#938F99',
  surface: '#141218',
  'on-surface': '#E6E0E9',
  'on-surface-variant': '#CAC4D0',
  'inverse-surface': '#E6E0E9',
  'inverse-on-surface': '#322F35',
  'inverse-primary': '#6750A4',
  shadow: '#000000',
  'outline-variant': '#49454F',
  scrim: '#000000',
  'surface-container-highest': '#36343B',
  'surface-container-high': '#2B2930',
  'surface-container': '#211F26',
  'surface-container-low': '#1D1B20',
  'surface-container-lowest': '#0F0D13',
  'surface-bright': '#3B383E',
  'surface-dim': '#141218'
}

const moxTheme: ThemeDefinition = {
  dark: true,
  colors: {
    background: '#141218',
    'on-background': '#E6E0E9',
    surface: dark.surface,
    'on-surface': dark['on-surface'],
    primary: dark.primary,
    'on-primary': dark['on-primary'],
    secondary: dark.secondary,
    'on-secondary': dark['on-secondary'],
    success: '#4CAF50', // TODO
    // 'on-success': '', // TODO
    warning: '#FB8C00', // TODO
    // 'on-warning': '', //TODO
    // error: '#F2B8B5',
    'on-error': dark['on-error'],
    info: '#2196F3', // TODO
    'on-info': '', // TODO

    'surface-bright': dark['surface-bright'],
    'surface-light': '#424242', // TODO
    'surface-variant': '#49454F',
    'on-surface-variant': dark['on-surface-variant'],
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
    aliases,
    sets: {
      mdi
    }
  }
})

export default vuetify

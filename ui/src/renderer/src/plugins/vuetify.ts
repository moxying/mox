import 'vuetify/styles'
import { createVuetify, type ThemeDefinition } from 'vuetify'
import { md3 } from 'vuetify/blueprints'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg'

const palettes = {
  primary0: '#000000',
  primary10: '#21005D',
  primary20: '#381E72',
  primary30: '#4F378B',
  primary40: '#6750A4',
  primary50: '#7F67BE',
  primary60: '#9A82DB',
  primary70: '#B69DF8',
  primary80: '#D0BCFF',
  primary90: '#EADDFF',
  primary95: '#F6EDFF',
  primary99: '#FFFBFE',
  primary100: '#FFFFFF',
  secondary0: '#000000',
  secondary10: '#1D192B',
  secondary20: '#332D41',
  secondary30: '#4A4458',
  secondary40: '#625B71',
  secondary50: '#7A7289',
  secondary60: '#958DA5',
  secondary70: '#B0A7C0',
  secondary80: '#CCC2DC',
  secondary90: '#E8DEF8',
  secondary95: '#F6EDFF',
  secondary100: '#FFFFFF',
  tertiary0: '#000000',
  tertiary10: '#31111D',
  tertiary20: '#492532',
  tertiary30: '#633B48',
  tertiary40: '#7D5260',
  tertiary50: '#986977',
  tertiary60: '#B58392',
  tertiary70: '#D29DAC',
  tertiary80: '#EFB8C8',
  tertiary90: '#FFD8E4',
  tertiary95: '#FFECF1',
  tertiary99: '#FFFBFA',
  tertiary100: '#FFFFFF',
  error0: '#000000',
  error10: '#410E0B',
  error20: '#601410',
  error30: '#8C1D18',
  error40: '#B3261E',
  error50: '#DC362E',
  error60: '#E46962',
  error70: '#EC928E',
  error80: '#F2B8B5',
  error90: '#F9DEDC',
  error95: '#FCEEEE',
  error99: '#FFFBF9',
  error100: '#FFFFFF',
  neutral0: '#000000',
  neutral10: '#1D1B20',
  neutral20: '#322F35',
  neutral30: '#48464C',
  neutral40: '#605D64',
  neutral50: '#79767D',
  neutral60: '#938F96',
  neutral70: '#AEA9B1',
  neutral80: '#CAC5CD',
  neutral90: '#E6E0E9',
  neutral95: '#F5EFF7',
  neutral100: '#FFFFFF',
  'neutral-variant0': '#000000',
  'neutral-variant10': '#1D1A22',
  'neutral-variant20': '#322F37',
  'neutral-variant30': '#49454F',
  'neutral-variant40': '#605D66',
  'neutral-variant50': '#79747E',
  'neutral-variant60': '#938F99',
  'neutral-variant70': '#AEA9B4',
  'neutral-variant80': '#CAC4D0',
  'neutral-variant90': '#E7E0EC',
  'neutral-variant95': '#F5EEFA',
  'neutral-variant100': '#FFFFFF'
}

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
    // surface: dark.surface,
    // 'on-surface': dark['on-surface'],
    // primary: dark.primary,
    // 'on-primary': dark['on-primary'],
    // secondary: dark.secondary,
    // 'on-secondary': dark['on-secondary'],
    success: '#4CAF50', // TODO
    // 'on-success': '', // TODO
    warning: '#FB8C00', // TODO
    // 'on-warning': '', //TODO
    // error: '#F2B8B5',
    // 'on-error': dark['on-error'],
    info: '#2196F3', // TODO
    'on-info': '', // TODO

    // 'surface-bright': dark['surface-bright'],
    'surface-light': '#424242', // TODO
    'surface-variant': '#49454F',
    // 'on-surface-variant': dark['on-surface-variant'],
    'primary-darken-1': '#277CC1', // TODO
    'secondary-darken-1': '#48A9A6', // TODO

    ...dark,
    ...palettes
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

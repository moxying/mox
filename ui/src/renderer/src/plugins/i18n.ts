// 多组件库的国际化和本地项目国际化兼容
import { type I18n, createI18n } from 'vue-i18n'

function siphonI18n(prefix = 'zh-CN') {
  return Object.fromEntries(
    Object.entries(import.meta.glob('../../locales/*.y(a)?ml', { eager: true })).map(
      ([key, value]: any) => {
        const matched = key.match(/([A-Za-z0-9-_]+)\./i)[1]
        return [matched, value.default]
      }
    )
  )[prefix]
}

export const localesConfigs = {
  zh: {
    ...siphonI18n('zh-CN')
  },
  en: {
    ...siphonI18n('en')
  }
}

/** 此函数只是配合i18n Ally插件来进行国际化智能提示，并无实际意义（只对提示起作用），如果不需要国际化可删除 */
export const $t = (key: string) => key

const i18n: I18n = createI18n({
  legacy: false,
  locale: 'zh',
  fallbackLocale: 'en',
  messages: localesConfigs
})

export default i18n

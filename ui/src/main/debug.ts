import { app } from 'electron'

export const printDebugInfo = () => {
  console.log('[main]debug info, home', app.getPath('home'))
  console.log('[main]debug info, appData', app.getPath('appData'))
  console.log('[main]debug info, userData', app.getPath('userData'))
  console.log('[main]debug info, temp', app.getPath('temp'))
  console.log('[main]debug info, logs', app.getPath('logs'))
  console.log('[main]debug info, appPath', app.getAppPath())
  console.log('[main]debug info, process.cwd()', process.cwd())
}

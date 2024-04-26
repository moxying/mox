import { contextBridge, ipcRenderer } from 'electron'

// Custom APIs for renderer
export const api = {
  // render => main
  // render: api.xx
  // preload: ipcRenderer.send
  // main: ipcMain.on
  //
  // startAgent: () => ipcRenderer.send('startAgent'),
  // restartAgent: () => ipcRenderer.send('restartAgent'),

  // render <=> main
  // render: api.xx
  // preload: ipcRenderer.invoke
  // main: ipcMain.handle
  //
  getAppPath: () => ipcRenderer.invoke('getAppPath'),

  // main => render
  // main: mainWindow.webContents.send
  // preload: ipcRenderer.on
  // render: window.api.onXXX
  //
  onLaunchEvent: (callback) => ipcRenderer.on('launch-event', (_event, value) => callback(value))
}

// Use `contextBridge` APIs to expose Electron APIs to
// renderer only if context isolation is enabled, otherwise
// just add to the DOM global.
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld('api', api)
  } catch (error) {
    console.error(error)
  }
} else {
  // @ts-ignore (define in dts)
  window.api = api
}

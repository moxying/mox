import { contextBridge, ipcRenderer } from 'electron'

// Custom APIs for renderer
export const api = {
  // agent
  // startAgent: () => ipcRenderer.send('startAgent'),
  // restartAgent: () => ipcRenderer.send('restartAgent'),

  // system
  getAppPath: () => ipcRenderer.invoke('getAppPath')
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
  window.electron = electronAPI
  // @ts-ignore (define in dts)
  window.api = api
}

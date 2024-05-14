import { app, shell, BrowserWindow, ipcMain } from 'electron'
import { join } from 'path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'

import icon from '../../resources/icon.png?asset'
import { launchInit, TOPIC_END, TOPIC_FAILED } from './launch'
import { config } from './config'
import { printDebugInfo } from './debug'
import { initUnhandled } from './unhandled'

console.info('[main]ui start...')
console.info(`[main]platform: ${process.platform}`)
initUnhandled()
printDebugInfo()

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  // Set app user model id for windows
  electronApp.setAppUserModelId('com.electron')

  // Default open or close DevTools by F12 in development
  // and ignore CommandOrControl + R in production.
  // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  // Create the browser window.
  const mainWindow = new BrowserWindow({
    show: false,
    width: config.launch.width,
    minWidth: config.launch.width,
    height: config.launch.height,
    minHeight: config.launch.height,
    titleBarStyle: 'hidden', // more: https://www.electronjs.org/zh/docs/latest/api/frameless-window
    titleBarOverlay: {
      color: 'rgba(0,0,0,0)',
      symbolColor: '#74b1be'
    },
    ...(process.platform === 'linux' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js')
    }
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    console.debug(
      `[main]dev mode, load mainWindow by loadURL from ${process.env['ELECTRON_RENDERER_URL']}`
    )
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
    mainWindow.webContents.openDevTools()
  } else {
    console.debug(`[main]production mode, load mainWindow from ../renderer/index.html}`)
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }

  launchInit(mainWindow)
    .then(() => {
      // resize window to normal
      mainWindow.setMinimumSize(config.width, config.height)
      mainWindow.setSize(config.width, config.height)
      mainWindow.center()
      // route to home page
      mainWindow.webContents.send('launch-event', {
        topic: TOPIC_END
      })
      console.info('[main]launchInit success')
    })
    .catch((error) => {
      console.error('[main]launchInit err:', error)
      if (error.message && error.message.toLowerCase().includes('launch error event sent')) {
        return
      }
      setTimeout(() => {
        mainWindow.webContents.send('launch-event', {
          topic: TOPIC_FAILED,
          data: {
            errMsg: `初始化错误：${error}`
          }
        })
      }, 500)
    })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  app.quit()
})

// In this file you can include the rest of your app"s specific main process
// code. You can also put them in separate files and require them here.

// get app dir
ipcMain.handle('getAppPath', () => {
  const appPath = app.getAppPath()
  console.info('[main]getAppPath exec: ', appPath)
  return appPath
})

ipcMain.on('openWebsite', (event, url) => {
  shell.openExternal(url)
})

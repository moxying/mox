import { BrowserWindow } from 'electron'
import { is, platform } from '@electron-toolkit/utils'

export const TOPIC_PROGRESS = 'progress'
export const TOPIC_FAILED = 'failed'
export const TOPIC_END = 'end'

export interface LaunchEventData {
  progressTip?: string
  progressDetail?: string
  progressValue?: number
  progressMax?: number
  errMsg?: string
}

export interface LaunchEvent {
  topic: string
  data?: any
}

export function launchInit(mainWindow: BrowserWindow): Promise<void> {
  return new Promise((resolve, reject) => {
    if (is.dev) {
      setTimeout(() => {
        mainWindow.webContents.send('launch-event', {
          topic: TOPIC_PROGRESS,
          data: {
            progressTip: '安装中...',
            progressDetail: '安装Git...',
            progressValue: 10,
            progressMax: 100
          }
        })
      }, 1000)
      setTimeout(() => {
        mainWindow.webContents.send('launch-event', {
          topic: TOPIC_PROGRESS,
          data: {
            progressTip: '安装中...',
            progressDetail: '安装Agent...',
            progressValue: 50,
            progressMax: 100
          }
        })
      }, 5000)
      setTimeout(() => {
        mainWindow.webContents.send('launch-event', {
          topic: TOPIC_PROGRESS,
          data: {
            progressTip: '安装中...',
            progressDetail: '安装ComfyUI...',
            progressValue: 80,
            progressMax: 100
          }
        })
        console.log('[main]dev mode, launch success')
        return resolve()
      }, 10000)
      return
    }

    if (platform.isLinux) {
      return reject('不支持Linux系统')
    }
    if (platform.isMacOS) {
      return reject('不支持MacOS系统')
    }
    console.info('[main]start launch init, cur platform:', platform.isLinux)
  })
}

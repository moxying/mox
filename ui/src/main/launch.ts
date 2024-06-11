import { BrowserWindow } from 'electron'
import { platform } from '@electron-toolkit/utils'

import { delay } from './util'
import { TOPIC_PROGRESS, Progress, ProgressMax } from './launch_common'
import { launchInitWin } from './launch_win'

export async function launchInit(mainWindow: BrowserWindow) {
  if (platform.isLinux) {
    throw new Error('暂不支持Linux系统')
  } else if (platform.isMacOS) {
    // throw new Error('暂不支持MacOS系统')
    return
  } else if (platform.isWindows) {
    await launchInitWin(mainWindow)
  } else {
    throw new Error('未知操作系统，暂不支持')
  }

  mainWindow.webContents.send('launch-event', {
    topic: TOPIC_PROGRESS,
    data: {
      progressTip: '更新成功',
      progressDetail: `更新成功`,
      progressValue: Progress.AllDone.valueOf(),
      progressMax: ProgressMax
    }
  })
  mainWindow.setProgressBar(1)
  await delay(1000)
}

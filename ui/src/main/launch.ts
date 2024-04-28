import { BrowserWindow, app } from 'electron'
import { is, platform } from '@electron-toolkit/utils'
import path from 'path'
import semver from 'semver'
import EventEmitter from 'events'
import prettyBytes from 'pretty-bytes'

import { config } from './config'
import {
  readJSONFile,
  writeJSONFile,
  createTempDir,
  downloadFile,
  delay,
  calculateSHA256,
  forceDeleteFile
} from './util'

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

enum Progress {
  CheckGitVersion = 1,
  DownloadGitNewVersion,
  CheckGitNewVersionSha256,
  ExtractGitNewVersion,
  UpdateGitNewVersion,
  CheckPythonEnvVersion,
  DownloadPythonEnvNewVersion,
  CheckPythonEnvNewVersionSha256,
  UpdatePythonEnvNewVersion
}
const ProgressMax = Object.keys(Progress).length / 2

const ExtraResourceDir = is.dev ? 'temp' : app.getPath('userData')
const GitPortableWinDir = path.join(ExtraResourceDir, 'git_portable_win')
const GitPortableWinInfoFile = path.join(ExtraResourceDir, 'git_portable_win.info.json')
const PythonEnvWinDir = path.join(ExtraResourceDir, 'python_env_win')
const PythonEnvWinInfoFile = path.join(ExtraResourceDir, 'python_env_win.info.json')

// eslint-disable-next-line @typescript-eslint/no-unused-vars
async function devMockInit(mainWindow) {
  await delay(1000)
  mainWindow.webContents.send('launch-event', {
    topic: TOPIC_PROGRESS,
    data: {
      progressTip: '安装中...',
      progressDetail: '安装Git...',
      progressValue: 10,
      progressMax: 100
    }
  })
  await delay(5000)
  mainWindow.webContents.send('launch-event', {
    topic: TOPIC_PROGRESS,
    data: {
      progressTip: '安装中...',
      progressDetail: '安装Agent...',
      progressValue: 50,
      progressMax: 100
    }
  })
  await delay(5000)
  mainWindow.webContents.send('launch-event', {
    topic: TOPIC_PROGRESS,
    data: {
      progressTip: '安装中...',
      progressDetail: '安装ComfyUI...',
      progressValue: 80,
      progressMax: 100
    }
  })
  console.info('[main]dev mode, launch success')
}

async function getGitPortableWinVersion() {
  try {
    const info = await readJSONFile(GitPortableWinInfoFile)
    console.info(`[main]get git_portable_win info: ${info}`)
    return info['version']
  } catch (error) {
    console.warn('[main]get git_portable_win failed, err is: ', error)
    return 'v0.0.0'
  }
}

async function updateGitPortableWin(mainWindow) {
  mainWindow.webContents.send('launch-event', {
    topic: TOPIC_PROGRESS,
    data: {
      progressTip: '检查更新中...',
      progressDetail: '检查Git...',
      progressValue: Progress.CheckGitVersion.valueOf(),
      progressMax: ProgressMax
    }
  })
  const curGitPortableWinVersion = await getGitPortableWinVersion()
  let needUpdateGitPortableWin = false
  try {
    needUpdateGitPortableWin = semver.gt(
      config.launch.winResource.git.version,
      curGitPortableWinVersion
    )
  } catch (error) {
    console.warn('[main]compare git_portable_win version failed, err is: ', error)
    needUpdateGitPortableWin = true
  }
  if (needUpdateGitPortableWin) {
    mainWindow.webContents.send('launch-event', {
      topic: TOPIC_PROGRESS,
      data: {
        progressTip: '更新Git...',
        progressDetail: '开始下载新版本..',
        progressValue: Progress.DownloadGitNewVersion.valueOf(),
        progressMax: ProgressMax
      }
    })
    console.info(
      `[main]git_portable_win need update, cur version is ${curGitPortableWinVersion}, will update to ${config.launch.winResource.git.version}`
    )
    const gitDownloadFilename =
      'temp_git_portable_win_' + config.launch.winResource.git.version + '.zip'
    const downloadEmitter = new EventEmitter()
    downloadEmitter.on('progress', (e) => {
      const receivedBytes = prettyBytes(e.receivedBytes)
      const totalBytes = prettyBytes(e.totalBytes)
      mainWindow.webContents.send('launch-event', {
        topic: TOPIC_PROGRESS,
        data: {
          progressTip: '更新Git...',
          progressDetail: `下载进度：${e.progress}% (${receivedBytes}/${totalBytes})`,
          progressValue: Progress.DownloadGitNewVersion.valueOf(),
          progressMax: ProgressMax
        }
      })
    })
    downloadEmitter.on('end', () => {
      console.info('[main]download git end')
      mainWindow.webContents.send('launch-event', {
        topic: TOPIC_PROGRESS,
        data: {
          progressTip: '更新Git...',
          progressDetail: `Git下载完成`,
          progressValue: Progress.DownloadGitNewVersion.valueOf(),
          progressMax: ProgressMax
        }
      })
    })
    downloadEmitter.on('error', (err) => {
      mainWindow.webContents.send('launch-event', {
        topic: TOPIC_PROGRESS,
        data: {
          progressTip: '更新Git...',
          progressDetail: `Git下载失败，错误原因：${err}`,
          progressValue: Progress.DownloadGitNewVersion.valueOf(),
          progressMax: ProgressMax
        }
      })
      throw new Error('launch error event sent')
    })
    const newGitArchiveFilename = path.join(ExtraResourceDir, gitDownloadFilename)
    await downloadFile(
      config.launch.winResource.git.downloadUrl,
      newGitArchiveFilename,
      downloadEmitter,
      true
    )

    // check sha256
    mainWindow.webContents.send('launch-event', {
      topic: TOPIC_PROGRESS,
      data: {
        progressTip: '更新Git...',
        progressDetail: `检查Sha256.。。`,
        progressValue: Progress.CheckGitNewVersionSha256.valueOf(),
        progressMax: ProgressMax
      }
    })
    const newGitArchiveSha256 = await calculateSHA256(newGitArchiveFilename)
    if (config.launch.winResource.git.sha256 !== newGitArchiveSha256) {
      await forceDeleteFile(newGitArchiveFilename)
      mainWindow.webContents.send('launch-event', {
        topic: TOPIC_PROGRESS,
        data: {
          progressTip: '更新Git...',
          progressDetail: `Git压缩包SHA256检查失败，已删除，请重新启动应用并更新...`,
          progressValue: Progress.DownloadGitNewVersion.valueOf(),
          progressMax: ProgressMax
        }
      })
      throw new Error('launch error event sent')
    }
    console.info('[main]check git archive sha256 done')

    console.info('[main]download git_portable_win success')
  }
}
async function updatePythonEnvWin(mainWindow) {}

async function launchInitWin(mainWindow) {
  // update git
  await updateGitPortableWin(mainWindow)
  // download python_env_win
  await updatePythonEnvWin(mainWindow)
  // download agent
}

export async function launchInit(mainWindow: BrowserWindow) {
  if (is.dev) {
    // await devMockInit(mainWindow)
    // return
  }

  if (platform.isLinux) {
    throw new Error('暂不支持MacOS系统')
  } else if (platform.isMacOS) {
    throw new Error('暂不支持Linux系统')
  } else if (platform.isWindows) {
    await launchInitWin(mainWindow)
  } else {
    throw new Error('未知操作系统，暂不支持')
  }
}

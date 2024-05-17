import { BrowserWindow, app, shell } from 'electron'
import { is, platform } from '@electron-toolkit/utils'
import path from 'path'
import semver from 'semver'
import EventEmitter from 'events'
import prettyBytes from 'pretty-bytes'

import { config } from './config'
import {
  readJSONFile,
  writeJSONFile,
  renameAndReplaceDirectorySync,
  downloadFile,
  extractZip,
  delay,
  calculateSHA256,
  forceDeleteFile,
  forceDeleteDir
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

export const ErrTriggered = 'launch error event sent'

enum Progress {
  CheckGitVersion = 1,
  DownloadGitNewVersion,
  CheckGitNewVersionSha256,
  ExtractGitNewVersion,
  SaveGitNewVersion,
  CheckPythonEnvVersion,
  DownloadPythonEnvNewVersion,
  CheckPythonEnvNewVersionSha256,
  ExtractPythonEnvNewVersion,
  SavePythonEnvNewVersion,
  AllDone
}
const ProgressMax = Object.keys(Progress).length / 2

const ExtraResourceDir = is.dev ? 'temp' : app.getPath('userData')
const GitPortableWinDir = path.join(ExtraResourceDir, 'git_portable_win')
const GitPortableWinInfoFile = path.join(ExtraResourceDir, 'git_portable_win.info.json')
const PythonEnvWinDir = path.join(ExtraResourceDir, 'python_env_win')
const PythonEnvWinInfoFile = path.join(ExtraResourceDir, 'python_env_win.info.json')

async function getGitPortableWinVersion() {
  try {
    const info = await readJSONFile(GitPortableWinInfoFile)
    console.info(`[main]get git_portable_win info, current version: ${info['version']}`)
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

  if (!needUpdateGitPortableWin) {
    console.info(`[main]git is updated, version: ${curGitPortableWinVersion}`)
    return
  }

  mainWindow.webContents.send('launch-event', {
    topic: TOPIC_PROGRESS,
    data: {
      progressTip: '更新Git...',
      progressDetail: `[${curGitPortableWinVersion} -> ${config.launch.winResource.git.version}] 开始下载新版本..`,
      progressValue: Progress.DownloadGitNewVersion.valueOf(),
      progressMax: ProgressMax
    }
  })
  console.info(
    `[main]git_portable_win need update, cur version is ${curGitPortableWinVersion}, will update to ${config.launch.winResource.git.version}`
  )

  // download git
  const gitDownloadFilename =
    'temp_git_portable_win_' + config.launch.winResource.git.version + '.zip'
  const newGitArchiveFilename = path.join(ExtraResourceDir, gitDownloadFilename)
  try {
    const downloadEmitter = new EventEmitter()
    downloadEmitter.on('progress', (e) => {
      const receivedBytes = prettyBytes(e.receivedBytes)
      const totalBytes = prettyBytes(e.totalBytes)
      mainWindow.webContents.send('launch-event', {
        topic: TOPIC_PROGRESS,
        data: {
          progressTip: '更新Git...',
          progressDetail: `[${curGitPortableWinVersion} -> ${config.launch.winResource.git.version}] 下载进度：${e.progress}% (${receivedBytes}/${totalBytes})`,
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
          progressDetail: `[${curGitPortableWinVersion} -> ${config.launch.winResource.git.version}] 下载完成`,
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
          progressDetail: `[${curGitPortableWinVersion} -> ${config.launch.winResource.git.version}] 下载失败，错误原因：${err}`,
          progressValue: Progress.DownloadGitNewVersion.valueOf(),
          progressMax: ProgressMax
        }
      })
      throw new Error(ErrTriggered)
    })

    await downloadFile(
      config.launch.winResource.git.downloadUrl,
      newGitArchiveFilename,
      downloadEmitter,
      true
    )
  } catch (error) {
    console.error(`[main]downloadFile failed, err: ${error}`)
    mainWindow.webContents.send('launch-event', {
      topic: TOPIC_PROGRESS,
      data: {
        progressTip: '更新Git...',
        progressDetail: `[${curGitPortableWinVersion} -> ${config.launch.winResource.git.version}] 下载失败，错误原因：${error}`,
        progressValue: Progress.DownloadGitNewVersion.valueOf(),
        progressMax: ProgressMax
      }
    })
    throw new Error(ErrTriggered)
  }

  // check sha256
  if (config.launch.winResource.git.checkSha256) {
    mainWindow.webContents.send('launch-event', {
      topic: TOPIC_PROGRESS,
      data: {
        progressTip: '更新Git...',
        progressDetail: `[${curGitPortableWinVersion} -> ${config.launch.winResource.git.version}] 检查Sha256...`,
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
          progressDetail: `[${curGitPortableWinVersion} -> ${config.launch.winResource.git.version}] 更新包SHA256检查失败，已删除，请重新启动应用并更新...`,
          progressValue: Progress.CheckGitNewVersionSha256.valueOf(),
          progressMax: ProgressMax
        }
      })
      throw new Error(ErrTriggered)
    }
    console.info('[main]check git archive sha256 done')
  }

  // extract git
  const gitExtractDir = path.join(
    ExtraResourceDir,
    'temp_git_portable_win_' + config.launch.winResource.git.version
  )
  try {
    await forceDeleteDir(gitExtractDir, true) // delete legacy dir
    console.info('[main]git, delete legacy dir done')

    const extractEmitter = new EventEmitter()
    extractEmitter.on('progress', (e) => {
      mainWindow.webContents.send('launch-event', {
        topic: TOPIC_PROGRESS,
        data: {
          progressTip: '更新Git...',
          progressDetail: `[${curGitPortableWinVersion} -> ${config.launch.winResource.git.version}] 解压进度：${e.progress}% (${e.extractedCount}/${e.totalCount})`,
          progressValue: Progress.ExtractGitNewVersion.valueOf(),
          progressMax: ProgressMax
        }
      })
    })
    extractEmitter.on('end', () => {
      console.info('[main]extra git end')
      mainWindow.webContents.send('launch-event', {
        topic: TOPIC_PROGRESS,
        data: {
          progressTip: '更新Git...',
          progressDetail: `[${curGitPortableWinVersion} -> ${config.launch.winResource.git.version}] 解压完成`,
          progressValue: Progress.ExtractGitNewVersion.valueOf(),
          progressMax: ProgressMax
        }
      })
    })
    extractEmitter.on('error', (err) => {
      mainWindow.webContents.send('launch-event', {
        topic: TOPIC_PROGRESS,
        data: {
          progressTip: '更新Git...',
          progressDetail: `[${curGitPortableWinVersion} -> ${config.launch.winResource.git.version}] 解压失败，错误原因：${err}`,
          progressValue: Progress.ExtractGitNewVersion.valueOf(),
          progressMax: ProgressMax
        }
      })
      throw new Error(ErrTriggered)
    })

    console.info('[main]start to extract git zip')
    await extractZip(newGitArchiveFilename, gitExtractDir, extractEmitter)
    await forceDeleteFile(newGitArchiveFilename)
    console.info('[main]extract git zip success')
  } catch (error) {
    console.error(`[main]extractZip git failed, err: ${error}`)
    mainWindow.webContents.send('launch-event', {
      topic: TOPIC_PROGRESS,
      data: {
        progressTip: '更新Git...',
        progressDetail: `[${curGitPortableWinVersion} -> ${config.launch.winResource.git.version}] 解压失败，错误原因：${error}`,
        progressValue: Progress.ExtractGitNewVersion.valueOf(),
        progressMax: ProgressMax
      }
    })
    throw new Error(ErrTriggered)
  }

  try {
    renameAndReplaceDirectorySync(gitExtractDir, GitPortableWinDir)
    // record git info
    await writeJSONFile(GitPortableWinInfoFile, {
      version: config.launch.winResource.git.version,
      updateTime: Date.now()
    })
  } catch (error) {
    console.error(`[main]save git failed, err: ${error}`)
    mainWindow.webContents.send('launch-event', {
      topic: TOPIC_PROGRESS,
      data: {
        progressTip: '更新Git...',
        progressDetail: `[${curGitPortableWinVersion} -> ${config.launch.winResource.git.version}] 保存结果失败，错误原因：${error}`,
        progressValue: Progress.SaveGitNewVersion.valueOf(),
        progressMax: ProgressMax
      }
    })
    throw new Error(ErrTriggered)
  }

  console.info('[main]update git_portable_win success')
}

async function getPythonEnvWinVersion() {
  try {
    const info = await readJSONFile(PythonEnvWinInfoFile)
    console.info(`[main]get PythonEnvWin info, current version: ${info['version']}`)
    return info['version']
  } catch (error) {
    console.warn('[main]get PythonEnvWin failed, err is: ', error)
    return 'v0.0.0'
  }
}

async function updatePythonEnvWin(mainWindow) {
  mainWindow.webContents.send('launch-event', {
    topic: TOPIC_PROGRESS,
    data: {
      progressTip: '检查更新中...',
      progressDetail: '检查Python环境版本...',
      progressValue: Progress.CheckPythonEnvVersion.valueOf(),
      progressMax: ProgressMax
    }
  })
  const curPythonEnvWinVersion = await getPythonEnvWinVersion()
  let needUpdate = false
  try {
    needUpdate = semver.gt(config.launch.winResource.pythonEnv.version, curPythonEnvWinVersion)
  } catch (error) {
    console.warn('[main]compare PythonEnvWin version failed, err is: ', error)
    needUpdate = true
  }

  if (!needUpdate) {
    console.info(`[main]git is updated, version: ${curPythonEnvWinVersion}`)
    return
  }

  mainWindow.webContents.send('launch-event', {
    topic: TOPIC_PROGRESS,
    data: {
      progressTip: '更新Python环境...',
      progressDetail: `[${curPythonEnvWinVersion} -> ${config.launch.winResource.pythonEnv.version}] 开始下载新版本..`,
      progressValue: Progress.DownloadPythonEnvNewVersion.valueOf(),
      progressMax: ProgressMax
    }
  })
  console.info(
    `[main]PythonEnvWin need update, cur version is ${curPythonEnvWinVersion}, will update to ${config.launch.winResource.pythonEnv.version}`
  )

  // download python env
  const pythonEnvDownloadFilename =
    'temp_python_env_win_' + config.launch.winResource.pythonEnv.version + '.zip'
  const newPythonEnvArchiveFilename = path.join(ExtraResourceDir, pythonEnvDownloadFilename)
  try {
    const downloadEmitter = new EventEmitter()
    downloadEmitter.on('progress', (e) => {
      const receivedBytes = prettyBytes(e.receivedBytes)
      const totalBytes = prettyBytes(e.totalBytes)
      mainWindow.webContents.send('launch-event', {
        topic: TOPIC_PROGRESS,
        data: {
          progressTip: '更新Python环境...',
          progressDetail: `[${curPythonEnvWinVersion} -> ${config.launch.winResource.pythonEnv.version}] 下载进度：${e.progress}% (${receivedBytes}/${totalBytes})`,
          progressValue: Progress.DownloadPythonEnvNewVersion.valueOf(),
          progressMax: ProgressMax
        }
      })
    })
    downloadEmitter.on('end', () => {
      console.info('[main]download git end')
      mainWindow.webContents.send('launch-event', {
        topic: TOPIC_PROGRESS,
        data: {
          progressTip: '更新Python环境...',
          progressDetail: `[${curPythonEnvWinVersion} -> ${config.launch.winResource.pythonEnv.version}] 下载完成`,
          progressValue: Progress.DownloadPythonEnvNewVersion.valueOf(),
          progressMax: ProgressMax
        }
      })
    })
    downloadEmitter.on('error', (err) => {
      mainWindow.webContents.send('launch-event', {
        topic: TOPIC_PROGRESS,
        data: {
          progressTip: '更新Python环境...',
          progressDetail: `[${curPythonEnvWinVersion} -> ${config.launch.winResource.pythonEnv.version}] 下载失败，错误原因：${err}`,
          progressValue: Progress.DownloadPythonEnvNewVersion.valueOf(),
          progressMax: ProgressMax
        }
      })
      throw new Error(ErrTriggered)
    })

    await downloadFile(
      config.launch.winResource.pythonEnv.downloadUrl,
      newPythonEnvArchiveFilename,
      downloadEmitter,
      true
    )
  } catch (error) {
    console.error(`[main]downloadFile failed, err: ${error}`)
    mainWindow.webContents.send('launch-event', {
      topic: TOPIC_PROGRESS,
      data: {
        progressTip: '更新Python环境...',
        progressDetail: `[${curPythonEnvWinVersion} -> ${config.launch.winResource.pythonEnv.version}] 下载失败，错误原因：${error}`,
        progressValue: Progress.DownloadPythonEnvNewVersion.valueOf(),
        progressMax: ProgressMax
      }
    })
    throw new Error(ErrTriggered)
  }

  // check sha256
  if (config.launch.winResource.pythonEnv.checkSha256) {
    mainWindow.webContents.send('launch-event', {
      topic: TOPIC_PROGRESS,
      data: {
        progressTip: '更新Python环境...',
        progressDetail: `[${curPythonEnvWinVersion} -> ${config.launch.winResource.pythonEnv.version}] 检查Sha256...`,
        progressValue: Progress.CheckPythonEnvNewVersionSha256.valueOf(),
        progressMax: ProgressMax
      }
    })
    const newPythonEnvArchiveSha256 = await calculateSHA256(newPythonEnvArchiveFilename)
    if (config.launch.winResource.pythonEnv.sha256 !== newPythonEnvArchiveSha256) {
      await forceDeleteFile(newPythonEnvArchiveFilename)
      mainWindow.webContents.send('launch-event', {
        topic: TOPIC_PROGRESS,
        data: {
          progressTip: '更新Python环境...',
          progressDetail: `[${curPythonEnvWinVersion} -> ${config.launch.winResource.pythonEnv.version}] 更新包SHA256检查失败，已删除，请重新启动应用并更新...`,
          progressValue: Progress.CheckPythonEnvNewVersionSha256.valueOf(),
          progressMax: ProgressMax
        }
      })
      throw new Error(ErrTriggered)
    }
    console.info('[main]check PythonEnv archive sha256 done')
  }

  // extract git
  const pythonEnvExtractDir = path.join(
    ExtraResourceDir,
    'temp_python_env_win_' + config.launch.winResource.pythonEnv.version
  )
  try {
    await forceDeleteDir(pythonEnvExtractDir, true) // delete legacy dir
    console.info('[main]PythonEnv, delete legacy dir done')

    const extractEmitter = new EventEmitter()
    extractEmitter.on('progress', (e) => {
      mainWindow.webContents.send('launch-event', {
        topic: TOPIC_PROGRESS,
        data: {
          progressTip: '更新Python环境...',
          progressDetail: `[${curPythonEnvWinVersion} -> ${config.launch.winResource.pythonEnv.version}] 解压进度：${e.progress}% (${e.extractedCount}/${e.totalCount})`,
          progressValue: Progress.ExtractPythonEnvNewVersion.valueOf(),
          progressMax: ProgressMax
        }
      })
    })
    extractEmitter.on('end', () => {
      console.info('[main]extra PythonEnv end')
      mainWindow.webContents.send('launch-event', {
        topic: TOPIC_PROGRESS,
        data: {
          progressTip: '更新Python环境...',
          progressDetail: `[${curPythonEnvWinVersion} -> ${config.launch.winResource.pythonEnv.version}] 解压完成`,
          progressValue: Progress.ExtractPythonEnvNewVersion.valueOf(),
          progressMax: ProgressMax
        }
      })
    })
    extractEmitter.on('error', (err) => {
      mainWindow.webContents.send('launch-event', {
        topic: TOPIC_PROGRESS,
        data: {
          progressTip: '更新Python环境...',
          progressDetail: `[${curPythonEnvWinVersion} -> ${config.launch.winResource.pythonEnv.version}] 解压失败，错误原因：${err}`,
          progressValue: Progress.ExtractPythonEnvNewVersion.valueOf(),
          progressMax: ProgressMax
        }
      })
      throw new Error(ErrTriggered)
    })

    console.info('[main]start to extract PythonEnv zip')
    await extractZip(newPythonEnvArchiveFilename, pythonEnvExtractDir, extractEmitter)
    await forceDeleteFile(newPythonEnvArchiveFilename)
  } catch (error) {
    console.error(`[main]extractZip PythonEnv failed, err: ${error}`)
    mainWindow.webContents.send('launch-event', {
      topic: TOPIC_PROGRESS,
      data: {
        progressTip: '更新Python环境...',
        progressDetail: `[${curPythonEnvWinVersion} -> ${config.launch.winResource.pythonEnv.version}] 解压失败，错误原因：${error}`,
        progressValue: Progress.ExtractPythonEnvNewVersion.valueOf(),
        progressMax: ProgressMax
      }
    })
    throw new Error(ErrTriggered)
  }

  try {
    renameAndReplaceDirectorySync(pythonEnvExtractDir, PythonEnvWinDir)
    // record git info
    await writeJSONFile(PythonEnvWinInfoFile, {
      version: config.launch.winResource.pythonEnv.version,
      updateTime: Date.now()
    })
  } catch (error) {
    console.error(`[main]save PythonEnv failed, err: ${error}`)
    mainWindow.webContents.send('launch-event', {
      topic: TOPIC_PROGRESS,
      data: {
        progressTip: '更新Python环境...',
        progressDetail: `[${curPythonEnvWinVersion} -> ${config.launch.winResource.pythonEnv.version}] 保存结果失败，错误原因：${error}`,
        progressValue: Progress.SavePythonEnvNewVersion.valueOf(),
        progressMax: ProgressMax
      }
    })
    throw new Error(ErrTriggered)
  }

  console.info('[main]update PythonEnv success')
}

async function launchInitWin(mainWindow) {
  // update git
  await updateGitPortableWin(mainWindow)
  // download python_env_win
  await updatePythonEnvWin(mainWindow)
  // download agent

  mainWindow.webContents.send('launch-event', {
    topic: TOPIC_PROGRESS,
    data: {
      progressTip: '更新成功',
      progressDetail: `更新成功`,
      progressValue: Progress.AllDone.valueOf(),
      progressMax: ProgressMax
    }
  })
}

export async function launchInit(mainWindow: BrowserWindow) {
  if (is.dev) {
    // for test
    await delay(5000)
  }

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
}

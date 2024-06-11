import { app } from 'electron'
import { is } from '@electron-toolkit/utils'
import path from 'path'

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

export enum Progress {
  // git
  CheckGitVersion = 1,
  DownloadGitNewVersion,
  CheckGitNewVersionSha256,
  ExtractGitNewVersion,
  SaveGitNewVersion,
  // python env
  CheckPythonEnvVersion,
  DownloadPythonEnvNewVersion,
  CheckPythonEnvNewVersionSha256,
  ExtractPythonEnvNewVersion,
  SavePythonEnvNewVersion,
  // agent
  UpdateAgent,
  AllDone
}
export const ProgressMax = Object.keys(Progress).length / 2

export const ExtraResourceDir = is.dev ? 'temp' : app.getPath('userData')
export const MoxDir = path.join(ExtraResourceDir, 'mox')

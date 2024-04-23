import path from 'path'
import { spawn } from 'child_process'

// win32 agent cwd
const agentCwd = path.join(process.cwd(), '/resources/extraResources', 'agent')
// win32 python exec
const python = path.join(
  process.cwd(),
  '/resources/extraResources/tools',
  'python-win/python-embeded/python.exe'
)

export function startAgent(): void {
  if (process.env.NODE_ENV === 'development') {
    console.info('[main]agent should start manually in development mode')
    return
  }
  console.info(`[main]start agent, agentCwd: ${agentCwd}, python exec: ${python}`)
  const agentProcess = spawn(python, ['main.py'], {
    cwd: agentCwd
  })
  agentProcess.stdout.on('data', function (chunk) {
    const log = chunk.toString().replace(/[\r\n]+$/, '')
    console.log(`${log}`)
  })
  agentProcess.stderr.on('data', function (chunk) {
    const log = chunk.toString().replace(/[\r\n]+$/, '')
    console.log(`${log}`)
  })
  agentProcess.on('close', (code) => {
    console.warn(`[main]agentProcess exited with code ${code}`)
  })
  console.debug('[main]agentProcess pid: ', agentProcess.pid)
}

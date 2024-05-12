import process from 'node:process'
import { app, dialog, clipboard } from 'electron'
import cleanStack from 'clean-stack'
import ensureError from 'ensure-error'

const options = {
  showDialog: true
}

// NOTE: The ES6 default for title will only be used if the error is invoked from the main process directly. When invoked via the renderer, it will use the ES6 default from invokeErrorHandler
const handleError = (title = `encountered an error`, error) => {
  error = ensureError(error)

  try {
    console.error(`[main]unhandled error: ${error}`)
  } catch (loggerError) {
    dialog.showErrorBox(
      'The `logger` option function in electron-unhandled threw an error',
      ensureError(loggerError).stack
    )
    return
  }

  if (options.showDialog) {
    const stack = cleanStack(error.stack)

    if (app.isReady()) {
      const buttons = ['确认', '复制错误原因']

      // Intentionally not using the `title` option as it's not shown on macOS
      const buttonIndex = dialog.showMessageBoxSync({
        type: 'error',
        buttons,
        defaultId: 0,
        noLink: true,
        message: title,
        detail: cleanStack(error.stack, { pretty: true })
      })

      if (buttonIndex === 1) {
        clipboard.writeText(`${title}\n${stack}`)
      }
    } else {
      dialog.showErrorBox(title, stack)
    }
  }
}

export const initUnhandled = () => {
  process.on('uncaughtException', (error) => {
    console.error('[main]uncaughtException error')
    handleError('发生错误', error)
  })

  process.on('unhandledRejection', (error) => {
    console.error('[main]unhandledRejection error')
    handleError('发生错误', error)
  })
}

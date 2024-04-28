import * as fs from 'fs'
import request from 'request'
import crypto from 'crypto'
import yauzl from 'yauzl'
import path from 'path'

export async function readJSONFile(filename: string): Promise<any> {
  return new Promise((resolve, reject) => {
    fs.readFile(filename, 'utf8', (err, data) => {
      if (err) {
        reject(err)
      } else {
        try {
          const json = JSON.parse(data)
          resolve(json)
        } catch (parseErr) {
          reject(parseErr)
        }
      }
    })
  })
}

export async function writeJSONFile(filename: string, data: any): Promise<void> {
  return new Promise((resolve, reject) => {
    fs.writeFile(filename, JSON.stringify(data, null, 2), (err) => {
      if (err) {
        reject(err)
      } else {
        resolve()
      }
    })
  })
}

export async function createTempDir(prefix: string): Promise<string> {
  return new Promise((resolve, reject) => {
    fs.mkdtemp(prefix, (err, folder) => {
      if (err) {
        reject(err)
      } else {
        resolve(folder)
      }
    })
  })
}

export async function downloadFile(url, dest, emitter, resume = false) {
  return new Promise<void>((resolve, reject) => {
    let receivedBytes = 0
    let totalBytes = 0

    const options = {
      method: 'GET',
      uri: url,
      headers: {}
    }

    // 如果支持断点续传并且之前已经下载过部分文件，则设置 Range 请求头
    if (resume && fs.existsSync(dest)) {
      const stats = fs.statSync(dest)
      options.headers['Range'] = `bytes=${stats.size}-`
      receivedBytes = stats.size
      console.info(`[main]downloadFile resume, receivedBytes: ${receivedBytes}`)
    }

    const req = request(options)

    const out = fs.createWriteStream(dest, { flags: resume ? 'a' : 'w' })
    req.pipe(out)

    req.on('response', (data) => {
      if (data.statusCode >= 400) {
        req.abort()
        // 404但断点续传有数据，大概率时文件已经在下载完了
        if (resume && data.statusCode === 404 && receivedBytes > 0) {
          return resolve()
        }
        const errMsg = `Request failed with status code: ${data.statusCode}, url: ${url}, dest: ${dest}`
        console.error(`[main]downloadFile, ${errMsg}`)
        try {
          emitter && emitter.emit('error', new Error(`${errMsg}`))
        } catch (error) {
          // console.error('[main]emit error: ', error)
        }
        return reject(errMsg)
      }
      totalBytes = parseInt(data.headers['content-length'])
      console.info(`[main]downloadFile statusCode: ${data.statusCode}, totalBytes: ${totalBytes}`)
      if (resume && data.headers['content-range']) {
        console.info(`[main]downloadFile resume, content-range: ${data.headers['content-range']}`)
        totalBytes += parseInt(data.headers['content-range'].split('/')[1])
      }
    })

    req.on('data', (chunk) => {
      // 更新接收到的字节数
      receivedBytes += chunk.length
      const progress = Math.floor((receivedBytes * 100) / totalBytes)

      try {
        emitter.emit('progress', {
          progress: progress,
          totalBytes: totalBytes,
          receivedBytes: receivedBytes
        })
      } catch (error) {
        // console.error('[main]emit error: ', error)
      }
    })

    req.on('end', () => {
      try {
        emitter && emitter.emit('end')
      } catch (error) {
        // console.error('[main]emit error: ', error)
      }
      return resolve()
    })

    req.on('error', (err) => {
      try {
        console.error(`[main] downloadFile err, url: ${url}, dest: ${dest}, err: ${err}`)
        emitter && emitter.emit('error', err)
      } catch (error) {
        // console.error('[main]emit error: ', error)
      }
      return reject(err)
    })
  })
}

export async function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms)
  })
}

// 计算文件的 SHA256 哈希值
export async function calculateSHA256(filename) {
  return new Promise((resolve, reject) => {
    const hash = crypto.createHash('sha256')
    const input = fs.createReadStream(filename)

    input.on('data', (chunk) => {
      hash.update(chunk)
    })

    input.on('end', () => {
      resolve(hash.digest('hex'))
    })

    input.on('error', (err) => {
      reject(err)
    })
  })
}

// 强制删除文件
export async function forceDeleteFile(filename) {
  return new Promise<void>((resolve, reject) => {
    fs.unlink(filename, (err) => {
      if (err) {
        if (err.code === 'ENOENT') {
          // 文件不存在，不需要删除
          resolve()
        } else {
          // 其他错误，拒绝删除
          reject(err)
        }
      } else {
        // 文件删除成功
        resolve()
      }
    })
  })
}

// 解压zip文件并获取解压进度
export async function extractZip(zipPath, destPath, emitter) {
  return new Promise<void>((resolve, reject) => {
    let extractedCount = 0

    yauzl.open(zipPath, { lazyEntries: true }, (err, zipFile) => {
      if (err) reject(err)

      zipFile.readEntry()

      zipFile.on('entry', (entry) => {
        const entryPath = path.join(destPath, entry.fileName)
        if (/\/$/.test(entry.fileName)) {
          // Directory file names end with '/'
          fs.mkdirSync(entryPath, { recursive: true })
          zipFile.readEntry()
        } else {
          // File entry
          zipFile.openReadStream(entry, (err, readStream) => {
            if (err) reject(err)
            readStream.on('end', () => {
              extractedCount++
              const progress = Math.floor((extractedCount * 100) / zipFile.entryCount)
              try {
                emitter.emit('progress', {
                  progress: progress,
                  totalCount: zipFile.entryCount,
                  extractedCount: extractedCount
                })
              } catch (error) {
                // console.error('[main]emit error: ', error)
              }
              zipFile.readEntry()
            })
            readStream.pipe(fs.createWriteStream(entryPath))
          })
        }
      })

      zipFile.on('end', () => {
        try {
          emitter && emitter.emit('end')
        } catch (error) {
          // console.error('[main]emit error: ', error)
        }
        resolve()
      })

      zipFile.on('error', (err) => {
        try {
          console.error(`[main] extractZip err, zipPath: ${zipPath}, err: ${err}`)
          emitter && emitter.emit('error', err)
        } catch (error) {
          // console.error('[main]emit error: ', error)
        }
        reject(err)
      })
    })
  })
}

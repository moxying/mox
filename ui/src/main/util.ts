import * as fs from 'fs'
import request from 'request'

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

export async function downloadFile(url, dest, emitter) {
  return new Promise<void>((resolve, reject) => {
    let receivedBytes = 0
    let totalBytes = 0

    const req = request({
      method: 'GET',
      uri: url
    })

    const out = fs.createWriteStream(dest)
    req.pipe(out)

    req.on('response', (data) => {
      // 获取总文件大小
      totalBytes = parseInt(data.headers['content-length'])
    })

    req.on('data', (chunk) => {
      // 更新接收到的字节数
      receivedBytes += chunk.length

      try {
        emitter.emit('progress', {
          totalBytes: totalBytes,
          receivedBytes: receivedBytes
        })
      } catch (error) {
        console.error('[main]emit error: ', error)
      }
    })

    req.on('end', () => {
      try {
        emitter && emitter.emit('end')
      } catch (error) {
        console.error('[main]emit error: ', error)
      }
      return resolve()
    })

    req.on('error', (err) => {
      try {
        emitter && emitter.emit('error', err)
      } catch (error) {
        console.error('[main]emit error: ', error)
      }
      reject(err)
    })
  })
}

export async function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms)
  })
}

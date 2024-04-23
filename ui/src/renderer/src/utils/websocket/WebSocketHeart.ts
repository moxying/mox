import { IWebSocketHeart, IWebSocketBean } from './websocket'

/**
 * WebSocket心跳机制
 */
export default class WebSocketHeart implements IWebSocketHeart {
  websocketbean: IWebSocketBean
  enableHeartbeat: boolean
  heartSend: string
  heartGet: string
  heartGapTime: number
  failNum: number = 0
  heartFailNum: number

  constructor(websocketbean: IWebSocketBean) {
    this.websocketbean = websocketbean
    this.enableHeartbeat = this.websocketbean.param.enableHeartbeat ?? false
    this.heartSend = this.websocketbean.param.heartSend ?? 'heartSend'
    this.heartGet = this.websocketbean.param.heartGet ?? 'heartGet'
    this.heartGapTime = this.websocketbean.param.heartGapTime ?? 30000
    this.heartFailNum = this.websocketbean.param.heartFailNum ?? 10
  }

  timer: number = null as any

  start = () => {
    if (!this.enableHeartbeat) return
    if (this.timer !== null) return
    this.failNum = 0
    this.timer = setInterval(() => {
      if (this.failNum >= this.heartFailNum) {
        this.stop()
        // FIXME
        this.websocketbean.onerror(new Event(''))
        return
      }
      this.websocketbean.send(this.heartSend)
      this.failNum++
    }, this.heartGapTime) as any
  }

  stop = () => {
    if (!this.enableHeartbeat) return
    clearInterval(this.timer)
    this.timer = null as any
  }

  onmessage = (ev: any) => {
    const messagePrefix = this.websocketbean.param.messagePrefix ?? ''
    const messageSuffix = this.websocketbean.param.messageSuffix ?? ''
    const heartGetMessage = messagePrefix + this.heartGet + messageSuffix
    if (ev === heartGetMessage) this.failNum = 0
  }
}

import { IWebSocketReconnect, IWebSocketBean } from './websocket'

/**
 * WebSocket重连机制和重连重发数据机制
 */
export default class WebSocketReconnect implements IWebSocketReconnect {
  /**
   * 开启状态
   */
  status: boolean

  /**
   * WebSocketBean对象
   */
  websocketbean: IWebSocketBean

  /**
   * 当前重连次数
   */
  num: number = 0

  /**
   * 最大重连次数
   */
  reconnectMaxNum: number = 10

  /**
   * 重连间隔时间
   */
  reconnectGapTime: number = 30000

  constructor(websocketbean: IWebSocketBean) {
    this.websocketbean = websocketbean
    this.status = websocketbean.param.needReconnect ?? false
    this.reconnectMaxNum = this.websocketbean.param.reconnectMaxNum ?? 10000
    this.reconnectGapTime = this.websocketbean.param.reconnectGapTime ?? 30000
  }

  timer: number = null as any

  /**
   * 开始尝试重连
   */
  start = () => {
    console.log('[WebSocketReconnect]start reconnect, reconnectGapTime:', this.reconnectGapTime)
    if (!this.status) return
    if (this.timer !== null) return
    this.num = 0
    if (this.websocketbean.param.onreconnect) this.websocketbean.param.onreconnect()
    this.timer = setInterval(() => {
      if (this.num >= this.reconnectMaxNum) {
        if (this.websocketbean.param.onFailReconnect) this.websocketbean.param.onFailReconnect()
        this.stop()
        return
      }
      this.websocketbean.start()
      console.log(`[WebSocketReconnect]reconnect after, num: ${this.num}`)
      this.num++
    }, this.reconnectGapTime) as any
  }

  /**
   * 停止重连
   */
  stop = () => {
    console.log('[WebSocketReconnect]stop reconnect')
    if (!this.status) return
    clearInterval(this.timer)
    this.timer = null as any
  }
}

import WebSocketBean from './WebSocketBean'
import { emitter, type WSEvent } from '@/utils/emitter'
export default class WSUtil {
  static ws: WebSocketBean
  static async init(url?: string) {
    if (!url) url = 'ws://127.0.0.1:7800/ws'
    this.ws = new WebSocketBean({
      url: url,
      needReconnect: true,
      reconnectGapTime: 3000,
      onmessage: (ev) => {
        const wsEvent = JSON.parse(ev.data) as WSEvent
        emitter.emit('wsEvent', wsEvent)
      },
      onreconnect: () => {
        console.log('ws start reconnect')
      },
      onFailReconnect: () => {
        console.log('ws reconnect failed')
      }
    })
    this.ws.start()
  }
}

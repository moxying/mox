import type { Emitter } from 'mitt'
import mitt from 'mitt'

export type WSEvent = {
  topic: string
  data?: any
}

type Events = {
  wsEvent: WSEvent
  showNetworkLoading: boolean // 通用网络加载
}

export const emitter: Emitter<Events> = mitt<Events>()

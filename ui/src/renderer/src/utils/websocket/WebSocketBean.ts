import {
  IWebSocketBean,
  IWebSocketBeanParam,
  IWebSocketReconnect,
  IWebSocketSend
} from './websocket'
import WebSocketHeart from './WebSocketHeart'
import WebSocketReconnect from './WebSocketReconnect'
import WebSocketSend from './WebSocketSend'
import { WebSocketStatusEnum } from './WebSocketEnum'

/**
 * WebSocket封装类
 * @param 封装了心跳机制 、重连机制
 */
export default class WebSocketBean implements IWebSocketBean {
  status: WebSocketStatusEnum = null as any
  websocket: WebSocket = null as any
  heart: WebSocketHeart = null as any
  reconnect: IWebSocketReconnect = null as any
  sendObj: IWebSocketSend = null as any
  param: IWebSocketBeanParam

  constructor(param: IWebSocketBeanParam) {
    this.param = param
  }

  onopen = async (ev: Event) => {
    //开启心跳
    this.heart.start()

    //通知连接成功或重连成功
    this.reconnect.stop()

    //调用生命周期
    if (this.param.onopen) await this.param.onopen(ev)

    //修改状态为已连接
    this.status = WebSocketStatusEnum.open

    //通知发送数据
    this.sendObj.onopen()
  }

  onmessage = (ev: MessageEvent<any>) => {
    //调用生命周期
    if (this.param.onmessage) this.param.onmessage(ev)

    this.heart.onmessage(ev.data)
  }

  onerror = (ev: Event) => {
    console.log('ws error, err', ev)
    //调用生命周期
    if (this.param.onerror) this.param.onerror(ev)
    //销毁对象
    this.close()
    //开始重连
    this.reconnect.start()
  }

  onclose = (ev: CloseEvent) => {
    let reason = ''
    // See https://www.rfc-editor.org/rfc/rfc6455#section-7.4.1
    if (ev.code == 1000)
      reason =
        'Normal closure, meaning that the purpose for which the connection was established has been fulfilled.'
    else if (ev.code == 1001)
      reason =
        'An endpoint is "going away", such as a server going down or a browser having navigated away from a page.'
    else if (ev.code == 1002)
      reason = 'An endpoint is terminating the connection due to a protocol error'
    else if (ev.code == 1003)
      reason =
        'An endpoint is terminating the connection because it has received a type of data it cannot accept (e.g., an endpoint that understands only text data MAY send this if it receives a binary message).'
    else if (ev.code == 1004)
      reason = 'Reserved. The specific meaning might be defined in the future.'
    else if (ev.code == 1005) reason = 'No status code was actually present.'
    else if (ev.code == 1006)
      reason =
        'The connection was closed abnormally, e.g., without sending or receiving a Close control frame'
    else if (ev.code == 1007)
      reason =
        'An endpoint is terminating the connection because it has received data within a message that was not consistent with the type of the message (e.g., non-UTF-8 [https://www.rfc-editor.org/rfc/rfc3629] data within a text message).'
    else if (ev.code == 1008)
      reason =
        'An endpoint is terminating the connection because it has received a message that "violates its policy". This reason is given either if there is no other sutible reason, or if there is a need to hide specific details about the policy.'
    else if (ev.code == 1009)
      reason =
        'An endpoint is terminating the connection because it has received a message that is too big for it to process.'
    else if (ev.code == 1010)
      // Note that this status code is not used by the server, because it can fail the WebSocket handshake instead.
      reason =
        "An endpoint (client) is terminating the connection because it has expected the server to negotiate one or more extension, but the server didn't return them in the response message of the WebSocket handshake. <br /> Specifically, the extensions that are needed are: " +
        ev.reason
    else if (ev.code == 1011)
      reason =
        'A server is terminating the connection because it encountered an unexpected condition that prevented it from fulfilling the request.'
    else if (ev.code == 1015)
      reason =
        "The connection was closed due to a failure to perform a TLS handshake (e.g., the server certificate can't be verified)."
    else reason = 'Unknown reason'
    console.log('ws closed, reason:', reason)
    //调用生命周期
    if (this.param.onclose) this.param.onclose(ev)
    //销毁对象
    this.close()
    //开始重连
    this.reconnect.start()
  }

  start = (param?: IWebSocketBeanParam) => {
    console.log('[WebSocketBean]ws bean start')

    //如果已经创建先关闭
    this.close()

    //使用新配置或者老配置
    if (param) this.param = param
    else param = this.param

    //创建连接
    this.websocket = new WebSocket(param.url)

    //修改状态为加载中
    this.status = WebSocketStatusEnum.load

    //绑定连接成功事件
    this.websocket.onopen = this.onopen
    //绑定消息接收事件
    this.websocket.onmessage = this.onmessage
    //绑定连接异常事件
    this.websocket.onerror = this.onerror
    //绑定连接关闭事件
    this.websocket.onclose = this.onclose

    //创建心跳
    this.heart = new WebSocketHeart(this)

    //创建重连，如果存在则跳过
    if (this.reconnect === null) this.reconnect = new WebSocketReconnect(this)

    //创建发送数据管理，如果存在则跳过
    if (this.sendObj === null) this.sendObj = new WebSocketSend(this)

    //监听窗口关闭事件，当窗口关闭时，主动去关闭websocket连接，防止连接还没断开就关闭窗口，server端会抛异常。
    window.addEventListener('beforeunload', this.dispose)
    console.log('[WebSocketBean]ws bean start end')
  }

  /**
   * 发送数据
   * @param data 数据对象，Object、Array、String
   */
  send(data: any, resend: boolean = false) {
    return this.sendObj?.send(data, resend)
  }

  /**
   * 销毁需要重发的数据信息
   * @param sendId
   */
  offsend = (sendId: string) => {
    this.sendObj?.offsend(sendId)
  }

  /**
   * 关闭socket，销毁绑定事件、心跳事件、窗口关闭事件，修改状态为已关闭
   */
  close = () => {
    console.log('[WebSocketBean] close start')
    if (this.websocket === null) return
    window.removeEventListener('beforeunload', this.dispose)
    //销毁绑定事件，关闭socket
    if (this.websocket) {
      this.websocket.onerror = null
      this.websocket.onmessage = null
      this.websocket.onclose = null
      this.websocket.onopen = null
      this.websocket.close()
      this.websocket = null as any
    }
    //销毁心跳事件
    if (this.heart) {
      this.heart.stop()
      this.heart = null as any
    }

    //修改状态为已关闭
    this.status = WebSocketStatusEnum.close
    console.log('[WebSocketBean] close end')
  }

  /**
   * 销毁所有对象
   */
  dispose = () => {
    this.close()
    if (this.reconnect) {
      this.reconnect.stop()
      this.reconnect = null as any
    }
    if (this.sendObj) {
      this.sendObj.clear()
      this.sendObj = null as any
    }
  }
}

import axios from 'axios' // 引入axios
import { ElMessage, ElNotification } from 'element-plus'
import { emitter } from '@/utils/emitter'

// console.log('baseURL: ', import.meta.env.VITE_BASE_API)

const http = axios.create({
  timeout: 3000
})
let activeAxios = 0
let timer
const showLoading = () => {
  activeAxios++
  if (timer) {
    clearTimeout(timer)
  }
  timer = setTimeout(() => {
    if (activeAxios > 0) {
      emitter.emit('showNetworkLoading', true)
    }
  }, 400)
}

const closeLoading = () => {
  activeAxios--
  if (activeAxios <= 0) {
    clearTimeout(timer)
    emitter.emit('showNetworkLoading', false)
  }
}
// http request 拦截器
http.interceptors.request.use(
  (config) => {
    showLoading()
    config.data = JSON.stringify(config.data)
    config.headers.set('Content-Type', 'application/json')
    return config
  },
  (error) => {
    closeLoading()
    ElMessage({
      showClose: true,
      message: error,
      type: 'error'
    })
    return error
  }
)

// http response 拦截器
http.interceptors.response.use(
  (response) => {
    closeLoading()
    if (response.data.code === 0) {
      if (response.data.msg) {
        ElNotification({
          title: '提示',
          message: response.data.msg,
          type: 'info'
        })
      }
    } else {
      ElNotification({
        title: '错误',
        message: response.data.msg,
        type: 'error'
      })
    }
    return response
  },
  (error) => {
    closeLoading()
    ElNotification({
      title: '错误',
      message: '接口错误',
      type: 'error'
    })
    console.log('api error', error)
    return error
  }
)

export default http

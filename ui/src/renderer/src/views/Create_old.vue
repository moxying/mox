<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import WSUtil from '@/utils/websocket/WSUtil'
import { emitter, type WSEvent } from '@/utils/emitter'
import { txt2imgAPI, getRandomPromptAPI } from '@/api/image'
import ProgressBar from '@/components/ProgressBar.vue'
import { AxiosError } from 'axios'

defineOptions({
  name: 'Create'
})

// splitter drag
const splitter = ref<HTMLElement | null>(null)
const topPane = ref<HTMLElement | null>(null)
const bottomPane = ref<HTMLElement | null>(null)
let isDragging = false
let startY = 0
const startDrag = (event: MouseEvent) => {
  if (event.target === splitter.value) {
    isDragging = true
    startY = event.clientY
    document.addEventListener('mousemove', handleDrag)
    document.addEventListener('mouseup', endDrag)
    splitter.value!.classList.add('dragging')
  }
}
const handleDrag = (event: MouseEvent) => {
  if (isDragging) {
    let deltaY = event.clientY - startY
    let newTopHeight = topPane.value!.offsetHeight + deltaY
    let newBottomHeight = bottomPane.value!.offsetHeight - deltaY

    // 确保高度不会小于最小值
    const minHeight = 170 // 根据需要设置最小高度
    if (newTopHeight < minHeight) {
      newTopHeight = minHeight
      deltaY = newTopHeight - topPane.value!.offsetHeight
      newBottomHeight = bottomPane.value!.offsetHeight - deltaY
    }
    if (newBottomHeight < minHeight) {
      newBottomHeight = minHeight
      deltaY = bottomPane.value!.offsetHeight - newBottomHeight
      newTopHeight = topPane.value!.offsetHeight + deltaY
    }

    topPane.value!.style.height = `${newTopHeight}px`
    bottomPane.value!.style.height = `${newBottomHeight}px`
    startY = event.clientY
  }
}
const endDrag = () => {
  isDragging = false
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', endDrag)
  splitter.value!.classList.remove('dragging')
}

// bottom
const activeBottomTab = ref('console')
const genRandomPrompt = async () => {
  const result = await getRandomPromptAPI()
  if (result instanceof AxiosError) {
    if (result.response) {
      const response = result.response
      console.log(`接口错误，原因：${response.statusText}，接口状态码：${response.status}`)
      return
    }
    if (result.message) {
      console.log(`接口错误，原因：${result.message}`)
      return
    }
    console.log(`接口错误，原因：${result.toJSON()}`)
    return
  }
  const response = result.data
  if (response.code != 0) {
    if (response.msg) {
      console.log(`接口错误，原因：${response.msg}`)
    }
    return
  }
  prompt.value = response.data ?? ''
}

// create
const prompt = ref('')
const negativePrompt = ref('')
const batchSize = ref(1)
const width = ref(1024)
const height = ref(1024)
const seed = ref(0)
enum CreateState {
  Waiting = 'Waiting',
  Doing = 'Doing',
  Done = 'Done',
  Failed = 'Failed'
}

const createState = ref<CreateState>(CreateState.Waiting)
const createProgress = ref(1)
const createProgressTip = ref('任务执行中...')
const images = ref<string[]>([])
const agentLogs = ref<string[]>([])
const agentLogsCap = 100
const startCreate = async () => {
  createState.value = CreateState.Doing
  createProgress.value = 1
  createProgressTip.value = '任务执行中...'
  const result = await txt2imgAPI({
    origin_prompt: prompt.value,
    ckpt_name: '',
    batch_size: batchSize.value,
    width: width.value,
    height: height.value,
    seed: seed.value
  })
  if (result instanceof AxiosError) {
    createState.value = CreateState.Failed
    if (result.response) {
      const response = result.response
      createProgressTip.value = `接口错误，原因：${response.statusText}，接口状态码：${response.status}`
      return
    }
    if (result.message) {
      createProgressTip.value = `接口错误，原因：${result.message}`
      return
    }
    createProgressTip.value = `接口错误，原因：${result.toJSON()}`
    return
  }
  const response = result.data
  if (response.code != 0) {
    createState.value = CreateState.Failed
    if (response.msg) {
      createProgressTip.value = response.msg
    }
    return
  }
}
const imageUrl = (filename: string) => {
  return window.location.origin + '/api/file/output/' + filename
}

// agent ws
const TOPIC_COMMON_STATUS = 'status'
const TOPIC_COMMON_LOG = 'log'
const TOPIC_GENIMAGE_PROGRESS = 'genimage_progress'
const TOPIC_GENIMAGE_END = 'genimage_end'
const TOPIC_GENIMAGE_FAILED = 'genimage_failed'
emitter.on('wsEvent', (e: WSEvent) => {
  const eventData = e.data
  switch (e.topic) {
    case TOPIC_GENIMAGE_PROGRESS:
      if (eventData.progress_value && eventData.progress_value_max) {
        createProgress.value = Math.floor(
          (100 * eventData.progress_value) / eventData.progress_value_max
        )
      }
      if (eventData.progress_tip) {
        createProgressTip.value = eventData.progress_tip
      }
      break
    case TOPIC_GENIMAGE_END:
      createProgressTip.value = '任务完成'
      createProgress.value = 100
      if (eventData.images) {
        images.value = eventData.images
      }
      setTimeout(() => {
        createState.value = CreateState.Done
      }, 300)
      break
    case TOPIC_GENIMAGE_FAILED:
      console.log('gen image failed', eventData)
      createState.value = CreateState.Failed
      if (eventData.err_msg) {
        createProgressTip.value = eventData.err_msg
      }
      break
    case TOPIC_COMMON_STATUS:
      break
    case TOPIC_COMMON_LOG:
      if (agentLogs.value.length >= agentLogsCap) {
        agentLogs.value.shift()
      }
      agentLogs.value.push(eventData.log)
      document.getElementById('newLog')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
      break
    default:
      console.log('other wsEvent:', e)
      break
  }
})

onMounted(() => {
  // agent ws
  WSUtil.init()
})

onUnmounted(() => {
  // drag splitter
  if (isDragging) {
    endDrag()
  }
  // agent ws
  WSUtil.ws.close()
  emitter.off('wsEvent')
})
const model = ref(true)
</script>

<template>
  <div class="app-create">
    <div class="app-create-config">
      <v-btn>Button</v-btn>
      <v-switch
        v-model="model"
        :label="`Switch: ${model.toString()}`"
        hide-details
        inset
      ></v-switch>
    </div>
    <div class="app-create-main">
      <div ref="topPane" class="app-create-top">
        <div
          v-if="[CreateState.Doing, CreateState.Failed].includes(createState)"
          class="create-progress"
        >
          <ProgressBar
            class="create-progress-bar"
            :container-bg-color="'#e0e0de'"
            :completed="createProgress"
          />
          <div
            class="create-progress-tip"
            :style="{ color: createState == CreateState.Failed ? 'rgb(250, 85, 96)' : '#a7b2c1' }"
          >
            {{ createProgressTip }}
          </div>
        </div>
        <div v-else-if="createState === CreateState.Done" class="image-view">
          <img :src="imageUrl(images[0])" />
        </div>
      </div>
      <div ref="splitter" class="splitter" @mousedown="startDrag"></div>
      <div ref="bottomPane" class="app-create-bottom">
        <el-tabs v-model="activeBottomTab" class="bottom-tabs">
          <el-tab-pane label="控制台" name="console" class="console-tab">
            <textarea v-model="prompt" placeholder="输入提示词..." />
            <div class="input-control">
              <button class="input-submit" @click="startCreate">生成</button>
              <button class="input-random" @click="genRandomPrompt">
                <i class="iconfont icon-touzi"></i>
              </button></div
          ></el-tab-pane>
          <el-tab-pane label="日志" name="log" class="log-tab">
            <div class="log-container">
              <p
                v-for="(item, index) in agentLogs"
                :id="agentLogs.length == index + 1 ? 'newLog' : ''"
                :key="index"
                class="log-item"
              >
                {{ item }}
              </p>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.app-create {
  display: flex;
  flex-direction: row;
  height: 100%;
  .app-create-config {
    display: flex;
    flex-direction: column;
    width: 16rem;
    height: 100%;
    background: $app-footer-color;
  }
  .app-create-main {
    display: flex;
    flex-direction: column;
    width: calc(100% - 16rem);
    height: 100%;
    position: relative;

    $app-create-bottom-height: 12rem;
    $splitter-height: 2px;
    .app-create-top {
      display: flex;
      flex-direction: row;
      height: calc(100% - $app-create-bottom-height - $splitter-height);

      .create-progress {
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 0 4rem 0 4rem;
        height: 100%;
        width: 100%;
        .create-progress-bar {
        }
        .create-progress-tip {
          font-size: small;
          color: $app-font-second-color;
          margin-top: 0.5rem;
          align-self: center;
          max-width: 38rem; /* 设置最大宽度 */
          // overflow: hidden; /* 溢出部分隐藏 */
          // white-space: nowrap; /* 不换行 */
          // text-overflow: ellipsis; /* 文本溢出时显示省略号 */
        }
      }
      .image-view {
        position: relative; /* 设置父元素为相对定位，以便后续绝对定位的子元素相对于父元素定位 */
        width: 100%;
        height: 100%;
        img {
          max-width: 100%; /* 设置图像的最大宽度为父元素的宽度 */
          max-height: 100%; /* 设置图像的最大高度为父元素的高度 */
          height: auto; /* 让图像的高度自动调整以保持纵横比 */
          display: block; /* 让图像成为块级元素，以便水平居中 */
          position: absolute; /* 将图像设置为绝对定位，以便水平和垂直居中 */
          top: 50%; /* 图像垂直居中 */
          left: 50%; /* 图像水平居中 */
          transform: translate(-50%, -50%); /* 通过平移变换实现水平和垂直居中 */
          animation: fadeIn 2s ease forwards; /* 使用fadeIn动画，持续2秒，渐变到透明度为1 */
        }
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
      }
    }

    .splitter {
      width: 100%;
      height: $splitter-height; // 分割线高度
      background-color: #474e55;
      cursor: ns-resize;
      user-select: none;
      z-index: 10;

      &:hover,
      &.dragging {
        background-color: #69737d;
        height: 3px;
      }
    }
    .app-create-bottom {
      display: flex;
      flex-direction: row;
      justify-content: start;
      width: 100%;
      height: $app-create-bottom-height;
      overflow-y: auto;
      padding-left: 0.8rem;
      padding-right: 0.8rem;

      .el-tabs {
        width: 100%;
      }
      :deep(.el-tabs__nav-wrap::after) {
        height: 0;
      }
      :deep(.el-tabs__item) {
        color: $app-font-second-color;
        &:hover {
          color: $app-font-first-color;
        }
      }
      :deep(.el-tabs__item.is-active) {
        color: $app-font-first-color;
      }
      :deep(.el-tabs__active-bar) {
        @extend %app-gradient-bg;
      }
      :deep(.el-tabs__content) {
        height: calc(100% - var(--el-tabs-header-height) - 15px);
      }

      .bottom-tabs {
        .console-tab {
          display: flex;
          flex-direction: row;
          height: 100%;

          textarea {
            height: 100%;
            width: 100%;
            padding: 0.5rem;
            resize: none;
            background: $app-input-background;
            border-radius: 6px;
            outline: none;

            &:focus {
              border: 1px solid $app-input-border-color;
            }
          }

          .input-control {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: start;
            width: 10rem;
            padding-left: 1rem;

            .input-submit {
              @extend %app-gradient-button;
              width: 100%;
            }

            .input-random {
              align-self: center;
              margin-top: 1rem;
              border-radius: 10px;
              background-color: rgb(47, 53, 63);
              width: 3.5rem;
              height: 3.5rem;
              display: flex;
              justify-content: center;
              align-items: center;
              position: relative;
              overflow: hidden;
              transition:
                background-color 0.3s linear,
                border 0.3s linear;
              .iconfont {
                font-size: 2.8rem;
                font-weight: bold;
                &:before {
                  @extend %app-gradient-bg-text;
                }
              }
              &:hover {
                box-shadow: rgba(161, 128, 255, 0.6) 0px 0px calc(1rem) 0px;
                animation-timing-function: ease-out;
                animation-duration: 200ms;
              }
              &:after {
                content: '';
                display: flex;
                position: absolute;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
                pointer-events: none;
                background-image: radial-gradient(circle, #000 10%, rgba(0, 0, 0, 0) 10.01%);
                background-repeat: no-repeat;
                background-position: 50%;
                transform: scale(10);
                opacity: 0;
                transition:
                  transform 0.5s,
                  opacity 1s;
              }
              &:active:after {
                transform: scale(0);
                opacity: 0.2;
                transition: 0s;
              }
            }
          }
        }
        .log-tab {
          display: flex;
          flex-direction: row;
          height: 100%;
          position: relative;
          .log-container {
            height: 100%;
            width: 100%;
            position: absolute;
            overflow-y: auto;
            p {
              font-size: small;
              color: $app-font-second-color;
            }
            &::-webkit-scrollbar {
              width: 8px;
              height: 10px;
              /**/
            }
            &::-webkit-scrollbar-track {
              background: transparent;
            }
            &::-webkit-scrollbar-thumb {
              background: #bfbfbf79;
              border-radius: 2px;
            }
            &::-webkit-scrollbar-thumb:hover {
              background: #bfbfbf;
            }
          }
        }
      }
    }
  }
}
</style>

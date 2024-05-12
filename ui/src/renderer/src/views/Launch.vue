<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ProgressBar from '@/components/ProgressBar.vue'

defineOptions({
  name: 'Launch'
})
const router = useRouter()

const progress = ref(1)
const progressTip = ref('更新中...')
const progressDetail = ref('')
const progressErrMsg = ref(null)

interface LaunchEvent {
  topic: string
  data?: any
}
const TOPIC_PROGRESS = 'progress'
const TOPIC_FAILED = 'failed'
const TOPIC_END = 'end'
window.api.onLaunchEvent((e: LaunchEvent) => {
  console.log('launch event', e)
  switch (e.topic) {
    case TOPIC_PROGRESS:
      progressTip.value = e.data.progressTip
      progressDetail.value = e.data.progressDetail
      progress.value = Math.floor((100 * e.data.progressValue) / e.data.progressMax)
      console.log('progress update to', progress.value)
      break
    case TOPIC_FAILED:
      progressErrMsg.value = e.data.errMsg
      break
    case TOPIC_END:
      console.log('onLaunchEvent end')
      router.push({
        path: '/create'
      })
      break
    default:
      console.log('unknow event topic')
      break
  }
})

const openHelp = () => {
  window.api.openWebsite('https://gitcode.com/moxying/mox/discussion')
}
</script>

<template>
  <div class="launch-content">
    <div class="background-img"></div>
    <div class="progress-tip">{{ progressTip }}</div>
    <ProgressBar class="progress-bar" :container-bg-color="'#e0e0de'" :completed="progress" />
    <div
      class="progress-detail"
      :style="{ color: progressErrMsg ? 'rgb(250, 85, 96)' : '#a7b2c1' }"
    >
      {{ progressDetail }}
    </div>
    <div class="circle-button" @click="openHelp">?</div>
  </div>
</template>

<style lang="scss" scoped>
.launch-content {
  display: flex;
  flex-direction: column;
  justify-content: start;
  align-items: center;
  position: relative;
  padding: 2rem 1rem 2rem 1rem;
  width: 100;
  height: 100%;

  .background-img {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url('@/assets/TreeMan.webp');
    background-size: cover;
    background-position: center;
    opacity: 0.5; /* 图片的透明度 */
    z-index: -1; /* 将背景图片置于最底层 */
  }

  .progress-tip {
    margin-top: 5rem;
  }

  .progress-bar {
    margin-top: 0.1rem;
    margin-bottom: 0.1rem;
    width: 100%;
  }

  .progress-detail {
    align-self: start;
    margin-top: 0.1rem;
    font-size: small;
    overflow: hidden;
    text-overflow: ellipsis;
    -webkit-box-orient: vertical;
    display: -webkit-box;
    -webkit-line-clamp: 5; /* 控制显示行数 */
    max-width: 99%; /* 限制内容宽度 */
    z-index: 1; /* 将子元素置于最顶层 */
  }
  .circle-button {
    position: absolute;
    right: 0.4rem;
    bottom: 0.4rem;
    z-index: 999;

    width: 1.4rem;
    height: 1.4rem;
    border-radius: 50%;
    background: linear-gradient(
        81.02deg,
        rgb(250, 85, 96) -23.47%,
        rgb(177, 75, 244) 45.52%,
        rgb(77, 145, 255) 114.8%
      )
      border-box border-box;
    color: $app-font-first-color;
    font-size: 0.9rem;
    font-weight: bold;
    text-align: center; /* 文本居中 */
    &:hover {
      box-shadow: rgba(161, 128, 255, 0.6) 0px 0px calc(1rem) 0px;
      animation-timing-function: ease-out;
      animation-duration: 200ms;
      cursor: pointer;
    }
  }
}
</style>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
defineOptions({
  name: 'Launch'
})
const router = useRouter()

const msg = ref('')

interface LaunchEvent {
  topic: string
  data?: any
}
const TOPIC_PROGRESS = 'progress'
const TOPIC_FAILED = 'failed'
const TOPIC_END = 'end'
window.api.onLaunchEvent((e: LaunchEvent) => {
  console.log('onLaunchEvent', e)
  switch (e.topic) {
    case TOPIC_PROGRESS:
      msg.value = e.data.progressDetail
      break
    case TOPIC_FAILED:
      msg.value = e.data.errMsg
      break
    case TOPIC_END:
      console.log('onLaunchEvent end')
      router.push({
        path: '/create'
      })
      break
    default:
      break
  }
})
</script>

<template>
  <div class="launch-content">{{ msg }}</div>
</template>

<style lang="scss" scoped>
.launch-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100;
  height: 100%;
  background: $app-header-color;
  -webkit-app-region: drag;
}
</style>

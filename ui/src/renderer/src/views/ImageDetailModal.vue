<script setup lang="ts">
import { ref, watch } from 'vue'
import { SDImage, SDImageFragment } from '@/api/image'
import dayjs from 'dayjs'

defineOptions({
  name: 'ImageDetailModal'
})
const model = defineModel<boolean>({ required: true, default: false })
const props = defineProps({
  sdImage: {
    type: Object as () => SDImage,
    require: true
  },
  fragments: {
    type: Array as () => SDImageFragment[],
    require: true
  }
})

// image switch
const images = ref<SDImage[]>([])
const curImageIndex = ref(-1)
watch(model, (newModel) => {
  if (!newModel) {
    return
  }
  console.log('model change to true and re cal images')
  if (props.fragments) {
    for (const fragment of props.fragments) {
      for (const sdImage of fragment.list) {
        if (sdImage.id === props.sdImage?.id) {
          curImageIndex.value = images.value.length
        }
        images.value.push(sdImage)
      }
    }
  }
})

const handleWheel = (e: WheelEvent) => {
  e.preventDefault()
  if (e.deltaY > 0) {
    nextImage(true)
  } else {
    nextImage(false)
  }
}
const nextImage = (next: boolean) => {
  if (next) {
    curImageIndex.value = Math.min(curImageIndex.value + 1, images.value.length - 1)
  } else {
    curImageIndex.value = Math.max(curImageIndex.value - 1, 0)
  }
}

const imageUrl = (filename: string | undefined) => {
  return window.location.origin + '/api/file/output/' + filename
}
</script>

<template>
  <div v-if="model" class="modal-container" @wheel="handleWheel">
    <div class="left-panel">
      <img :src="imageUrl(images[curImageIndex].uuid + '.' + images[curImageIndex].format)" />
    </div>
    <div class="right-panel">
      <div class="detail-panel">
        <div class="image-info">
          <div class="image-date">
            {{ dayjs(images[curImageIndex].created_at).fromNow() }}
          </div>
          <div class="image-prompt">{{ images[curImageIndex].origin_prompt }}</div>
        </div>
        <div class="image-action"></div>
      </div>
      <div class="extra-panel">
        <div class="close-modal" @click="model = !model">
          <i class="iconfont icon-close"></i>
        </div>
        <div class="images-preview"></div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.modal-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: $app-background-color;
  display: flex;
  flex-direction: row;

  .left-panel {
    display: flex;
    flex: auto;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;
    padding: 2rem;

    img {
      width: auto;
      height: auto;
      max-width: 100%;
      max-height: 100%;
      border-radius: 1rem;
    }
  }
  .right-panel {
    width: 25rem;
    flex-shrink: 0;
    height: 100%;
    background-color: $app-black-1;
    display: flex;
    flex-direction: row;

    .detail-panel {
      width: 19rem;
      flex-shrink: 0;
      display: flex;
      flex-direction: column;
      justify-content: end;
      padding: 1rem 0 1rem 1rem;

      .image-info {
        flex: auto;
        display: flex;
        flex-direction: column;

        .image-date {
          color: $app-font-second-color;
        }
        .image-prompt {
          margin-top: 0.5rem;
          height: 100%;
          color: $app-font-first-color;
        }
      }
      .image-action {
        height: 25rem;
        flex-shrink: 0;
      }
    }
    .extra-panel {
      width: 6rem;
      flex-shrink: 0;
      display: flex;
      flex-direction: column;

      .close-modal {
        height: 5rem;
        flex-shrink: 0;
        display: flex;
        flex-direction: row-reverse;
        padding: 1rem 1rem 0 0;

        i {
          background-color: $app-black-3;
          border-radius: 0.8rem;
          width: 3rem;
          height: 3rem;
          display: flex;
          justify-content: center;
          align-items: center;

          &:hover {
            background-color: $app-black-4;
          }
        }
        .iconfont {
          font-size: 1rem;
          color: $app-font-first-color;
          font-weight: lighter;
        }
      }
      .images-preview {
      }
    }
  }
}
</style>

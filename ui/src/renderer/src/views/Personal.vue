<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import {
  SDImage,
  getImageListAsFragmentAPI,
  type SDImageFragment,
  deleteImageAPI
} from '@/api/image'
import { AxiosError } from 'axios'
import LoadMoreBar from '@/components/LoadMoreBar.vue'
import ContextMenu from '@imengyu/vue3-context-menu'
import { MenuOptions } from '@imengyu/vue3-context-menu'
import ImageDetailModal from './ImageDetailModal.vue'

defineOptions({
  name: 'Personal'
})

// images
const fragments = ref<SDImageFragment[]>([])
const page = ref(1)
const pageSize = 60
const total = ref(0)
const hasMoreImages = ref(true)
const timestampFilter = ref(Math.floor(Date.now() / 1000))
const imageUrl = (filename: string) => {
  return window.location.origin + '/api/file/output/' + filename
}
const isGetTableData = ref(false)
const getTableData = () => {
  isGetTableData.value = true
  getImageListAsFragmentAPI({
    page: page.value,
    page_size: pageSize,
    timestamp_filter: timestampFilter.value
  }).then((result) => {
    if (result instanceof AxiosError) {
      if (result.response) {
        const response = result.response
        console.log(`接口错误，原因：${response.statusText}，接口状态码：${response.status}`)
        isGetTableData.value = false
        return
      }
      if (result.message) {
        console.log(`接口错误，原因：${result.message}`)
        isGetTableData.value = false
        return
      }
      console.log(`接口错误，原因：${result.toJSON()}`)
      isGetTableData.value = false
      return
    }
    const response = result.data
    if (response.code != 0) {
      console.log(`code != 0, 原因：${response.msg}`)
      isGetTableData.value = false
      return
    }
    if (response.data?.list && response.data?.list.length !== 0) {
      // check merge or not
      if (
        fragments.value.length != 0 &&
        fragments.value[fragments.value.length - 1].date == response.data.list[0].date
      ) {
        fragments.value[fragments.value.length - 1].list.push(...response.data.list[0].list)
        response.data.list.shift()
      }
      fragments.value.push(...response.data.list)
      page.value = response.data.page + 1
      total.value = response.data.total
      hasMoreImages.value =
        response.data.cur_total + (response.data.page - 1) * pageSize == total.value ? false : true
    }
    // add all artworks to image ob
    nextTick(() => {
      const allImages = document.querySelectorAll('img[data-src]')
      allImages.forEach((img) => {
        imageOb.observe(img)
      })
    })
    isGetTableData.value = false
  })

  // ob image: lazy load when in view
  const imageOb = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement
          const src = img.getAttribute('data-src')
          if (src) {
            img.src = src
            img.removeAttribute('data-src')
            imageOb.unobserve(img)
          }
        }
      }
    },
    { threshold: 0, root: null, rootMargin: '0px' }
  )
  // ob load more
  const loadMoreOb = new IntersectionObserver(
    (entries) => {
      const entry = entries[0]
      if (entry.isIntersecting) {
        if (!isGetTableData.value) {
          getTableData()
        }
      }
    },
    {
      threshold: 0,
      root: null,
      rootMargin: '0px'
    }
  )
  const loadMoreDiv = document.querySelector('.load-more')
  if (loadMoreDiv) {
    loadMoreOb.observe(loadMoreDiv)
  }
}

// image detail
const showImageDetailModal = ref(false)
const curDetailImage = ref<SDImage>()
const showImageDetail = (sdImage: SDImage) => {
  showImageDetailModal.value = true
  curDetailImage.value = sdImage
}

// context menu
const onImageContextMenu = (
  e: MouseEvent,
  sdImage: SDImage,
  outerIndex: number,
  innerIndex: number
) => {
  //prevent the browser's default menu
  e.preventDefault()
  e.stopPropagation()
  //show our menu
  ContextMenu.showContextMenu({
    items: [
      {
        label: '删除',
        icon: 'icon-delete',
        onClick: async () => {
          const result = await deleteImageAPI(sdImage.uuid)
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
            console.log(`code != 0, 原因：${response.msg}`)
            return
          }
          fragments.value[outerIndex].list.splice(innerIndex, 1)
          console.log('image delete done', sdImage.id)
        }
      }
    ],
    theme: 'mac dark',
    iconFontClass: 'iconfont',
    zIndex: 3,
    minWidth: 140,
    x: e.x,
    y: e.y
  } as MenuOptions)
}

onMounted(() => {
  getTableData()
})
</script>

<template>
  <div class="app-personal">
    <div class="artworks">
      <div class="outer-grid-container">
        <div
          v-for="(fragment, outerIndex) in fragments"
          :key="fragment.date"
          class="outer-grid-item"
        >
          <div class="fragment-bar">{{ fragment.date }}</div>
          <div class="inner-grid-container">
            <div
              v-for="(sdImage, innerIndex) in fragment.list"
              :key="sdImage.id"
              class="inner-grid-item"
              @contextmenu="onImageContextMenu($event, sdImage, outerIndex, innerIndex)"
            >
              <img
                src="@/assets/default-artwork.png"
                :data-src="imageUrl(sdImage.name)"
                @click="showImageDetail(sdImage)"
              />
            </div>
          </div>
        </div>
      </div>
      <div v-if="hasMoreImages" class="load-more-wrap">
        <LoadMoreBar class="load-more" />
      </div>
    </div>

    <!-- image detail modal -->
    <ImageDetailModal
      v-model="showImageDetailModal"
      :sd-image="curDetailImage && curDetailImage"
      :fragments="fragments"
    />
  </div>
</template>

<style lang="scss" scoped>
.app-personal {
  width: 100%;
  height: 100%;
  position: relative;

  .artworks {
    width: 100%;
    height: 100%;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
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
    .outer-grid-container {
      display: grid;
      grid-template-columns: 100%;
      row-gap: 2rem;
      .outer-grid-item {
        .fragment-bar {
          margin-bottom: 0.8rem;
        }
        .inner-grid-container {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr));
          gap: 0.5rem;
          .inner-grid-item {
            position: relative;
            width: 100%;
            overflow: hidden;
            background: $app-black-1;
            border-radius: 10px;

            img {
              position: absolute;
              top: 50%;
              left: 50%;
              transform: translate(-50%, -50%);
              width: auto;
              height: auto;
              max-width: 100%;
              max-height: 100%;
            }
            // 撑开高度
            &::after {
              content: '';
              display: block;
              margin-top: 100%;
            }
          }
        }
      }
    }
    .load-more-wrap {
      width: 100%;
      margin-top: 1rem;
      margin-bottom: 1rem;
      display: flex;
      justify-content: center;
      .load-more {
        width: 25px;
      }
    }
  }
}
</style>

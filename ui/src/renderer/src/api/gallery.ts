// import { http } from '@/utils/http'

export interface ArtworkListRequest {
  page: number
  pageSize: number
}
export interface ArtworkListResponse {
  code: number
  msg?: string
  data: [
    {
      id: string
      name: string
      src: string
    }
  ]
}

/**
 * 艺术作品的类型声明
 */
export interface ArtworkInfo {
  id: string
  src: string
}

/** 登录 */
export const artworkListAPI = (request?: ArtworkListRequest) => {
  // return http.request<ArtworkListResponse>("post", "/login", { data });
  const artworks = <ArtworkInfo[]>[]
  const sizes = [300, 400, 500, 600, 700]
  function randomPick(array) {
    // 确保数组不为空
    if (!Array.isArray(array) || array.length === 0) {
      throw new Error('Array must be non-empty')
    }

    // 生成一个随机索引
    const randomIndex = Math.floor(Math.random() * array.length)

    // 返回随机选中的元素
    return array[randomIndex]
  }
  const startIndex = ((request?.page ?? 1) - 1) * (request?.pageSize ?? 10)
  const endIndex = startIndex + (request?.pageSize ?? 10)
  for (let i = startIndex; i < endIndex; i++) {
    artworks.push({
      id: i.toString(),
      name: i.toString(),
      src:
        'https://picsum.photos/id/' +
        i.toString() +
        '/' +
        randomPick(sizes).toString() +
        '/' +
        randomPick(sizes).toString()
    })
  }
  return new Promise((resolve) => {
    resolve({
      code: 0,
      data: artworks
    })
  })
}

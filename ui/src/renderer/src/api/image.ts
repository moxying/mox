import http from '@/utils/http'

export interface Txt2imgRequest {
  origin_prompt: string
  ckpt_name: string
  negative_prompt?: string
  seed?: number
  steps?: number
  cfg?: number
  sampler_name?: string
  scheduler?: string
  denoise?: number
  batch_size?: number
  width?: number
  height?: number
  task_tags?: object
}

export interface Txt2imgResponse {
  code: number
  msg?: string
  data?: {
    id?: string
  }
}

export interface GetImageListAsFragmentRequest {
  page: number
  page_size: number
  timestamp_filter: number
}

export interface SDImage {
  id: number
  created_at: string
  updated_at: string
  uuid: string
  format: string
  origin_prompt: string
  image_file_deleted: boolean
  task_type: string
  task_tags: object

  prompt: string
  negative_prompt: string
  width: number
  height: number
  seed: number
  steps: number
  cfg: number
  sampler_name: string
  scheduler: string
  denoise: number
  ckpt_name: string
}
export interface SDImageFragment {
  date: string
  list: SDImage[]
}

export interface GetImageListAsFragmentResponse {
  code: number
  msg?: string
  data?: {
    page: number
    page_size: number
    total: number
    cur_total: number
    list?: SDImageFragment[]
  }
}

export interface GetRandomPromptResponse {
  code: number
  msg?: string
  data?: string
}
export interface DeleteImageResponse {
  code: number
  msg?: string
  data?: string
}

export const txt2imgAPI = async (request?: Txt2imgRequest) => {
  return await http<Txt2imgResponse>({ url: '/api/image/txt2img', method: 'post', data: request })
}

export const getImageListAsFragmentAPI = async (request?: GetImageListAsFragmentRequest) => {
  return await http<GetImageListAsFragmentResponse>({
    url: '/api/image/list/fragment',
    method: 'post',
    data: request
  })
}

export const getRandomPromptAPI = async () => {
  return await http<GetRandomPromptResponse>({
    url: '/api/image/prompt/random',
    method: 'get'
  })
}

export const deleteImageAPI = async (imageUUID: string) => {
  return await http<DeleteImageResponse>({
    url: '/api/image/' + imageUUID,
    method: 'delete'
  })
}

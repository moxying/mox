import http from '@/utils/http'

export interface GenImageRequest {
  prompt: string
  negative_prompt?: string
  batch_size?: number
  width?: number
  height?: number
  seed?: number
}

export interface GenImageResponse {
  code: number
  msg?: string
  data?: {
    task_uuid?: string
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
  task_uuid: string
  name: string
  time_cost: number
  origin_prompt: string
  prompt: string
  negative_prompt: string
  width: number
  height: number
  seed: number
  steps: number
  cfg: number
  sampler_name: string
  scheduler: string
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

export const genImageAPI = async (request?: GenImageRequest) => {
  return await http<GenImageResponse>({ url: '/api/image/create', method: 'post', data: request })
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

// import { http } from '@/utils/http'

export type LoginResult = {
  code: number
  msg?: string
  data: {
    /** 用户名 */
    username: string
    /** 当前登陆用户的角色 */
    roles: Array<string>
    /** `token` */
    accessToken: string
    /** 用于调用刷新`accessToken`的接口时所需的`token` */
    refreshToken: string
    /** `accessToken`的过期时间（时间戳） */
    expires: number
  }
}

export type RefreshTokenResult = {
  code: number
  msg?: string
  data: {
    /** `token` */
    accessToken: string
    /** 用于调用刷新`accessToken`的接口时所需的`token` */
    refreshToken: string
    /** `accessToken`的过期时间（时间戳） */
    expires: number
  }
}

/** 登录 */
export const loginAPI = (data?: object) => {
  // return http.request<LoginResult>("post", "/login", { data });
  console.log('loginAPI', data)
  return new Promise((resolve) => {
    resolve({
      code: 0,
      data: {
        username: 'admin',
        // 一个用户可能有多个角色
        roles: ['admin'],
        accessToken: 'eyJhbGciOiJIUzUxMiJ9.admin',
        refreshToken: 'eyJhbGciOiJIUzUxMiJ9.adminRefresh',
        expires: '2024/10/30 00:00:00'
      }
    })
  })
}

/** 刷新token */
export const refreshTokenAPI = (data?: object) => {
  // return http.request<RefreshTokenResult>("post", "/refreshToken", { data });
  console.log('refreshTokenAPI', data)
  return new Promise((resolve) => {
    resolve({
      code: 0,
      data: {
        accessToken: 'eyJhbGciOiJIUzUxMiJ9.newAdmin',
        refreshToken: 'eyJhbGciOiJIUzUxMiJ9.newAdminRefresh',
        // `expires`选择这种日期格式是为了方便调试，后端直接设置时间戳或许更方便（每次都应该递增）。如果后端返回的是时间戳格式，前端开发请来到这个目录`src/utils/auth.ts`，把第`38`行的代码换成expires = data.expires即可。
        expires: '2024/10/30 23:59:59'
      }
    })
  })
}

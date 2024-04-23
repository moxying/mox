<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'

const userStore = useUserStore()
const router = useRouter()

defineOptions({
  name: 'Login'
})

const login = () => {
  userStore.userInfo.login = true
  router.push({ name: 'Home' })
}
</script>

<template>
  <div class="login-wrap h-full flex flex-col justify-center">
    <div class="login-bg" />
    <div class="login-content flex flex-row h-full p-8">
      <div class="image-container flex-grow" />
      <div class="form-container flex flex-col text-white px-14 pt-5 pb-2">
        <div class="flex flex-col items-center mb-6">
          <!-- <img
            src="@/assets/logo.931a2409.png"
            alt="Colorful abstract logo"
            class="mb-3 w-20 h-20 rounded-2xl"
          /> -->
          <h2 class="font-semibold mb-1">登入</h2>
        </div>
        <div>
          <button
            class="button-field w-full flex items-center justify-start mb-3 p-2 ps-10 rounded-md"
            @click="login"
          >
            <img src="@/assets/logos--wechat-icon.svg" class="mr-1 w-5 h-6" /> 微信
          </button>
          <button
            class="button-field w-full flex items-center justify-start p-2 ps-10 rounded-md"
            @click="login"
          >
            <img src="@/assets/logos--google-icon.svg" class="mr-2" /> 谷歌
          </button>
          <div class="login-divider mb-3 mt-10">
            <hr class="login-hr" />
            <div class="login-text-wrap">
              <div class="login-text text-center my-4">或</div>
            </div>
          </div>
        </div>

        <div class="my-2">邮箱</div>
        <input type="email" placeholder="name@host.com" class="input-field w-full p-2 rounded-md" />
        <div class="my-2">密码</div>
        <input type="password" placeholder="密码" class="input-field w-full p-2 mb-4 rounded-md" />
        <a href="#" class="text-blue-500 hover:text-blue-700 text-xs">忘记密码？</a>
        <button class="login-button w-full mt-4" @click="login">登入</button>
        <div class="text-center mt-4 text-xs">
          <span>需要一个新账号？</span
          ><a href="#" class="text-blue-500 hover:text-blue-700 text-xs">注册</a>
        </div>

        <div class="bottom-info flex flex-row justify-evenly items-end">
          <a href="#">隐私政策</a>
          <a href="#">服务条款</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.login-wrap {
  .login-bg {
    position: absolute;
    z-index: -1;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-image: url('/src/assets/TreeMan.webp'),
      linear-gradient(rgb(0 0 0 / 60%), rgba(0, 0, 0, 0.7));
    background-blend-mode: overlay; /* 设置混合模式 */
    background-position: center center;
    background-size: cover;
    background-repeat: no-repeat;
  }
  .login-content {
    .image-container {
      background-image: url('/src/assets/TreeMan.webp');
      background-position: center center;
      background-size: cover;
      background-repeat: no-repeat;
      border-top-left-radius: 12px;
      border-bottom-left-radius: 12px;
    }
    .form-container {
      background: rgb(23, 23, 23); /* Dark background */
      border-top-right-radius: 12px;
      border-bottom-right-radius: 12px;
      min-width: 26rem;

      .login-divider {
        position: relative;

        .login-hr {
          opacity: 0.6;
          border-width: 0px 0px 1px;
          border-image: initial;
          border-style: solid;
          width: 100%;
          border-color: rgb(38, 39, 44);
        }

        .login-text-wrap {
          display: flex;
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: 2rem;
          height: 2rem;
          border-radius: 999rem;
          background-color: rgb(23, 23, 23);
          border: 1px solid rgb(38, 39, 44);
          -webkit-box-pack: center;
          justify-content: center;
          -webkit-box-align: center;
          align-items: center;
          z-index: 1;

          .login-text {
            font-size: 0.6rem;
            font-weight: 500;
            line-height: 1;
          }
        }
      }

      .bottom-info {
        font-size: 0.75rem;
        font-weight: 500;
        color: rgb(167, 178, 193);
        height: 100%;
      }
    }
  }
}

.button-field {
  background: rgb(38, 39, 44);
  border: none;
  color: white;
  transition-property: background-color, border-color, color, fill, stroke, opacity, box-shadow,
    transform;
  transition-duration: 200ms;
}

.button-field:hover {
  background-color: rgb(57, 61, 67);
}

.input-field {
  background: rgb(38, 39, 44);
  transition-property: background-color, border-color, color, fill, stroke, opacity, box-shadow,
    transform;
  transition-duration: 200ms;
}

.input-field:hover {
  background-color: rgb(57, 61, 67);
}

.input-field:focus {
  outline-color: rgb(114, 88, 242);
  outline-style: solid;
  box-shadow: 0 0 0 0.06rem rgb(114, 88, 242);
}
.login-button {
  @extend %app-gradient-button;
}
</style>

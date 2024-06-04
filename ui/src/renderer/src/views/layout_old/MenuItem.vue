<script setup lang="ts">
defineOptions({
  name: 'MenuItem'
})

const props = defineProps({
  routerInfo: {
    default: function () {
      return null
    },
    type: Object
  }
})
</script>

<template>
  <div class="menu-item-warp">
    <el-menu-item :index="props.routerInfo.name" :route="{ params: props.routerInfo.parameters }">
      <i :class="props.routerInfo.meta.icon" class="menu-icon"></i>
    </el-menu-item>
  </div>
</template>

<style lang="scss" scoped>
.menu-item-warp {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  margin-top: 0.3rem;
  margin-bottom: 0.3rem;

  .el-menu-item {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    flex-grow: 1;
    padding-left: 0 !important;
    padding-right: 0;
    height: 2.6rem;
    // border-radius: 10px;

    &:hover {
      // background-color: rgb(63, 71, 82);
      background-color: transparent;
      .menu-icon:before {
        @extend %app-gradient-bg-text;
      }
    }

    .menu-icon {
      // margin-left: 0.25rem;
      // margin-right: 0.25rem;
      margin-top: 0rem;
    }
    .menu-name {
      pointer-events: none;
    }

    .iconfont {
      font-size: 1.6rem;
      color: $app-font-second-color;
    }

    border-left: 3px solid;
    border-image: none;
    border-color: transparent;
    &.is-active {
      @extend %app-gradient-border-image;
      .menu-icon:before {
        @extend %app-gradient-bg-text;
      }
    }
  }
}
</style>

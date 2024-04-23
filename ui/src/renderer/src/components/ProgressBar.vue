<script setup lang="ts">
import { computed, StyleValue } from 'vue'

const props = defineProps({
  bgColor: String,
  containerBgColor: String,
  completed: Number
})

const fillerStyles = computed(() => {
  return {
    height: '100%',
    width: `${props.completed}%`,
    transition: 'width 100ms ease-in-out',
    borderRadius: 'inherit',
    textAlign: 'right'
  } as StyleValue
})
</script>

<template>
  <div class="container" :style="{ backgroundColor: `${props.containerBgColor}` }">
    <div class="bar" :style="fillerStyles">
      <span v-if="props.completed && props.completed > 1" class="label">{{
        `${props.completed}%`
      }}</span>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.container {
  height: 15px;
  border-radius: 40px;
}

.bar {
  background: linear-gradient(
      81.02deg,
      rgb(250, 85, 96) -23.47%,
      rgb(177, 75, 244) 45.52%,
      rgb(77, 145, 255) 114.8%
    )
    border-box border-box;
}

.label {
  display: flex;
  flex-direction: row-reverse;
  align-items: center;
  height: 15px;
  padding: 5px;
  color: white;
  font-weight: bold;
}
</style>

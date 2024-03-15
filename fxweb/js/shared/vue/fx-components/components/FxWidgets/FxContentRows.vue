<style>
</style>
<template>
  <div class ="list-content-rows">
    <div class="list-content-row" v-for="(value, name) in content" :key="value">
      <div class="list-content-name">{{ name }}</div>
      <div class="list-content-value">{{ value }}</div>
    </div>
  </div>
</template>
<script>
export default {
  props: [
    'content'
  ]
};
</script>

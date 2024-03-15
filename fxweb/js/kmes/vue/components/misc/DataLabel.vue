<style scoped>
.breakable {
  word-break: break-all;
  word-wrap: break-word;
}
</style>
<template>
  <div class="breakable">
    <slot></slot>
  </div>
</template>
<script>
export default {
};
</script>

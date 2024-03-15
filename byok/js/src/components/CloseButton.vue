<template>
  <div id="close" @click.prevent="$emit('click', $event)">
    <i class="fa fa-times"></i>
  </div>
</template>

<script>
export default {
  name: "CloseButton",
};
</script>

<style scoped>
#close {
  float: right;
  vertical-align: middle;
  text-align: center;
  font-size: 13px;
  width: 40px;
  height: 40px;
  padding: 12px 0px 0px 0px;
  border-left: 1px solid var(--border-color);
  margin: 0px;
  cursor: pointer;
}

#close:hover {
  background-color: #e6e6e6;
}

#close:active {
  background: #d4d4d4;
  box-shadow: inset 0 3px 5px rgba(0, 0, 0, 0.125);
}
</style>

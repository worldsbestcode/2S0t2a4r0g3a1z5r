<style scoped>
.panel-heading {
  border-radius: inherit
};
.heading-bar-panel {
  border: 0px
};
</style>
<template>
<div class="panel heading-bar-panel">
  <div class="panel-heading list-view-group list-view-header-group">
    <component
      :is="headingBar"
      v-bind="headingBarData"
      class="panel-title">
    </component>
  </div>
 </div>
</template>

<script>
export default {
  name: 'fx-treeview-heading-bar',
  props: [
    'headingBar',
    'headingBarData'
  ]
};
</script>

<style lang="scss" scoped>
span {
  display: block;
}

#main-canvas {
  height: 100%;
  position: absolute;
}

.sidebar-option {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow-y: auto;
  overflow-y: overlay;
  background-color: whitesmoke;
}
</style>
<template>
  <div>
    <transition name="fade">
      <keep-alive>
        <component :is="selectedView" :classPerms="classPerms">
        </component>
      </keep-alive>
    </transition>
  </div>
</template>
<script>
import ViewUtils from '../views/ViewUtils';

export default {
  props: {
    selectedView: {
      type: String,
      required: true,
      default: 'token'
    },
    classPerms: {
      type: Object,
      required: true,
    },
  },
  components: ViewUtils.getViewComponents(),
  data () {
    return {};
  },
};
</script>

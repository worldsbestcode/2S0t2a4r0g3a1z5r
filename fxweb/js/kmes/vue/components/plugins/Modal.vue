<style lang="scss" scoped>
@import '~src/css/variables.scss';

.base-modal {
  white-space: nowrap;
  height: 100%;
  right: 0;
  left: auto;
  -webkit-box-shadow: -2px 0px 5px 0px rgba(0,0,0,0.4);
  -moz-box-shadow: -2px 0px 5px 0px rgba(0,0,0,0.4);
  box-shadow: -2px 0px 5px 0px rgba(0,0,0,0.4);
  position: fixed;
  top: 0;
  bottom: 0;
  z-index: 5002;
  overflow: overlay;
  background: $base;
}

hr {
  border-top: 1px solid #d2d2d2;
}

.footer a {
  float: right;
  margin: 5px;
}
.service-heading {
  color: $secondary;
}
h1 {
  text-align: center;
}
.title {
  margin-bottom: 10px;
}

.backdrop {
  position: fixed;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  background: #000;
  z-index: 5001;
  opacity: .5;
}
.visible {
  transition: all .3s;
}

.invisible {
  width: 0px !important;
  transition: all .3s;
}

.base-modal {
  min-width: inherit;
}

</style>
<template>
  <div>
    <transition name="slide-right">
      <div class="base-modal" :class="{'visible': show, 'invisible': !show}" :style="{'width':width + '%'}" @keyup.enter="callback" @keyup.esc="close" v-if="show">
        <slot>
        </slot>
      </div>
    </transition>

    <div v-show="show" class="backdrop" @click="closeBackdrop"></div>
  </div>
</template>
<script>
export default {
  props: {
    closeBackdrop: {
      type: Function,
      default: function () {
        this.close();
      }
    },
    okText: {
      type: String,
      default: 'OK'
    },
    cancelText: {
      type: String,
      default: 'Cancel'
    },
    show: {
      required: true,
      type: Boolean
    },
    width: {
      default: 50,
      type: Number
    },
    title: {
      type: String
    },
    callback: {
      type: Function,
      default: function () {}
    },
    cancelCallback: {
      type: Function,
      required: false
    }
  },
  data () {
    return {
    };
  },
  methods: {
    close: function () {
      var self = this;
      if (self.cancelCallback) {
        self.cancelCallback();
      }
      self.$emit('on-close');
    }
  }
};
</script>

<style lang="scss" scoped>
@import '~src/css/variables.scss';

hr {
  border-top: 1px solid #d2d2d2;
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

.clickable {
  &:hover {
    color: black;
    text-decoration: none;
  }
}

</style>
<template>
  <div>
    <modal :show="show" @on-close="$emit('on-close')" :class="{'visible': show, 'invisible': !show}" :style="{'width':width + '%'}" @keyup.enter="callback" @keyup.esc="close">
      <div class="column is-12">
        <span v-if="serviceName != null">
          <h1 class="title is-2">{{ serviceName }}</h1>
        </span>

        <h4 class="subtitle is-3">{{ title }}</h4>
        <hr>

        <div class="column is-12">
          <slot name="modal-body"></slot>
        </div>

        <hr>

        <div class="column is-12">
          <div class="field is-grouped is-pulled-right">
            <a class="click clickable control" @click="close">{{ cancelText }}</a>
            <a class="click clickable control" @click="callback">{{ okText }}</a>
          </div>
        </div>

      </div>
    </modal>

    <div v-show="show" class="backdrop" @click="close"></div>
  </div>
</template>
<script>
import Modal from './Modal';

export default {
  components: {
    'modal': Modal
  },
  props: {
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
    },
    serviceName: {
      type: String,
      default: null,
    }
  },
  data () {
    return {};
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

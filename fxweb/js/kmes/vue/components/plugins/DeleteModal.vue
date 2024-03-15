<template>
  <modal :title="title" :callback="deleteCallback" :show="show" @on-close="$emit('on-close')">
    <div slot="modal-body">
      <delete-objects :data="data">
      </delete-objects>
    </div>
  </modal>
</template>
<script>
import DeleteComponent from './DeleteComponent';
import VIPModal from './VIPModal';

export default {
  components: {
    'delete-objects': DeleteComponent,
    'modal': VIPModal,
  },
  props: {
    data: {
      required: true
    },
    title: {
      required: true
    },
    show: {
      required: true
    },
    callback: {
      required: true
    }
  },
  data () {
    return {
      deleteModal: false
    };
  },
  methods: {
    deleteCallback: function () {
      this.callback();
      this.$emit('on-close');
    }
  }
};
</script>

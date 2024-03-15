<template>
  <fx-modal
    v-if="action"
    :title="action.title"
    :callback="action.callback"
    :show="show"
    @on-close="closeModal"
  >
    <div slot="modal-body">
      <component
        v-if="action.component"
        :is="action.component"
        v-bind.sync="action.props"
      >
      </component>
    </div>
  </fx-modal>
</template>
<script>
import ViewAction from 'kmes/components/views/actions/ViewAction';
import VIPModal from 'kmes/components/plugins/VIPModal';

export default {
  components: {
    'fx-modal': VIPModal,
  },
  props: {
    action: {
      type: ViewAction,
      default: null,
    },
    show: {
      type: Boolean,
      required: true,
    },
  },
  methods: {
    closeModal () {
      this.$emit('update:show', false);
    }
  }
};

</script>

<template>
  <btn-group v-if="this.actions.length > 0">
    <btn
      v-for="action in actions"
      :key="action"
      @click="actionClicked(action)"
    >
      {{ action }}
    </btn>
  </btn-group>
</template>
<script>
export default {
  props: {
    // data passed to callback. can be anything (e.g. a certificate or CA)
    data: {
      required: true,
    },
    // action names (that we just throw on buttons)
    actions: {
      type: Array,
      required: true,
    },
    // Callback for when an action was activated
    performAction: {
      type: Function,
      required: true,
    },
  },
  methods: {
    actionClicked: function (action) {
      this.performAction(this.data, action);
    }
  }
};
</script>

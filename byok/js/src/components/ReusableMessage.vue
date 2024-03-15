<template>
  <div
    :id="$props.messageData.messageId"
    :class="$props.messageData.messageClass"
  >
    <i
      :id="$props.messageData.iconId"
      :class="$props.messageData.iconClass"
    ></i>
    <p :id="$props.messageData.textId">{{ $props.messageData.firstLine }}</p>
    <p v-if="$props.messageData.secondLine">
      {{ $props.messageData.secondLine }}
    </p>
  </div>
</template>

<script>
export default {
  name: "ReusableMessage",
  props: {
    messageData: Object,
  },
};
</script>

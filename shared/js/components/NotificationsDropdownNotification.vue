<template>
  <div>
    {{ props.notification.objInfo.name }}
  </div>
  <div class="notification__time">
    {{ toTimeAgo(props.notification.objInfo.creationDate) }}
  </div>

  <button
    class="notification__clear"
    @click.prevent.stop="
      store.dispatch(
        'notifications/deleteNotification',
        props.notification.objInfo.uuid
      )
    "
  >
    Clear
  </button>
</template>

<script setup>
import { defineProps } from "vue";
import { useStore } from "vuex";

import { toTimeAgo } from "$shared/utils/misc.js";

const store = useStore();

const props = defineProps({
  notification: {
    type: Object,
    required: true,
  },
});
</script>

<style scoped>
.notification__time {
  font-size: 12px;
  color: var(--muted-text-color);
}

.notification__clear {
  color: var(--secondary-text-color);
  position: absolute;
  right: 1.25rem;
  top: 0.75rem;
  padding: 0;
  border: 0;
  background: 0;
}
</style>

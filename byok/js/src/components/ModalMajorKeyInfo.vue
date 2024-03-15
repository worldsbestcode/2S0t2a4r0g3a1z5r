<template>
  <modal-base @esc="$emit('closeModal')">
    <template #header>
      <p>{{ majorKey.alias || majorKey.name }} - Information</p>
      <button @click="$emit('closeModal')">
        <i class="fa fa-times" />
      </button>
    </template>
    <template #main>
      <ul class="modal-list">
        <li v-for="(value, key) in majorKeyFiltered" :key="key">
          {{ apiToReadable[key] }}:
          <span :class="key === 'kcv' ? 'checksum' : 'value'"
            >{{ value }}
          </span>
        </li>
      </ul>
    </template>
    <template #footer>
      <button
        class="button blue-button icon-text-button"
        @click="$emit('closeModal')"
      >
        <i class="fa fa-times" />
        Close
      </button>
    </template>
  </modal-base>
</template>

<script>
import ModalBase from "@/components/ModalBase.vue";

let apiToReadable = {
  name: "Name",
  kcv: "Checksum",
  type: "Type",
};

export default {
  components: {
    "modal-base": ModalBase,
  },
  inject: ["getSessionId", "isGpMode"],
  props: {
    majorKey: {
      type: Object,
      required: true,
    },
  },
  data: function () {
    return {
      apiToReadable: apiToReadable,
    };
  },
  computed: {
    majorKeyFiltered: function () {
      let filtered = {};
      for (let key in this.majorKey) {
        if (apiToReadable[key]) {
          filtered[key] = this.majorKey[key];
        }
      }
      return filtered;
    },
  },
};
</script>

<style scoped>
.value {
  color: var(--text-color-blue-lighter);
}

.modal-list {
  margin-bottom: 0;
  padding-left: 1rem;
}
</style>

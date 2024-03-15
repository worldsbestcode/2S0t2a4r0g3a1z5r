<template>
  <v-card>
    <v-card-title class="fx-card-title">
      <fx-label text="Update Serial Number" color="var(--primary-color)" />
      <fx-button variant="plain" icon="mdi-close" @click="emit('abort')" />
    </v-card-title>
    <v-card-subtitle>
      <fx-label
        text="If you wish to override the injected serial number, update/enter the serial number displayed.
              Click INJECT to apply changes."
      />
    </v-card-subtitle>
    <fx-separator />
    <v-card-text class="d-flex justify-center">
      <fx-label
        v-if="props.serialNumberFailed"
        text="Failed to read serial number, injection will not continue"
        color="var(--primary-color)"
      />
      <fx-text-field
        v-else
        v-model:input="serialNumber"
        label="Enter Serial Number"
      />
    </v-card-text>
    <v-card-actions>
      <div class="fx-serial-button-container">
        <fx-button
          :text="props.serialNumberFailed ? 'CLOSE' : 'ABORT'"
          theme="primary"
          icon="mdi-close"
          @click="emit('abort')"
        />
        <fx-button
          v-if="!props.serialNumberFailed"
          text="INJECT"
          icon="mdi-check"
          variant="tonal"
          theme="primary"
          @click="emit('inject')"
        />
      </div>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { defineEmits, defineProps, computed } from "vue";

const emit = defineEmits(["update:serialNumber", "inject", "abort"]);
const props = defineProps({
  serialNumber: {
    type: String,
    requried: true,
  },
  serialNumberFailed: {
    type: Boolean,
    required: false,
    default: false,
  },
});

const serialNumber = computed({
  get() {
    return props.serialNumber;
  },

  set(value) {
    emit("update:serialNumber", value);
  },
});
</script>

<style scoped>
.fx-card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fx-serial-button-container {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2.5rem;
}
</style>

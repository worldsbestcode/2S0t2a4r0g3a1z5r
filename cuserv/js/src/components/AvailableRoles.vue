<template>
  <ChcLabel div label="Choose a role to reparent the associated objects to">
    <div class="radio-container radio-container--two-col">
      <ChcRadio
        v-for="role in controllableRoles"
        :key="role.uuid"
        v-model="selectedRole"
        type="radio"
        :value="role.uuid"
        :label="role.name"
      />
    </div>
  </ChcLabel>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";
import { useStore } from "vuex";

import ChcLabel from "$shared/components/ChcLabel.vue";
import ChcRadio from "$shared/components/ChcRadio.vue";

const store = useStore();

const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  modelValue: {
    type: String,
    required: true,
  },
});

const controllableRoles = computed(() =>
  store.state.auth.managed_roles.filter((x) => x.type === "Controllable"),
);

const selectedRole = computed({
  get() {
    return props.modelValue;
  },
  set(value) {
    emit("update:modelValue", value);
  },
});

if (!selectedRole.value) {
  selectedRole.value = controllableRoles.value[0].uuid;
}
</script>

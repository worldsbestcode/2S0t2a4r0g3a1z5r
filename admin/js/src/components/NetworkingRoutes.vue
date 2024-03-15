<template>
  <ChcLabel div label="Routes">
    <ChcLabel div class="modal-stuff-container">
      <ChcLabel
        v-for="route of routes"
        :key="route"
        div
        class="modal-stuff-container modal-stuff-container--white"
      >
        <ChcInput v-model="route.destination" label="Destination" />
        <ChcInput v-model="route.netmask" label="Netmask" />
        <ChcInput v-model="route.gateway" label="Gateway" />
        <ChcInput v-model="route.metric" label="Metric" />

        <ChcLabel div>
          <ChcButton secondary @click="deleteRoute(route)">
            Delete route
          </ChcButton>
        </ChcLabel>
      </ChcLabel>

      <ChcLabel div>
        <ChcButton secondary @click="createRoute">Add route</ChcButton>
      </ChcLabel>
    </ChcLabel>
  </ChcLabel>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import ChcButton from "$shared/components/ChcButton.vue";
import ChcInput from "$shared/components/ChcInput.vue";
import ChcLabel from "$shared/components/ChcLabel.vue";

const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  modelValue: {
    type: Array,
    required: true,
  },
});

const routes = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

function createRoute() {
  const newRoute = {
    destination: "",
    netmask: "",
    gateway: "",
    metric: 0,
  };

  routes.value.push(newRoute);
}

function deleteRoute(route) {
  const routeIndex = routes.value.indexOf(route);
  routes.value.splice(routeIndex, 1);
}
</script>

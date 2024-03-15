<template>
  <div class="fx-service-header-container">
    <div class="fx-service-header">
      <div class="fx-service-header__icon">
        <img :src="serviceIcon" />
      </div>
      <div class="fx-service-header__title">{{ serviceName }}</div>
    </div>
    <fx-separator />
    <div class="fx-service-header__info">
      <fx-label :text="description" />
    </div>
  </div>
</template>

<script setup>
import { defineProps, watchEffect, ref } from "vue";
import axios from "axios";

const props = defineProps({
  serviceId: {
    type: String,
    required: true,
  },
});
let serviceName = ref("");
let serviceIcon = ref(null);
let description = ref("");
const getTemplateData = (templateUuid) => {
  try {
    axios
      .get(`/cuserv/v1/templates/${templateUuid}`, {
        errorContext: "Failed to fetch service",
      })
      .then((response) => {
        description.value = response.data.params.details.description;
      });
  } catch (error) {
    console.error(error);
  }
};
watchEffect(() => {
  try {
    axios
      .get(`/cuserv/v1/services/${props.serviceId}`, {
        errorContext: "Failed to fetch service",
      })
      .then((response) => {
        serviceName.value = response.data.objInfo.name;
        serviceIcon.value = response.data.relatedInfo.templateIcon;
        getTemplateData(response.data.templateUuid);
      });
  } catch (error) {
    console.error(error);
  }
});
</script>
<style scoped>
.fx-service-header-container {
  width: 100%;
  background: var(--primary-background-color);
  border-bottom: 1px solid var(--border-color);
  padding: 1.2rem 16rem;
  display: block;
}
.fx-service-header {
  display: flex;
  align-items: center;
}

.fx-service-header__icon {
  margin-right: 1rem;
  width: 85px;
  height: 60px;
  padding: 0.6rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 15px;
  text-align: center;
}
.fx-service-header__icon img {
  width: 100%;
  height: 100%;
}

.fx-service-header__title {
  font-weight: 700;
  font-size: 28px;
}

.fx-service-header__info {
  display: block;
  min-height: 20px;
  padding: 0.2rem 1rem;
}
</style>

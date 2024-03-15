<template>
  <div class="available-services-bread__wrapper">
    <div class="available-services-bread">
      <a @click="headToManageServices"> Service Management</a>
      <div>/</div>
      <a @click="headToDeployedServices"> Deployed Services</a>
      <div>/</div>
      <a @click="headToService"> {{ serviceName }}</a>
    </div>
    <div class="available-services-bread mx-2">/</div>
    <div class="available-services-bread__current">
      <a> Payment Key Injection </a>
    </div>
  </div>
</template>

<script setup>
import { defineProps, ref, watchEffect } from "vue";
import axios from "axios";

let serviceName = ref("");
const props = defineProps({
  serviceUuid: {
    type: String,
    required: true,
  },
});

function headToService() {
  window.location.href = "/cuserv/#/deployed/" + props.serviceUuid;
}

function headToDeployedServices() {
  window.location.href = "/cuserv/#/deployed";
}

function headToManageServices() {
  window.location.href = "/cuserv/#/available/All";
}

watchEffect(() => {
  try {
    axios
      .get(`/cuserv/v1/services/${props.serviceUuid}`, {
        errorContext: "Failed to fetch service",
      })
      .then((response) => {
        serviceName.value = response.data.objInfo.name;
      });
  } catch (error) {
    console.error(error);
  }
});
</script>

<style scoped>
.available-services-bread__wrapper {
  margin: 2rem 0;
  padding: 0 2rem;
  display: flex;
  max-width: 80rem;
  padding: 0rem 16rem;
}

.available-services-bread {
  display: flex;
  gap: 0.5rem;
  color: var(--border-color);
  align-items: center;
  flex-wrap: wrap;
}

.available-services-bread a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  cursor: pointer;
  text-overflow: ellipsis;
}

.available-services-bread a:hover {
  text-decoration: underline;
  color: var(--primary-color);
}

a.available-services-bread__current {
  pointer-events: none;
  color: var(--secondary-text-color);
}

.available-services-seperator {
  min-height: 1px;
  background: var(--border-color);
}
</style>

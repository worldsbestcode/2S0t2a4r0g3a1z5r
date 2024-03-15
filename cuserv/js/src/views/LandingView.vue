<template>
  <main class="app-main chc-main-horizontal-padding">
    <h1 class="service-management-text" title="Service Management">
      Service Management
    </h1>

    <div class="service-management-actions-container">
      <div class="service-management-actions">
        <ChcMainRouterLink
          v-if="store.state.auth.mgmtPerms.services"
          :to="{ name: 'serviceTemplates' }"
        >
          Available Services
        </ChcMainRouterLink>
        <ChcMainRouterLink :to="{ name: 'deployedServices' }">
          Deployed Services
        </ChcMainRouterLink>
        <ChcMainRouterLink
          v-if="store.state.auth.mgmtPerms.legacy"
          :to="{ name: 'adminServices' }"
        >
          Administrative Services
        </ChcMainRouterLink>
        <DkiRouterLink />
      </div>

      <div class="service-management-actions">
        <ServiceTemplateImport />

        <ChcListStyle v-model="state.listStyle" />
      </div>
    </div>

    <ChcHorizontalSeperator />

    <RouterView :list-style="state.listStyle" />
  </main>
</template>

<script setup>
import { reactive, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useStore } from "vuex";

import ChcHorizontalSeperator from "$shared/components/ChcHorizontalSeperator.vue";
import ChcListStyle from "$shared/components/ChcListStyle.vue";
import ChcMainRouterLink from "$shared/components/ChcMainRouterLink.vue";

import DkiRouterLink from "@/components/DkiRouterLink.vue";
import ServiceTemplateImport from "@/components/service-template/ServiceTemplateImport.vue";

const store = useStore();
const route = useRoute();
const router = useRouter();

const state = reactive({
  listStyle: "tile",
});

watchEffect(() => {
  if (route.name === "landing") {
    if (store.state.auth.mgmtPerms.services) {
      router.replace({ name: "serviceTemplates" });
    } else {
      router.replace({ name: "deployedServices" });
    }
  }
});
</script>

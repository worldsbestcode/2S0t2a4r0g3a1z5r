<template>
  <main-sidebar />

  <router-view :key="$route.params.clusterId" />
</template>

<script>
import MainSidebar from "@/layouts/MainSidebar.vue";
export default {
  name: "MainLayout",
  components: {
    MainSidebar,
  },
};
</script>

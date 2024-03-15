<template>
  <v-card>
    <v-card-title class="fx-card-title">
      <fx-label
        variant="plain"
        text="Your session is about to expire!"
        color="var(--primary-color)"
      />
    </v-card-title>
    <fx-separator />
    <v-card-text class="d-flex justify-center">
      <fx-label :text="remainingTimeText" />
    </v-card-text>
    <v-card-actions>
      <div class="fx-serial-button-container">
        <fx-button
          theme="primary"
          text="END SESSION"
          icon="mdi-close"
          @click="goHome"
        />
        <fx-button
          text="CONTINUE"
          icon="mdi-arrow-right-drop-circle-outline"
          theme="primary"
          variant="tonal"
          @click="keepAlive"
        />
      </div>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { querySession } from "@/utils/common";
import store from "@/store";

let remainingTimeText = ref("Session will expire in 2:00 minutes");

const remainingTime = computed(
  () => store.getters["serviceInfo/getRemainingTime"],
);

const sessionUuid = computed(() => {
  return store.getters["pedinject/getSessionId"];
});

const keepAlive = () => {
  querySession(sessionUuid.value, true);
};

const goHome = () => {
  window.location = "/cuserv/";
};

watch(
  remainingTime,
  () => {
    let seconds = remainingTime.value % 60;
    let minutes = Math.floor(remainingTime.value / 60);
    remainingTimeText.value = `Session will expire in ${minutes}:${seconds
      .toString()
      .padStart(2, "0")} minutes`;
  },
  { eager: true },
);
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

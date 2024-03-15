<template>
  <v-col>
    <v-row>
      <div class="fx-header">Logs</div>
    </v-row>
    <v-row>
      <v-sheet
        elevation="0.5"
        :style="getSheetStyle"
        rounded
        min-height="500"
        max-height="500"
        min-width="500"
        max-width="700"
      >
        <div ref="scrollContainer" class="fx-scrollable-content">
          <div v-for="logMsg in logMsgs" :key="logMsg.oid">
            <span class="fx-timestamp">
              {{ "(" + logMsg.timeStamp + "): " }}</span
            >
            <span :style="getMessageStyle(logMsg.status)">
              {{ logMsg.msg }}
            </span>
          </div>
        </div>
      </v-sheet>
    </v-row>
    <v-row>
      <fx-button
        :disabled="logMsgs.length === 0"
        class="mt-3"
        text="EXPORT"
        @click="exportLog"
      />
    </v-row>
  </v-col>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import store from "@/store";
import useVuetify from "@/plugins/useVuetify";

const scrollContainer = ref(null);

const logMsgs = computed(() => {
  return store.getters["pedinject/getLogMessages"];
});
const vuetify = useVuetify();
const lightTheme = vuetify.theme.themes._rawValue.light.colors;
const getSheetStyle = computed(() => {
  return {
    background: lightTheme.background,
    "border-color": lightTheme.offwhiteDark,
    "border-width": "1px",
    "border-style": "solid",
  };
});

const scrollToBottom = () => {
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight;
  }
};

watch(logMsgs, scrollToBottom);
const getMessageStyle = (status) => {
  let messageColor = "darkgreen";

  if (status === "Warning") {
    messageColor = "darkorange";
  } else if (status === "Error") {
    messageColor = "darkred";
  }

  return {
    color: messageColor,
    "font-size": "12px",
    "margin-bottom": "1px",
  };
};

const generateLogData = () => {
  let logData = "";

  logMsgs.value.forEach((logMsg) => {
    logData += logMsg.timeStamp + " " + logMsg.msg + "\r\n";
  });

  return logData;
};

const download = (data, fileName) => {
  if (typeof data === "string") {
    data = data.split("");
  }

  let a = document.createElement("a");
  let blob = new Blob(data);
  let blobUrl = window.URL.createObjectURL(blob);
  a.href = blobUrl;
  a.download = fileName;
  a.click();
  window.URL.revokeObjectURL(blobUrl);
};

const exportLog = () => {
  let logData = generateLogData();

  let today = new Date();
  let date =
    today.getFullYear() + "-" + (today.getMonth() + 1) + "-" + today.getDate();
  let fileName = "key-injection-session-log-" + date;
  download(logData, fileName);
};
</script>

<style scoped>
.fx-header {
  font-size: 25px;
  font-weight: 500;
  color: #000000;
  margin-bottom: 3px;
}
.fx-scrollable-content {
  overflow-y: auto;
  max-height: 500px;
  padding-left: 10px;
  padding-top: 5px;
}
.fx-timestamp {
  font-size: 12px;
  margin-bottom: 1px;
}
</style>

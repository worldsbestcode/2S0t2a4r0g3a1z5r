<template>
  <TaskSkeleton
    title="Automatic Backups"
    :loading="loading"
    @finish="updateBackupConfiguration"
  >
    <ChcToggle v-model="state.enabled" label="Enable" />

    <ChcInput v-model="state.startDate" label="Start date" type="date" />

    <ChcInput
      v-model.number="state.weeksFrequency"
      label="Frequency"
      hint="every 1-52 weeks"
      type="number"
      min="1"
      max="52"
    />

    <!-- todo: Add support to v-model arrays and value for type=checkbox -->
    <ChcToggle
      v-for="weekDay in weekDays"
      :key="weekDay"
      v-model="state.weekDays[weekDay]"
      :label="weekDay"
      side="right"
      small
    />

    <ChcComboBox
      v-model="state.selectedMirrors"
      multiple
      hint=""
      label="Storage Mirrors"
      :values="state.remoteDriveValues"
    />
  </TaskSkeleton>
</template>

<script setup>
import axios from "axios";
import { reactive, ref } from "vue";

import ChcComboBox from "$shared/components/ChcComboBox.vue";
import ChcInput from "$shared/components/ChcInput.vue";
import ChcToggle from "$shared/components/ChcToggle.vue";

import TaskSkeleton from "@/components/tasks/TaskSkeleton.vue";
import { useTaskFinish } from "@/composables";

const weekDays = [
  "Sunday",
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
];

const taskFinish = useTaskFinish();

const loading = ref(false);

const state = reactive({
  enabled: false,
  weeksFrequency: 1,
  startDate: "",
  // Turns week day array into object with week days as key, false as value
  weekDays: Object.assign({}, ...weekDays.map((x) => ({ [x]: false }))),
  selectedMirrors: [],
  remoteDriveValues: [],
});

function getBackupConfiguration() {
  axios
    .get("/kmes/v7/system/autobackup", {
      loading,
      errorContext: "Failed to fetch automatic backup configuration",
    })
    .then((response) => {
      const data = response.data.response;
      state.enabled = data.enabled;
      state.weeksFrequency = data.frequency;
      if (state.weeksFrequency === 0) {
        state.weeksFrequency = 1;
      }
      state.startDate = data.lastBackupDate;
      state.selectedMirrors = data.storageMirrors;

      for (const weekDay of data.weekDays) {
        state.weekDays[weekDay] = true;
      }
    });
}

function updateBackupConfiguration() {
  let enabledWeekDays = [];

  for (const [weekDay, enabled] of Object.entries(state.weekDays)) {
    if (enabled) {
      enabledWeekDays.push(weekDay);
    }
  }

  axios
    .put(
      "/kmes/v7/system/autobackup",
      {
        enabled: state.enabled,
        beginDate: state.startDate || undefined,
        frequency: state.weeksFrequency,
        weekDays: enabledWeekDays,
        storageMirrors: state.selectedMirrors,
      },
      {
        loading,
        errorContext: "Failed to update automatic backup configuration",
      },
    )
    .then(() => {
      taskFinish("AutomaticBackups");
    });
}

function getRemoteDrives() {
  axios
    .get("/admin/v1/drives", {
      loading,
      errorContext: "Failed to fetch remote drives",
    })
    .then((response) => {
      const data = response.data;
      for (const drive of data.drives) {
        state.remoteDriveValues.push({
          value: drive.uuid,
          label: drive.name + " - " + drive.type,
        });
      }
    });
}

getBackupConfiguration();
getRemoteDrives();
</script>

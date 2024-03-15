<template>
  <TaskSkeleton title="Date & Time" :loading="loading" @finish="setTime">
    <ChcLabel div label="NTP Servers" class="modal-stuff-container">
      <div
        v-for="(_, index) of state.ntpServers"
        :key="index"
        class="dns-server-container"
      >
        <ChcInput v-model="state.ntpServers[index]" />

        <div class="dns-server-delete-container">
          <!-- todo: Use X icon image -->
          <button class="dns-server-delete" @click="deleteNtp(index)">X</button>
        </div>
      </div>

      <ChcButton
        secondary
        style="margin-top: 0.5rem; display: block"
        @click="createNtp"
      >
        Add NTP server
      </ChcButton>
    </ChcLabel>

    <ChcInput
      v-model="state.utcDateTime"
      label="UTC date time"
      hint="read only"
      readonly
      type="datetime-local"
    />

    <ChcSelect v-model="state.country" label="Country">
      <option :value="''">Select a country</option>
      <option v-for="country in countries" :key="country.id" :value="country">
        {{ country.name }}
      </option>
    </ChcSelect>

    <ChcSelect v-model="state.timezone" label="Timezone">
      <option :value="''">Select a timezone</option>
      <option
        v-for="timezone in zonesForCountry"
        :key="timezone"
        :value="timezone"
      >
        {{ timezone }}
      </option>
    </ChcSelect>

    <ChcInput
      v-model="state.localDateTime"
      label="Local date time"
      type="datetime-local"
    />
  </TaskSkeleton>
</template>

<script setup>
import axios from "axios";
import countriesAndTimezones from "countries-and-timezones";
import { computed, reactive, ref, watch } from "vue";

import ChcButton from "$shared/components/ChcButton.vue";
import ChcInput from "$shared/components/ChcInput.vue";
import ChcLabel from "$shared/components/ChcLabel.vue";
import ChcSelect from "$shared/components/ChcSelect.vue";

import TaskSkeleton from "@/components/tasks/TaskSkeleton.vue";
import { useTaskFinish } from "@/composables";

/*
  countriesAndTimezones.getAllCountries() returns
  {
    AD: {
      id: 'AD',
      ...
    },
  }

  Convert getAllCountries to an array so we can sort it by the country's name
  as that is what we display to the user.
*/
const countries = Object.entries(countriesAndTimezones.getAllCountries())
  .map(([, country]) => country)
  .sort((a, b) => a.name.localeCompare(b.name));

const taskFinish = useTaskFinish();

const loading = ref(false);

const state = reactive({
  ntpServers: [],
  utcDateTime: "",
  localDateTime: "",
  timezone: "",
  country: "",
});

const zonesForCountry = computed(() => state.country?.timezones);

function createNtp() {
  state.ntpServers.push("");
}

function deleteNtp(index) {
  state.ntpServers.splice(index, 1);
}

function getTime() {
  axios
    .get("/admin/v1/time", {
      loading,
      errorContext: "Failed to fetch date and time configuration",
    })
    .then((response) => {
      state.ntpServers = response.data.ntpServers ?? [];
      state.utcDateTime = response.data.utcDateTime.replace(" ", "T");
      state.localDateTime = response.data.localDateTime.replace(" ", "T");
      state.timezone = response.data.timezone ?? "";

      if (state.timezone) {
        state.country = countriesAndTimezones.getCountryForTimezone(
          state.timezone,
        );
      }
    });
}

function setTime() {
  const localDateTime = state.localDateTime.replace("T", " ");
  console.log(localDateTime);
  axios
    .post(
      "/admin/v1/time",
      {
        ntpServers: state.ntpServers,
        localDateTime,
        timezone: state.timezone,
      },
      {
        loading,
        errorContext: "Failed to update date and time configuration",
      },
    )
    .then(() => {
      taskFinish("DateTime");
    });
}

watch(
  () => state.country,
  (newVal, oldVal) => {
    if (oldVal) {
      state.timezone = "";
    }
  },
);

watch(
  () => state.timezone,
  (value) => {
    if (value) {
      const timezoneInformation = countriesAndTimezones.getTimezone(
        state.timezone,
      );
      console.log(timezoneInformation.utcOffsetStr);
      const newUtcDateTime = new Date(
        state.localDateTime + timezoneInformation.utcOffsetStr,
      )
        .toISOString()
        .replace("Z", "");
      state.utcDateTime = newUtcDateTime;
    }
  },
);

watch(
  () => state.localDateTime,
  (value) => {
    const timezoneInformation = countriesAndTimezones.getTimezone(
      state.timezone,
    );
    const utcOffset = timezoneInformation?.utcOffsetStr ?? "Z";
    const newUtcDateTime = new Date(value + utcOffset)
      .toISOString()
      .replace("Z", "");
    state.utcDateTime = newUtcDateTime;
  },
);

getTime();
</script>

<style scoped>
.dns-server-container {
  position: relative;
}

.dns-server-container + .dns-server-container {
  margin-top: 0.5rem;
}

.dns-server-delete-container {
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  width: 40px;

  display: flex;
  justify-content: center;
  align-items: center;
}

.dns-server-delete {
  background: none;
  border: 0;
  padding: 0;
  height: 30px;
  width: 30px;
}
</style>

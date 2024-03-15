<template>
  <TaskSkeleton
    title="Major Keys"
    :loading="getMajorKeyLoading"
    @finish="finish"
  >
    <div class="major-keys-container">
      <div
        v-for="majorKey in state.majorKeys"
        :key="majorKey.name"
        class="major-key"
      >
        <div class="major-key__top">
          <div class="major-key__name">
            {{ majorKey.name }}
          </div>

          <div v-if="majorKey.checksum" class="checksum major-key__checksum">
            {{ majorKey.checksum }}
          </div>
          <div v-else class="major-key__not-loaded">Not loaded</div>
        </div>

        <div class="major-key__bottom">
          <template v-if="isWeb">
            <ModalRandomizeMajorKey
              :major-key="majorKey.name"
              @new-checksum="replaceChecksum(majorKey.name, $event)"
            />
          </template>
          <template v-else-if="isLocal">
            <ModalRandomizeMajorKeySmartCardFragments
              :major-key="majorKey.name"
              @new-checksum="replaceChecksum(majorKey.name, $event)"
            />

            <ModalLoadMajorKeyComponents
              :major-key="majorKey.name"
              @new-checksum="replaceChecksum(majorKey.name, $event)"
            />

            <ModalLoadMajorKeySmartCardFragments
              :major-key="majorKey.name"
              @new-checksum="replaceChecksum(majorKey.name, $event)"
            />
          </template>
        </div>
      </div>
    </div>
  </TaskSkeleton>
</template>

<script setup>
import axios from "axios";
import { computed, reactive, ref } from "vue";

import ModalLoadMajorKeyComponents from "@/components/modals/ModalLoadMajorKeyComponents.vue";
import ModalLoadMajorKeySmartCardFragments from "@/components/modals/ModalLoadMajorKeySmartCardFragments.vue";
import ModalRandomizeMajorKey from "@/components/modals/ModalRandomizeMajorKey.vue";
import ModalRandomizeMajorKeySmartCardFragments from "@/components/modals/ModalRandomizeMajorKeySmartCardFragments.vue";
import TaskSkeleton from "@/components/tasks/TaskSkeleton.vue";
import { useTaskFinish } from "@/composables";

const taskFinish = useTaskFinish();

const getMajorKeyLoading = ref(false);

const state = reactive({
  majorKeys: [],
});

const isWeb = computed(() => window.location.hostname !== "localhost");
const isLocal = computed(() => window.location.hostname === "localhost");
// const isRemote = computed(() => window.isExcryptTouch);

function getMajorKeys() {
  axios
    .get("/admin/v1/majorkeys", {
      loading: getMajorKeyLoading,
      errorContext: "Failed to fetch major keys",
    })
    .then((response) => {
      const majorKeys = ["PMK", "BAK", "MFK", "SCEK"];
      const responseMajorKeys = response.data.majorKeys;

      state.majorKeys = majorKeys.map((majorKey) => {
        const ret = {
          name: majorKey,
          checksum: null,
        };

        if (responseMajorKeys) {
          const majorKeyInResponse = responseMajorKeys.find(
            (responseMajorKey) => responseMajorKey.name === majorKey,
          );
          if (majorKeyInResponse) {
            ret.checksum = majorKeyInResponse.checksum;
          }
        }

        return ret;
      });
    });
}

function replaceChecksum(majorKey, checksum) {
  state.majorKeys.find((x) => x.name === majorKey).checksum = checksum;
}

async function finish() {
  taskFinish("MajorKeys");
}

getMajorKeys();
</script>

<style>
.major-keys-container {
  max-width: 1200px;
  display: grid;
  grid-template-columns: repeat(auto-fit, 500px);
  gap: 1rem;
}
.major-key {
  border: 1px solid var(--border-color);
  border-radius: 15px;
}

.major-key__top {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.major-key__bottom {
  display: grid;
  gap: 0.5rem;
  padding: 1rem;
}

.major-key__name {
  font-size: 28px;
  font-weight: 500;
}

.major-key__not-loaded {
  color: var(--muted-text-color);
  font-size: 12px;
}
</style>

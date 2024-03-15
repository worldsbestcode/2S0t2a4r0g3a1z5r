<template>
  <TaskSkeleton title="Join Clusters" :loading="loading" @finish="updatePeers">
    <template v-if="state.peers.length > 0">
      <ChcLabel
        v-for="(peer, index) in state.peers"
        :key="index"
        div
        class="modal-stuff-container"
      >
        <ChcInput v-model="peer.ip" label="IP/Hostname" />
        <ChcInput v-model.number="peer.port" label="Port" type="number" />
        <ChcLabel div>
          <ChcButton secondary @click="deletePeer(index)">Delete</ChcButton>
        </ChcLabel>
      </ChcLabel>
    </template>

    <ChcLabel div>
      <ChcButton secondary @click="createPeer">Add new peer</ChcButton>
    </ChcLabel>
  </TaskSkeleton>
</template>

<script setup>
import axios from "axios";
import { reactive, ref } from "vue";

import ChcButton from "$shared/components/ChcButton.vue";
import ChcInput from "$shared/components/ChcInput.vue";
import ChcLabel from "$shared/components/ChcLabel.vue";

import TaskSkeleton from "@/components/tasks/TaskSkeleton.vue";
import { useTaskFinish } from "@/composables";

const taskFinish = useTaskFinish();

const loading = ref(false);

const state = reactive({
  peers: [],
});

function createPeer() {
  state.peers.push({ ip: "", port: 7001 });
}

function deletePeer(index) {
  state.peers.splice(index, 1);
}

function getPeers() {
  axios
    .get("/admin/v1/peers", {
      loading: loading,
      errorContext: "Failed to fetch peers",
    })
    .then((response) => {
      state.peers = response.data.peers;
    });
}

function updatePeers() {
  axios
    .put(
      "/admin/v1/peers",
      {
        peers: state.peers,
      },
      {
        loading,
        errorContext: "Failed to update peers",
      },
    )
    .then(() => {
      taskFinish("JoinCluster");
    });
}

getPeers();
</script>

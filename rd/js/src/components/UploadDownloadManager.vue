<template>
  <input
    v-show="false"
    ref="fileInput"
    type="file"
    @change="handleFileSelected"
  />
  <Teleport to="body">
    <div class="upload-progress">
      <progress
        v-show="state.uploadProgress"
        :value="state.uploadProgress"
        max="100"
      />
      <div v-if="state.uploadWaitingForServer && state.uploadProgress === null">
        Upload finished, waiting for server to process file.
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, reactive } from "vue";
import axios from "axios";
import { useToast } from "vue-toastification";
import { download } from "@/utils.js";
import { unwrapErr } from "$shared/utils/web";

const toast = useToast();

const fileInput = ref(null);

const state = reactive({
  uploadProgress: null,
});

async function handleFileSelected(event) {
  const file = event.target.files[0];

  try {
    const uploadFormData = new FormData();
    uploadFormData.append("file", file);
    const uploadConfig = {
      onUploadProgress: function (progressEvent) {
        // https://gist.github.com/virolea/e1af9359fe071f24de3da3500ff0f429
        var percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total,
        );

        if (percentCompleted === 100) {
          state.uploadProgress = null;
        } else {
          state.uploadProgress = percentCompleted;
        }
      },
    };
    state.uploadWaitingForServer = true;
    await axios
      .post("/rd/v1/files/upload", uploadFormData, uploadConfig)
      .finally(() => {
        state.uploadWaitingForServer = false;
      });

    const eventBody = {
      event: "upload",
      file: file.name,
    };
    await axios.post("/rd/v1/files/event", eventBody);
  } catch (error) {
    toast.error(unwrapErr(error));
  }
}

let filesPollingInterval;
onMounted(() => {
  filesPollingInterval = setInterval(() => {
    axios
      .get("/rd/v1/files/event")
      .then((response) => {
        const event = response.data.event;
        if (event === "download") {
          const filename = response.data.file;
          download(filename);
        } else if (event === "upload") {
          fileInput.value.click();
        }
      })
      .catch((error) => {
        // Refresh on network error
        if (error.message == "Network Error" || error.response.status == 502) {
          location.reload();
        } else {
          toast.error(unwrapErr(error));
        }
      });
  }, 2000);
});
onBeforeUnmount(() => {
  clearInterval(filesPollingInterval);
});
</script>

<style scoped>
.upload-progress {
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  top: 2rem;
  width: 75%;
  padding: 0.5rem;
  text-align: center;
  z-index: 2;
}

.upload-progress progress {
  width: 100%;
  display: block;
}
</style>

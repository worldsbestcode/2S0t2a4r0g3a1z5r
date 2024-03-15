<template>
  <div class="remote-desktop">
    <UploadDownloadManager />

    <iframe
      ref="iframeRef"
      class="vnc-iframe"
      sandbox="allow-scripts allow-same-origin"
    />

    <div v-if="remotehost" class="remote-desktop-controls">
      <button class="icon-button" @click="setIframeSrc">
        <span class="material-symbols-outlined">refresh</span>
      </button>

      <button
        v-if="state.needsResize"
        class="icon-button"
        @click="synchronizeSize"
      >
        <span class="material-symbols-outlined"> fit_screen </span>
      </button>

      <div class="btn-group">
        <input
          id="low"
          v-model="state.resolution"
          value="low"
          type="radio"
          class="btn-check"
        />
        <label class="btn btn-outline-dark" for="low">Low</label>

        <input
          id="medium"
          v-model="state.resolution"
          value="medium"
          type="radio"
          class="btn-check"
        />
        <label class="btn btn-outline-dark" for="medium">Medium</label>

        <input
          id="high"
          v-model="state.resolution"
          value="high"
          type="radio"
          class="btn-check"
        />
        <label class="btn btn-outline-dark" for="high">High</label>

        <input
          id="highest"
          v-model="state.resolution"
          value="highest"
          type="radio"
          class="btn-check"
        />
        <label class="btn btn-outline-dark" for="highest">Highest</label>
      </div>

      <span class="text-danger"> {{ state.error }} </span>
    </div>
  </div>
  <FidoEvents />
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, watchEffect } from "vue";
import axios from "axios";
import { encodeUrlParams, unwrapErr } from "$shared/utils/web";
import UploadDownloadManager from "@/components/UploadDownloadManager.vue";
import FidoEvents from "@/components/FidoEvents.vue";

import { useRoute } from "vue-router";

// desktop.py
// DesktopConfig
const DESKTOP_MINIMUM_WIDTH = 100;
const DESKTOP_MAXIMUM_WIDTH = 7680;
const DESKTOP_MINIMUM_HEIGHT = 100;
const DESKTOP_MAXIMUM_HEIGHT = 4320;

const remotehost = window.location.hostname != "localhost";
const defaultQuality = remotehost ? "high" : "highest";
const iframeWPad = remotehost ? 0 : 2;

const route = useRoute();

const iframeRef = ref(null);

const state = reactive({
  port: null,
  session: null,
  resolution: null,
  compression: null,
  quality: null,
  width: null,
  height: null,

  needsResize: false,
  error: "",
});

async function setIframeSrc() {
  state.error = "";

  const hashParams = {
    width: state.width,
    height: state.height,
    compression: state.compression,
    quality: state.quality,
  };

  iframeRef.value.src = "";

  const config = {
    params: {
      width: hashParams.width,
      height: hashParams.height,
      view: route.params.view,
    },
  };
  axios
    .get("/rd/v1/desktop", config)
    .then(async (response) => {
      hashParams.vport = response.data.port;
      hashParams.sess = response.data.sess;

      iframeRef.value.src = "/remoteviewer/#" + encodeUrlParams(hashParams);
      iframeRef.value.contentWindow.focus();
    })
    .catch((error) => {
      state.error = unwrapErr(error);
    });
}

function setCompressionAndQuality() {
  switch (state.resolution) {
    case "low":
      state.compression = 9;
      state.quality = 0;
      break;
    case "medium":
      state.compression = 6;
      state.quality = 4;
      break;
    case "high":
      state.compression = 2;
      state.quality = 6;
      break;
    case "highest":
      state.compression = 0;
      state.quality = 9;
      break;
  }
  sessionStorage.setItem("desktopResolution", state.resolution);
}

function synchronizeSize() {
  // https://stackoverflow.com/a/11409978
  function clamp(number, min, max) {
    return Math.max(min, Math.min(number, max));
  }

  state.width = clamp(
    iframeRef.value.clientWidth - iframeWPad,
    DESKTOP_MINIMUM_WIDTH,
    DESKTOP_MAXIMUM_WIDTH,
  );
  state.height = clamp(
    iframeRef.value.clientHeight,
    DESKTOP_MINIMUM_HEIGHT,
    DESKTOP_MAXIMUM_HEIGHT,
  );
  state.needsResize = false;
}

function needsResizeObserver() {
  const width = state.width;
  const height = state.height;
  const iframeWidth = iframeRef.value.clientWidth - iframeWPad;
  const iframeHeight = iframeRef.value.clientHeight;

  if (width === iframeWidth && height === iframeHeight) {
    state.needsResize = false;
  } else {
    state.needsResize = true;
  }
}

const resizeObserver = new ResizeObserver(needsResizeObserver);
let stopIframeWatcher;
let stopResolutionWatcher;
onMounted(() => {
  state.resolution =
    sessionStorage.getItem("desktopResolution") ?? defaultQuality;
  resizeObserver.observe(iframeRef.value);
  synchronizeSize();
  stopResolutionWatcher = watchEffect(setCompressionAndQuality);
  stopIframeWatcher = watchEffect(setIframeSrc);
});
onBeforeUnmount(() => {
  resizeObserver.unobserve(iframeRef.value);
  stopResolutionWatcher();
  stopIframeWatcher();
});
</script>

<style scoped>
.remote-desktop {
  display: grid;
  gap: 0.5rem;
  padding: 0.5rem;
  grid-template-rows: 1fr max-content;

  /* Prevents the active quality from showing through the services selector dropdown 🤷 */
  z-index: 0;
}

.remote-desktop-controls {
  display: flex;
  align-items: center;
  justify-content: right;
  gap: 0.5rem;
  overflow: auto;
}

.remote-desktop-controls .btn {
  padding: calc(var(--bs-btn-padding-y) / 6) var(--bs-btn-padding-x);
  font-size: 10px;
}

.remote-desktop-controls .material-symbols-outlined {
  font-size: 20px;
}

.vnc-iframe {
  height: 100%;
  width: 100%;
  border: 0.5rem solid var(--bs-border-color-translucent);
}
</style>

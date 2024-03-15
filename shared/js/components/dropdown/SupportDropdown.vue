<template>
  <Dropdown right>
    <template #button="{ on }">
      <button class="icon-button" v-on="on">
        <img src="/shared/static/icons/help.svg" />
      </button>
    </template>

    <header>Support Information</header>
    <div class="support-information-container">
      <img
        class="support-information-container__img"
        src="/shared/static/crypto-hub-futurex-color.png"
      />
      <div class="support-information-container__text-and-link">
        <span>CryptoHub {{ state.version }}</span>
        <a class="chc-link" href="mailto:info@futurex.com">
          info@futurex.com
        </a>
      </div>
    </div>

    <header>Xceptional Support</header>
    <div class="exceptional-support-container">
      <div class="exceptional-support-container__key-value">
        <span class="exceptional-support-container__key">Available</span>
        <span>24/7/365</span>
      </div>
      <div class="exceptional-support-container__key-value">
        <span class="exceptional-support-container__key">Phone</span>
        <span>
          <a class="chc-link" href="tel:18309809782">(+1) 830-980-9782</a>
        </span>
      </div>
      <div class="exceptional-support-container__key-value">
        <span class="exceptional-support-container__key">E-mail</span>
        <span>
          <a class="chc-link" href="mailto:support@futurex.com">
            support@futurex.com
          </a>
        </span>
      </div>
      <div class="exceptional-support-container__key-value">
        <span class="exceptional-support-container__key">Toll-Free</span>
        <span>
          <a class="chc-link" href="tel:18002515112">1-800-251-5112</a>
        </span>
      </div>
    </div>

    <header>Engineering Campus</header>
    <span>864 Old Boerne Road Bulverde, Texas USA 78163</span>
  </Dropdown>
</template>

<script setup>
import { reactive } from "vue";

import axios from "$shared/axios.js";
import Dropdown from "$shared/components/Dropdown.vue";

const state = reactive({
  version: "",
});

axios.get("/home/v1/status").then((response) => {
  state.version = "v" + response.data.version;
});
</script>

<style scoped>
.support-information-container {
  display: flex;
  gap: 1rem;
}

.support-information-container__img {
  width: 300px;
}

.support-information-container__text-and-link {
  display: grid;
  justify-items: center;
  align-items: center;
}

.exceptional-support-container {
  display: grid;
  grid-template-columns: repeat(2, auto);
  column-gap: 1.5rem;
}

.exceptional-support-container__key {
  font-weight: 500;
}

.exceptional-support-container__key-value {
  display: flex;
  justify-content: space-between;
}
</style>

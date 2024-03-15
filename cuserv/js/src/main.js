import "bootstrap/dist/css/bootstrap.css";

import { createPinia } from "pinia";
import { createApp } from "vue";

import "$shared/style/shared.css";
import "$shared/style/wizard.css";

import { configureAxios } from "$shared/axios-setup.js";
import { toast, toastOptions } from "$shared/toast.js";

import "@/cuserv.css";

import App from "@/App.vue";
import router from "@/router.js";
import store from "@/store";

const pinia = createPinia();
const app = createApp(App);
app.use(pinia);
app.use(store);
app.use(router);
app.use(toast, toastOptions);
configureAxios();
app.mount("#app");

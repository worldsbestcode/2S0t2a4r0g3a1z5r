import "bootstrap/dist/css/bootstrap.css";

import { createApp } from "vue";

import "$shared/style/shared.css";

import { configureAxios } from "$shared/axios-setup.js";

import App from "@/App.vue";

import "@/iam.css";

import { toast, toastOptions } from "$shared/toast.js";

import router from "@/router.js";
import store from "@/store";

const app = createApp(App);
app.use(store);
app.use(router);
app.use(toast, toastOptions);
configureAxios();
app.mount("#app");

import "bootstrap/dist/css/bootstrap.css";

import { createApp } from "vue";

import "$shared/style/shared.css";
import "$shared/style/wizard.css";

import { configureAxios } from "$shared/axios-setup.js";
import { toast, toastOptions } from "$shared/toast.js";

import App from "@/App.vue";
import router from "@/router.js";
import store from "@/store";

const app = createApp(App);
app.use(store);
app.use(router);
app.use(toast, toastOptions);
configureAxios({ loading: false, auth: false, error: false });
app.mount("#app");

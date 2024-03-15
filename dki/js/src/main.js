// Global styling
import "bootstrap/dist/css/bootstrap.css";
//import "@/assets/dki.css";
import "$shared/style/shared.css";
import "@mdi/font/css/materialdesignicons.css";

// Setup the SPA
import { createApp } from "vue";
import App from "./App.vue";

import FxControls from "@/components/controls";

const app = createApp(App);

Object.entries(FxControls).forEach(([name, component]) => {
  app.component(name, component);
});

// Vuex
import store from "./store";
app.use(store);

// vuetify
import "vuetify/styles";
import vuetify from "./plugins/vuetify";
app.use(vuetify);
app.provide("vuetify", vuetify);

// Router
import router from "./router.js";
app.use(router);

// Toasts
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";
const toastOptions = {
  position: "top-center",
  timeout: 5000,
  closeOnClick: true,
  pauseOnFocusLoss: false,
  pauseOnHover: true,
  draggable: false,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: "button",
  icon: true,
  rtl: false,
  transition: "Vue-Toastification__fade",
  maxToasts: 20,
  newestOnTop: true,
};
app.use(Toast, toastOptions);

// Mount
app.mount("#app");

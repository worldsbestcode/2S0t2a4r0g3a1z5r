import { createApp } from "vue";
import { httpV2, bus } from "@/plugins";
import router from "@/router";
import store from "@/store";
import App from "@/App.vue";

import "@/assets/main.css";
import "@/assets/wizard-page.css";
import "$shared";

const app = createApp(App);

app.use(router);
app.use(store);

app.config.globalProperties.$bus = bus;
app.config.globalProperties.$httpV2 = httpV2;

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

app.mount("#app");

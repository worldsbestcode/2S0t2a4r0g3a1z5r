import { createApp } from "vue";
import App from "./App.vue";

import "./assets/main.css";

const app = createApp(App);

import store from "@/store";
import "$shared";
import "$shared/style/shared.css";
app.use(store);
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

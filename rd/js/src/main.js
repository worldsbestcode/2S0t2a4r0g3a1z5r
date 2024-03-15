// Global styling
import "bootstrap/dist/css/bootstrap.css";
import "@/assets/rd.css";
import "$shared/style/shared.css";

// Setup the SPA
import { createApp } from "vue";
import App from "./App.vue";
const app = createApp(App);

// Vuex
import store from "./store";
app.use(store);

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

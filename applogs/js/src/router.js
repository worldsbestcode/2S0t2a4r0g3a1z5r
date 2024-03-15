import { setupRouter } from "$shared/vue-router/setup.js";
import store from "@/store";

const routes = [
  {
    path: "/",
    name: "home",
    component: () => import("@/views/LogView.vue"),
    meta: {
      requiresAuth: true,
    },
  },
];

const router = setupRouter(routes, store);

export default router;

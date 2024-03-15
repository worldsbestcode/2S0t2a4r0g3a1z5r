import { setupRouter } from "$shared/vue-router/setup.js";

import store from "@/store";

const routes = [
  {
    path: "/",
    name: "login",
    component: () => import("@/views/LoginView.vue"),
    meta: {
      requiresAuth: false,
    },
  },
];

const router = setupRouter(routes, store);

export default router;

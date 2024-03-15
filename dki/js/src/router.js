import { setupRouter } from "$shared/vue-router/setup.js";
import store from "@/store";

const routes = [
  {
    path: "/pedinject/:service_id",
    name: "pedinject",
    component: () => import("@/views/InjectView.vue"),
    meta: {
      requiresAuth: true,
    },
  },
];

const router = setupRouter(routes, store, "/pedinject");

export default router;

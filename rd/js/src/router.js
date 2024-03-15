import { setupRouter } from "$shared/vue-router/setup.js";
import store from "@/store";

const routes = [
  {
    path: "/:view",
    name: "desktop",
    component: () => import("@/views/DesktopView.vue"),
    meta: {
      requiresAuth: true,
    },
  },
];

const router = setupRouter(routes, store);

export default router;

import { createRouter, createWebHashHistory } from "vue-router";

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "landing",
      component: () => import("@/views/LandingView.vue"),
    },
    {
      name: "session",
      path: "/:clusterId",
      component: () => import("@/layouts/MainCanvas.vue"),
      children: [
        {
          name: "login",
          path: "login",
          component: () => import("@/views/LoginView.vue"),
        },
        {
          name: "actions",
          path: "actions",
          component: () => import("@/views/ActionsView.vue"),
        },
        {
          name: "majorKeys",
          path: "major-keys",
          component: () => import("@/views/MajorKeysView.vue"),
        },
        {
          name: "workingKeys",
          path: "working-keys",
          component: () => import("@/views/WorkingKeysView.vue"),
        },
        {
          name: "userManagement",
          path: "user-management",
          component: () => import("@/views/Users/UserManagement.vue"),
        },
        {
          name: "smartCards",
          path: "smart-cards",
          component: () => import("@/views/SmartCard/SmartCardManagement.vue"),
        },
        {
          name: "certificatesAndRequests",
          path: "certificates-and-requests",
          component: () => import("@/views/CertificatesAndRequestsView.vue"),
        },
        {
          name: "generateComponents",
          path: "generate-components",
          component: () => import("@/views/GenerateComponentsView.vue"),
        },
      ],
    },
  ],
});

export default router;

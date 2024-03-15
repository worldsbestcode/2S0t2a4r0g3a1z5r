import { setupRouter } from "$shared/vue-router/setup.js";

import store from "@/store";

const routes = [
  {
    path: "/",
    name: "landing",
    meta: {
      requiresAuth: true,
      crumb: "Administration Tasks",
    },
    component: () => import("@/views/LandingView.vue"),
    children: [
      {
        path: "default",
        name: "default",
        component: () => import("@/components/tasks/TaskDefaultLogin.vue"),
      },

      {
        path: "setup",
        name: "setup",
        meta: {
          crumb: "Setup",
        },
        component: () => import("@/views/SetupWizardView.vue"),
      },

      {
        path: "pending/",
        name: "pending",
        meta: {
          crumb: "Pending",
        },
        component: () => import("@/views/SetupTasksListView.vue"),
        props: {
          tasksTypeText: "Pending",
          notificationsGetter: "notifications/setupPending",
        },
        children: [
          {
            path: ":setupPath",
            component: () => import("@/views/SetupView.vue"),
          },
        ],
      },

      {
        path: "completed/",
        name: "completed",
        meta: {
          crumb: "Completed",
        },
        component: () => import("@/views/SetupTasksListView.vue"),
        props: {
          tasksTypeText: "Completed",
          notificationsGetter: "notifications/setupCompleted",
        },
        children: [
          {
            path: ":setupPath",
            component: () => import("@/views/SetupView.vue"),
          },
        ],
      },

      {
        path: "settings",
        name: "settings",
        component: () => import("@/views/SettingsView.vue"),
      },
    ],
  },
];

const router = setupRouter(routes, store);

export default router;

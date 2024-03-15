// Pages
import LoginPage from "@/views/LoginPage.vue";
import GuardianDashboard from "@/views/GuardianDashboard.vue";

// Routes
const routes = [
  // Landing Page - Login
  {
    path: "/",
    name: "login",
    component: LoginPage,
    meta: {
      requiresAuth: false,
    },
  },

  // Dashboard
  {
    path: "/dashboard",
    name: "dashboard",
    component: GuardianDashboard,
    meta: {
      requiresAuth: true,
    },
  },
];

// Router
import { createRouter, createWebHashHistory } from "vue-router";
const router = createRouter({
  history: createWebHashHistory(),
  routes: routes,
});

// Enforce requiresAuth on route event
import store from "@/store";
router.beforeEach((to /*from*/) => {
  // Route requires auth and not logged in, redirect to login
  if (to.meta.requiresAuth && !store.state.auth.fully_logged_in) {
    return {
      path: "/",
    };
  }
  // Going to login and already logged in, redirect to dashboard
  else if (to.path == "/" && store.state.auth.fully_logged_in) {
    return {
      path: "/dashboard",
    };
  }
});

// Route on login state change
store.watch(
  (state) => state.auth.fully_logged_in,
  () => {
    // Redirect to dashboard on login
    if (store.state.auth.fully_logged_in) {
      router.push("/dashboard");
      // Redirect to / on loogut
    } else {
      router.push("/");
    }
  },
);

export default router;

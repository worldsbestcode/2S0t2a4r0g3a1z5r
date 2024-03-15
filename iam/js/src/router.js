import { bus } from "$shared/bus.js";
import { setupRouter } from "$shared/vue-router/setup.js";

import store from "@/store";

const routes = [
  {
    path: "/",
    name: "landing",
    component: () => import("@/views/LandingView.vue"),
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: "users",
        name: "users",
        component: () => import("@/users/UserManagementView.vue"),
        props: {
          type: "users",
        },
      },
      {
        path: "apps",
        name: "apps",
        component: () => import("@/users/UserManagementView.vue"),
        props: {
          type: "apps",
        },
      },
      {
        path: "userAdd",
        name: "userAdd",
        component: () => import("@/users/UserAddWizard.vue"),
        props: {
          type: "user",
        },
      },
      {
        path: "appAdd",
        name: "appAdd",
        component: () => import("@/users/UserAddWizard.vue"),
        props: {
          type: "app",
        },
      },
      {
        path: "roles",
        name: "roles",
        component: () => import("@/roles/RoleManagementView.vue"),
        props: {
          type: "users",
        },
      },
      {
        path: "partitions",
        name: "partitions",
        component: () => import("@/roles/RoleManagementView.vue"),
        props: {
          type: "apps",
        },
      },
      {
        path: "userRoleAdd",
        name: "userRoleAdd",
        component: () => import("@/roles/RoleAddWizard.vue"),
        props: {
          type: "user",
        },
      },
      {
        path: "appRoleAdd",
        name: "appRoleAdd",
        component: () => import("@/roles/RoleAddWizard.vue"),
        props: {
          type: "app",
        },
      },
      {
        path: "idp",
        name: "idp",
        component: () => import("@/idp/IdpManagementView.vue"),
      },
      {
        path: "/idpJwt/:uuid",
        name: "idpJwt",
        component: () => import("@/idp/jwt/JwtProviderWizard.vue"),
        props: true,
      },
      {
        path: "/idpLdap/:uuid",
        name: "idpLdap",
        component: () => import("@/idp/ldap/LdapProviderWizard.vue"),
        props: true,
      },
    ],
  },
];

const router = setupRouter(routes, store);

router.beforeEach(() => {
  bus.emit("routerBeforeEach");
});

router.afterEach(() => {
  bus.emit("routerAfterEach");
});

export default router;

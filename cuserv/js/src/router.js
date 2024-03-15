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
        path: "available",
        name: "serviceTemplates",
        component: () => import("@/views/ServiceTemplatesView.vue"),
        children: [
          {
            path: ":serviceTemplateCategory",
            name: "serviceTemplateCategory",
            children: [
              {
                path: ":serviceTemplateUuid",
                name: "serviceTemplate",
                component: () => import("@/views/ServiceTemplateView.vue"),
                props: true,
                children: [
                  {
                    path: "deploy",
                    name: "deploy",
                    component: () =>
                      import("@/views/ServiceTemplateDeployView.vue"),
                  },
                ],
              },
            ],
          },
        ],
      },

      {
        path: "deployed",
        name: "deployedServices",
        component: () => import("@/views/DeployedServicesView.vue"),
        children: [
          {
            path: ":serviceUuid",
            name: "deployedService",
            props: true,
            component: () => import("@/views/DeployedServiceView.vue"),
            children: [
              {
                path: "logs",
                name: "deployedServiceLogs",
                props: true,
                component: () => import("@/views/DeployedServiceLogsView.vue"),
              },
              {
                path: "instructions",
                name: "deployedServiceInstructions",
                component: () =>
                  import("@/views/DeployedServiceInstructionsView.vue"),
              },

              {
                path: "endpoints",
                name: "endpoints",
                props: true,
                component: () => import("@/views/ClientAppEndpointsView.vue"),
                children: [
                  {
                    path: ":endpointUuid",
                    name: "endpoint",
                    component: () =>
                      import("@/views/ClientAppEndpointView.vue"),
                    children: [
                      {
                        path: "credentials",
                        name: "endpointCredentials",
                        component: () =>
                          import(
                            "@/views/ClientAppEndpointCredentialsView.vue"
                          ),
                      },
                    ],
                  },
                ],
              },

              {
                path: "keys",
                name: "clientAppKeys",
                props: true,
                component: () => import("@/views/ClientAppKeysView.vue"),
              },

              {
                path: "service",
                name: "serviceAccounts",
                props: true,
                component: () =>
                  import("@/views/GoogleServiceAccountsView.vue"),
              },
              {
                path: "cryptospaces",
                name: "cryptospaces",
                props: true,
                component: () => import("@/views/GoogleCryptospacesView.vue"),
                children: [
                  {
                    path: ":cryptospaceUuid",
                    name: "cryptospace",
                    props: true,
                    component: () =>
                      import("@/views/GoogleCryptospaceView.vue"),
                    children: [
                      {
                        path: "logs",
                        name: "cryptospaceLogs",
                        props: true,
                        component: () =>
                          import("@/views/DeployedServiceLogsView.vue"),
                      },
                      {
                        path: "keys",
                        name: "cryptospaceKeys",
                        props: true,
                        component: () =>
                          import("@/views/GoogleCryptospaceKeysView.vue"),
                        children: [
                          {
                            path: ":keyUuid",
                            name: "cryptospaceKey",
                            props: true,
                            component: () =>
                              import("@/views/GoogleCryptospaceKeyView.vue"),
                            children: [
                              {
                                path: "logs",
                                name: "cryptospaceKeyLogs",
                                props: true,
                                component: () =>
                                  import("@/views/DeployedServiceLogsView.vue"),
                              },
                            ],
                          },
                        ],
                      },
                    ],
                  },
                ],
              },

              {
                path: "users",
                name: "googleUsers",
                props: true,
                component: () => import("@/views/GoogleUsersView.vue"),
                children: [
                  {
                    path: ":userUuid",
                    name: "googleUser",
                    props: true,
                    component: () => import("@/views/GoogleUserView.vue"),
                    children: [
                      {
                        path: "logs",
                        name: "userLogs",
                        props: true,
                        component: () =>
                          import("@/views/DeployedServiceLogsView.vue"),
                      },
                      {
                        path: "keys",
                        name: "personalKeys",
                        props: true,
                        component: () =>
                          import("@/views/GooglePersonalKeysView.vue"),
                        children: [
                          {
                            path: ":keyUuid",
                            name: "personalKey",
                            props: true,
                            component: () =>
                              import("@/views/GooglePersonalKeyView.vue"),
                          },
                        ],
                      },
                    ],
                  },
                ],
              },

              {
                path: "keyInjectionSessions",
                name: "keyInjectionSessions",
                props: true,
                component: () =>
                  import("@/components/dki/KeyInjectionSessions.vue"),
                children: [
                  {
                    path: ":sessionUuid",
                    name: "deviceLoadingEvents",
                    props: true,
                    component: () =>
                      import("@/components/dki/DeviceLoadingEvents.vue"),
                    children: [
                      {
                        path: "injectionLog/:logUuid",
                        name: "injectionLog",
                        props: true,
                        component: () =>
                          import("@/components/dki/InjectionLog.vue"),
                      },
                      {
                        path: "injectedKeys/:logUuid",
                        name: "injectedKeys",
                        props: true,
                        component: () =>
                          import("@/components/dki/InjectedKeysView.vue"),
                      },
                    ],
                  },
                ],
              },
              {
                path: "manageProtocolOptions",
                name: "manageProtocolOptions",
                props: true,
                component: () => import("@/views/ManageProtocolOptions.vue"),
              },
              {
                path: "selectOptionalKeys",
                name: "selectOptionalKeys",
                props: true,
                component: () =>
                  import("@/views/PedInjectionOptionalKeysView.vue"),
              },
              {
                path: "manageKeySlots",
                name: "manageKeySlots",
                props: true,
                component: () =>
                  import("@/components/dki/DKIKeySlotManagement.vue"),
              },
            ],
          },
        ],
      },

      {
        path: "admin",
        name: "adminServices",
        component: () => import("@/views/AdminServicesView.vue"),
        children: [
          {
            path: ":adminServiceCategory",
            name: "adminServiceCategory",
          },
        ],
      },
      {
        path: "pedinject",
        name: "pedinjectServices",
        component: () => import("@/components/dki/DKIServiceSelectWizard.vue"),
      },
    ],
  },
];

const router = setupRouter(routes, store);

export default router;

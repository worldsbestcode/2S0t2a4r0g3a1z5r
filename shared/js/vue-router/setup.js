import { createRouter, createWebHashHistory } from "vue-router";

import { initializeSharedStores, sendToLogin } from "$shared";
import { bus } from "$shared/bus.js";

export function setupRouter(routes, store, defaultAuthPath) {
  // Send to the first route in routes if the route does not exist
  routes.push({
    path: "/:pathMatch(.*)*",
    redirect: () => {
      return routes[0];
    },
  });

  const router = createRouter({
    history: createWebHashHistory(),
    routes: routes,
  });

  router.beforeEach(async (to) => {
    await initializeSharedStores(store);

    const loggedIn = store.state.auth.fully_logged_in;
    if (loggedIn) {
      // if you are at the SPA's index.html, to.path will be "/"
      if (defaultAuthPath && to.path === "/") {
        return {
          path: defaultAuthPath,
        };
      }
    } else {
      if (to.meta.requiresAuth) {
        sendToLogin({ shouldContinue: true });
      }
    }
  });

  router.beforeEach(() => {
    bus.emit("routerBeforeEach");
  });

  router.afterEach(() => {
    bus.emit("routerAfterEach");
  });

  return router;
}

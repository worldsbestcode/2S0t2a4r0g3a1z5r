import { computed } from "vue";
import { useRoute } from "vue-router";
import { useStore } from "vuex";

export function useLoggedIn() {
  const store = useStore();

  return computed(() => store.state.auth.fully_logged_in);
}

export function usePermissions() {
  const store = useStore();

  return computed(() => store.state.auth.perms);
}

export function useCrumbs() {
  const route = useRoute();

  return computed(() =>
    route.matched.map((x) => ({
      name: x.meta.crumb,
      to: { name: x.name },
    }))
  );
}

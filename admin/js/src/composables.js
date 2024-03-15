import { computed, inject } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useStore } from "vuex";

export function usePlaylist() {
  const route = useRoute();
  return computed(() => route.name === "setup");
}

export function useTaskFinish() {
  const store = useStore();
  const router = useRouter();
  const playlist = usePlaylist();

  const nextPage = inject("nextPage");

  return async (setupType) => {
    await store.dispatch("notifications/deleteSetupNotification", setupType);

    if (playlist.value) {
      nextPage();
    } else {
      router.replace("./");
    }
  };
}

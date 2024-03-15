import mitt from "mitt";
import { onBeforeMount, onBeforeUnmount } from "vue";

export const bus = mitt();

export function useBus(busEvent, busCallback) {
  onBeforeMount(() => {
    bus.on(busEvent, busCallback);
  });
  onBeforeUnmount(() => {
    bus.off(busEvent, busCallback);
  });
}

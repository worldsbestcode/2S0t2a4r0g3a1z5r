import { inject } from "vue";

export default function useVuetify() {
  const vuetify = inject("vuetify", null);

  if (!vuetify) {
    throw new Error("vuetify is not provided");
  }

  return vuetify;
}

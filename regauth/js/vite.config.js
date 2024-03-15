import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

import { generateAliases } from "../../shared/js/vite-config.js";

const fxwebShared = fileURLToPath(
  new URL("../../fxweb/js/shared/vue", import.meta.url),
);

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      ...generateAliases(import.meta.url),
      "fxweb-shared": fxwebShared,
    },
  },
  base: "/regauth",
  server: {
    fs: {
      allow: ["../.."],
    },
  },
});

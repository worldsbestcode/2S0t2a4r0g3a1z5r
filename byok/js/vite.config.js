import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

import { generateAliases } from "../../shared/js/vite-config.js";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: generateAliases(import.meta.url),
  },
  base: "/byok/",
  server: {
    fs: {
      allow: ["../.."],
    },
  },
});

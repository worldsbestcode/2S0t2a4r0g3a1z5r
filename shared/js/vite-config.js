import { fileURLToPath, URL } from "node:url";

const sharedDependencies = [
  "axios",
  "vue",
  "vue-toastification",
  "vuex",
  "vue-router",
];

function generateSharedDependencyAliases(nodeModulesPath) {
  const aliases = {};

  for (const sharedDependency of sharedDependencies) {
    aliases[sharedDependency] = nodeModulesPath + sharedDependency;
  }

  return aliases;
}

export function generateAliases(viteConfigFileUrl) {
  const rootPath = fileURLToPath(new URL("./src/", viteConfigFileUrl));
  const sharedPath = fileURLToPath(
    new URL("../../shared/js/", viteConfigFileUrl)
  );
  const sharedStaticPath = fileURLToPath(
    new URL("../../shared/static/", viteConfigFileUrl)
  );
  const nodeModulesPath = fileURLToPath(
    new URL("./node_modules/", viteConfigFileUrl)
  );

  const aliases = {
    "@": rootPath,
    $shared: sharedPath,
    "/shared/static": sharedStaticPath,
    ...generateSharedDependencyAliases(nodeModulesPath),
  };

  return aliases;
}

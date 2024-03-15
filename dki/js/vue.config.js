const path = require("path");
const { defineConfig } = require("@vue/cli-service");

const sharedPath = path.resolve(__dirname, "../../shared/js/");

module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {
    resolve: {
      alias: {
        $shared: sharedPath,
      },
    },
  },
  publicPath: "/dki/",
  devServer: {
    client: {
      webSocketURL: "wss://localhost/dki/ws",
    },
  },
});

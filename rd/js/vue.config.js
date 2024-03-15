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
  publicPath: "/rd/",
  devServer: {
    client: {
      webSocketURL: "auto://0.0.0.0:0/rd/ws",
    },
  },
});

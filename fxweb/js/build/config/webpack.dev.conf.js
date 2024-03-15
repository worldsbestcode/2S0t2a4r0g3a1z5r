var webpack = require('webpack');
var webpackMerge = require('webpack-merge');
var HtmlWebpackPlugin = require('html-webpack-plugin');
var FriendlyErrorsPlugin = require('friendly-errors-webpack-plugin');
var configUtils = require('../utils/config.js');

// Config data
var baseWebpackConfig = {};
var productConfig = {};

// Modify app context for development mode
function entryPointContextForDevMode() {
    // Add the client to each entry
    Object.keys(baseWebpackConfig.entry).forEach(function (name) {
        var clientEntry = ['./build/utils/client.js'];
        baseWebpackConfig.entry[name] = clientEntry.concat(baseWebpackConfig.entry[name]);
    });
}

// Webpack module rules
function makeModule() {
    // Add all the style loaders
    var styleLoaders = configUtils.styleLoaders({
        sourceMap: productConfig.prod.productionSourceMap
    });

    return configUtils.moduleWebpackConfig(styleLoaders);
}

// Source map generation
function makeDevtool() {
    // cheap-module-eval-source-map is faster than eval-source-map is faster for development
    return '#cheap-module-eval-source-map';
}

// Webpack plugin config
function makePlugins() {
    // Hot reload modules as needed
    // https://github.com/glenjamin/webpack-hot-middleware#installation--usage
    var hotModulePlugin = new webpack.HotModuleReplacementPlugin();

    // Do not update when the build fails
    var noEmitPlugin = new webpack.NoEmitOnErrorsPlugin();

    // Display webpack errors in a friendlier format
    var friendlyErrorsPlugin = new FriendlyErrorsPlugin();

    // Define a custom plugin to propagate the NODE_ENV variable everywhere
    // see http://vuejs.github.io/vue-loader/workflow/production.html
    var envPlugin = new webpack.DefinePlugin({
        'process.env': productConfig.dev.env
    });

    var WebPackPlugins = [
        envPlugin,
        hotModulePlugin,
        noEmitPlugin,
        friendlyErrorsPlugin
    ];

    // HtmlWebPackPlugin for each html landing page
    var webpackPages = productConfig.dev.HTMLWebpacks.map(function(info) {
        return new HtmlWebpackPlugin(info)
    });
    WebPackPlugins = WebPackPlugins.concat(webpackPages);

    return WebPackPlugins;
}

// Export the resulting webpack config
module.exports = function(config) {
    // Populate config data
    productConfig = config;
    baseWebpackConfig = require('./webpack.base.conf.js')(productConfig);

    // Use a client to listen for the hot reload
    entryPointContextForDevMode();

    // Build the webpack config
    return webpackMerge(baseWebpackConfig, {
        module: makeModule(),
        devtool: makeDevtool(),
        plugins: makePlugins()
    });
};

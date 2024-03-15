var path = require('path');
var webpack = require('webpack');
var webpackMerge = require('webpack-merge');
var HtmlWebpackPlugin = require('html-webpack-plugin');
var configUtils = require('../utils/config.js');
var VueLoaderPlugin = require('vue-loader/lib/plugin');

// Config data
var productConfig = {};
var projectRoot = '';

// Webpack module rules
function makeModule() {
    // Add all the style loaders
    var styleLoaders = configUtils.styleLoaders({
        sourceMap: productConfig.prod.productionSourceMap,
        extract: true
    });

    return configUtils.moduleWebpackConfig(styleLoaders);
}

// Source map generation
function makeDevtool() {
    return productConfig.prod.productionSourceMap ? '#source-map' : false;
}

// How to write file output
function makeOutput() {
    var path = productConfig.prod.assetsRoot;
    var jsSubdir = productConfig.common.subdirs.javascript;
    var filename = configUtils.assetsPath(jsSubdir + '/[name].[chunkhash].js', productConfig);
    var chunkFilename = configUtils.assetsPath(jsSubdir + '/[id].[chunkhash].js', productConfig);

    return configUtils.outputWebpackConfig(path, filename, null, chunkFilename);
}

// Webpack plugin config
function makePlugins() {
    // Define a custom plugin to propagate the NODE_ENV variable everywhere
    // see http://vuejs.github.io/vue-loader/workflow/production.html
    var envPlugin = new webpack.DefinePlugin({
        'process.env': {
            NODE_ENV: '"production"'
        }
    });

    // Pass options to loaders
    var loaderOptionsPlugin = new webpack.LoaderOptionsPlugin({
        minimize: true
    });

    var WebPackPlugins = [
        envPlugin,
        new VueLoaderPlugin(),
        loaderOptionsPlugin,
    ];

    // HtmlWebPackPlugin for each html landing page
    // var webpackPages = productConfig.prod.HTMLWebpacks.map(function(info) {
    //     return new HtmlWebpackPlugin(info)
    // });
    // WebPackPlugins = WebPackPlugins.concat(webpackPages);

    return WebPackPlugins;
}

// Check if extra plugins are needed
function checkConfig(webpackConfig, config) {
    if (productConfig.prod.productionGzip) {
        var CompressionWebpackPlugin = require('compression-webpack-plugin');

        webpackConfig.plugins.push(
            new CompressionWebpackPlugin({
                asset: '[path].gz[query]',
                algorithm: 'gzip',
                test: new RegExp(
                    '\\.(' +
                    productConfig.prod.productionGzipExtensions.join('|') +
                    ')$'
                ),
                threshold: 10240,
                minRatio: 0.8
            })
        );
    }

    if (productConfig.prod.bundleAnalyzerReport) {
        var BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
        webpackConfig.plugins.push(new BundleAnalyzerPlugin());
    }
}

// Export the resulting webpack config
module.exports = function(config) {
    // Populate config data
    productConfig = config;
    projectRoot = productConfig.common.projectRoot;
    baseConfig = require('./webpack.base.conf.js')(productConfig);

    // Create prod config on top of base config
    var webpackConfig = webpackMerge.merge(baseConfig, {
        module: makeModule(),
        devtool: makeDevtool(),
        output: makeOutput(),
        plugins: makePlugins()
    });

    // Add extra plugins as needed
    checkConfig(webpackConfig, productConfig);

    return webpackConfig;
};

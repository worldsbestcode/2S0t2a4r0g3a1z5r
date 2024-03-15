var path = require('path');
var configUtils = require('../utils/config.js');

// Config data
var productConfig = {};
var projectRoot = '';

// App entry-point
function makeEntry() {
    return configUtils.entryWebpackConfig(productConfig.common.entryPoint, ['babel-polyfill']);
}

// Where to write output
function makeOutput(product) {
    var prodPath = productConfig.prod.assetsPublicPath;
    var devPath = productConfig.dev.assetsPublicPath;
    var assetsPublicPath = process.env.NODE_ENV === 'production' ? prodPath : devPath;

    return configUtils.outputWebpackConfig(
        productConfig.prod.assetsRoot,
        product + '/app/[name].js',
        assetsPublicPath
    );
}

// Where to find source files
function makeResolve() {
    var vueProd = path.resolve(__dirname, projectRoot, 'node_modules/vue/dist/vue.esm.js');
    var vueDev = path.resolve(__dirname, projectRoot, 'node_modules/vue/dist/vue.js');
    var vuePath = process.env.NODE_ENV === 'production' ? vueProd : vueDev;

    var aliases = productConfig.common.aliases;
    aliases['vue$'] = vuePath;

    return configUtils.resolveWebpackConfig(
        [path.resolve(__dirname, projectRoot, 'node_modules')],
        ['.js', '.vue'],
        aliases,
        false
    )
}

// Where to find loaders
function makeResolveLoader() {
    var modulePaths = [
        path.resolve(__dirname, projectRoot, 'node_modules')
    ];

    return configUtils.resolveLoaderWebpackConfig(modulePaths);
}

// Webpack module rules
function makeModule() {
    // JSON Loader
    var jsonLoader = configUtils.moduleRuleWebpackConfig('json-loader', /\.json$/);

    // Vue HTML Loader
    var vueHTMLLoader = configUtils.moduleRuleWebpackConfig('vue-html-loader', /\.html$/);

    // ESLint Loader
    var eslintLoader = configUtils.moduleRuleWebpackConfig('eslint-loader', /\.(vue|js)$/, productConfig.common.eslint);

    // Vue Loader
    var vueLoader = configUtils.moduleRuleWebpackConfig('vue-loader', /\.vue$/, {
        options: {
            loaders: configUtils.cssLoaders({
                sourceMap: process.env.NODE_ENV === 'production' ? productConfig.prod.productionSourceMap : productConfig.dev.cssSourceMap,
                extract: process.env.NODE_ENV === 'production'
            })
        }
    });

    // Babel Loader
    var babelLoader = configUtils.moduleRuleWebpackConfig('babel-loader', /\.js$/, {
        include: projectRoot,
        exclude: /node_modules/
    });

    // Image Loader
    var imgLoader = configUtils.moduleRuleWebpackConfig('url-loader', /\.(png|jpe?g|gif|svg)(\?.*)?$/, {
        query: {
            limit: 10000,
            name: configUtils.assetsPath(productConfig.common.subdirs.images + '/[name].[hash:7].[ext]', productConfig)
        }
    });

    // Font Loader
    var fontLoader = configUtils.moduleRuleWebpackConfig('url-loader', /\.(woff2?|eot|ttf|otf)(\?.*)?$/, {
        query: {
            limit: 10000,
            name: configUtils.assetsPath(productConfig.common.subdirs.fonts + '/[name].[hash:7].[ext]', productConfig)
        }
    });

    return configUtils.moduleWebpackConfig([
        eslintLoader,
        vueLoader,
        babelLoader,
        jsonLoader,
        vueHTMLLoader,
        imgLoader,
        fontLoader
    ]);
}

// Export the resulting webpack config
module.exports = function(config) {
    // Populate config data
    productConfig = config;
    projectRoot = productConfig.common.projectRoot;

    // Build the webpack config
    return {
        entry: makeEntry(),
        output: makeOutput(config.product),
        resolve: makeResolve(),
        resolveLoader: makeResolveLoader(),
        module: makeModule(),
        bail: true
    };
};

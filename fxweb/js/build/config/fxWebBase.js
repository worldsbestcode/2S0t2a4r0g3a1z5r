var path = require('path');

// Root directory for the entire project
var projectRoot = path.resolve(__dirname, '../../');

function makeProductWebRoot(product) {
    return path.resolve(__dirname, projectRoot, product, 'vue');
}

function makeProdHtmlWebpack(product, buildDir, filePath, htmlFile) {
    return {
        filename: path.resolve(buildDir, htmlFile),
        template: path.resolve(__dirname, projectRoot, product, filePath + htmlFile),
        inject: 'head',
        minify: {
            removeComments: true,
            collapseWhitespace: true,
            removeAttributeQuotes: false,
            // more options:
            // https://github.com/kangax/html-minifier#options-quick-reference
        },
    };
}

// Production config
function makeProdConfig(product, buildDir) {
    var webpacks = [
        makeProdHtmlWebpack(product, buildDir, 'vue/', 'landing.html')
    ];

    if (product === 'regauth') {
        webpacks.push(makeProdHtmlWebpack(product, buildDir, 'protected_static/', 'download-landing.html'));
    }

    return {
        env: { NODE_ENV: '"production"' },
        HTMLWebpacks: webpacks,
        productionSourceMap: false,
        productionGzip: false,
        productionGzipExtensions: ['js', 'css'],

        assetsRoot: path.resolve(buildDir),
        assetsSubDirectory: '.',
        assetsPublicPath: '/' + product + '/static/',
    };
}

function makeDevHtmlWebpack(product, filePath, htmlFile) {
    return {
        filename: product + '/' + htmlFile,
        template: path.resolve(__dirname, projectRoot, product, filePath + htmlFile),
        inject: 'head'
    };
}

// Development config - currently not supported
// NOTE: will have to figure out how dev build will work deploying to multiple web servers?
function makeDevConfig(product) {
    var port = process.env.DEV_PORT || 8082;
    var host = process.env.DEV_HOST || 'localhost';
    var localproxy = "https://localhost:" + port;

    var webpacks = [
        makeDevHtmlWebpack(product, 'vue/', 'landing.html')
    ];

    if (product === 'regauth') {
        webpacks.push(makeDevHtmlWebpack(product, 'protected_static/', 'download-landing.html'));
    }

    return {
        env: { NODE_ENV: '"development"' },
        HTMLWebpacks: webpacks,
        port: port,
        proxyTable: {
            "!(/(app.js|landing.html)|/__webpack_hmr|/*.hot-update.json|/*.hot-update.js)": {
                target: "https://" + host + ":8443",
                changeOrigin: false,
                secure: false,
                hostRewrite: 'localhost:' + port,
            }
        },
        staticOptions: {
            extensions: ['html']
        },
        cssSourceMap: false,

        // Must be relative to production assets root?
        assetsSubDirectory: '.',
        assetsPublicPath: '/' + product + '/static/',
    };
}

// Test config
function makeTestConfig(product, buildDir) {
    return {
        env: { NODE_ENV: '"testing"' },

        htmlFilename: path.resolve(buildDir, product + '/landing.html'),
        htmlTemplate: path.resolve(__dirname, projectRoot, product, 'vue/landing.html'),
    };
}

// Options used regardless of how the build script is run
function makeCommonConfig(product, product_aliases) {
    var sharedBase = path.resolve(__dirname, projectRoot, 'shared/vue');
    var rkwebBase = path.resolve(__dirname, projectRoot, '../../shared/js');
    var shared_aliases = {
        'shared': sharedBase,
        'widgets': path.resolve(__dirname, sharedBase, 'widgets'),
        'rkweb': rkwebBase,
    };
    var all_aliases = {};
    Object.assign(all_aliases, shared_aliases);
    Object.assign(all_aliases, product_aliases);

    console.log(all_aliases);

    return {
        projectRoot: projectRoot,
        entryPoint: path.resolve(__dirname, projectRoot, product, 'vue/main.js'),
        aliases: all_aliases,
        subdirs: {
            images: 'images',
            fonts: 'fonts',
            javascript: 'js',
            css: 'css'
        },
        eslint: {
            enforce: 'pre',
            include: projectRoot,
            exclude: /node_modules/,
            plugins: [
              'vue'
            ],
        },
    };
}

// Web export build parameters
function webExport(product, aliases, buildDir) {
    return {
        product: product,
        prod: makeProdConfig(product, buildDir),
        dev: makeDevConfig(product),
        test: makeTestConfig(product, buildDir),
        common: makeCommonConfig(product, aliases),
    };
}

module.exports = {
    makeProductWebRoot, makeProductWebRoot,
    webExport: webExport,
};

var path = require('path');
var webpack = require('webpack');
var shell = require('./utils/shell.js');
var info = require('./utils/info.js');
var server = require('./utils/server.js');
var products = require('./products.json');

// Determine whether to run in prod or dev mode
shell.getArgs(process.argv, prodBuild, debugProdBuild, devBuild);

// Fetch the product-specific config file
function getProductConfig(productName, buildDir, callback) {
    // Validate that the product name exists
    if (Object.keys(products).indexOf(productName) !== -1) {
        // Pass the product config file to the build callback
        var buildFunc = require(products[productName])
        callback(buildFunc(buildDir));
    }
    // Failed to fetch the file, so display help
    else {
        shell.displayHelp('Cannot build "' + productName + '". No such entry in "products.json".');
        process.exit(1);
    }
}

function buildWebpackOutput(productConfig, webpackConfig, buildName) {
    // Print some random advice
    info.printRandomTip();

    // Display loading spinner
    var spinner = info.startSpinner('Building for ' + buildName + '...');

    // Ensure a clean output directory
    shell.makeAssetsDirectory(path.join(productConfig.prod.assetsRoot, productConfig.prod.assetsSubDirectory));

    // Build for production
    webpack(webpackConfig, function (err, stats) {
        info.stopSpinner(spinner);

        // Catch any errors that occur during the build process
        if (err) {
            console.log(err);
            process.exit(1);
        }

        // Print the build results
        else if (stats) {
            console.log(stats.toString({
                colors: true,
                modules: false,
                children: false,
                chunks: false,
                chunkModules: false
            }) + '\n');
            process.exit(0);
        }
        else {
            console.log('Webpack build finished, but no stats were returned!');
        }
    });
}

// Production build
function prodBuild(productName, buildDir) {
    process.env.NODE_ENV = 'production';
    getProductConfig(productName, buildDir, function(config) {
        var webpackProdConfig = require('./config/webpack.prod.conf.js')(config);
        webpackProdConfig.output.filename = `${productName}.js`;
        webpackProdConfig.mode = 'production';
        buildWebpackOutput(config, webpackProdConfig, 'Production');
    });
}

// Debug Production build
function debugProdBuild(productName, buildDir) {
    process.env.NODE_ENV = 'development';
    getProductConfig(productName, buildDir, function(config) {
        var webpackDevConfig = require('./config/webpack.dev.conf.js')(config);
        webpackDevConfig.mode = 'development';
        buildWebpackOutput(config, webpackDevConfig, 'Debug Production');
    });
}

// Development build
function devBuild(productName, buildDir) {
    process.env.NODE_ENV = 'development';
    getProductConfig(productName, buildDir, function(config) {
        // Start hot-reloading development server
        server.startServer(config);
    });
}

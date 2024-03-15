var path = require('path');
var express = require('express');
var webpack = require('webpack');
var historyAPI = require('connect-history-api-fallback');
var proxyMiddleware = require('http-proxy-middleware');
var devMiddleware = require('webpack-dev-middleware');
var hotMiddleware = require('webpack-hot-middleware');
var info = require('./info.js');
var https = require('https');
var fs = require('fs');
var morgan = require('morgan');

// Set up the Express instance
function setupServer(app, config) {
    // Config data
    var webpackDevConfig = require('../config/webpack.dev.conf.js')(config);

    // Print some random advice
    info.printRandomTip();

    // Display loading spinner
    var spinner = info.startSpinner('Building for Development...');
    console.log('\n');

    // Build for development
    var compiler = webpack(webpackDevConfig, function(err, stats) {
        info.stopSpinner(spinner);

        // Catch any errors that occur during the build process
        if (err) {
            throw err;
        }
    });

    // Static content routes
    var devRoutes = devMiddleware(compiler, {
        publicPath: webpackDevConfig.output.publicPath,
        stats: { colors: true, chunks: false }
    });

    // Routing for hot-reloading
    var hotReloadRoutes = hotMiddleware(compiler);

    // Force a page reload when html-webpack-plugin template changes
    compiler.plugin('compilation', function (compilation) {
        compilation.plugin('html-webpack-plugin-after-emit', function (data, callback) {
            hotReloadRoutes.publish({ action: 'reload' });
            callback();
        });
    });

    // Proxy API requests
    var proxyTable = config.dev.proxyTable;
    Object.keys(proxyTable).map(function(proxyRule) {
        var options = proxyTable[proxyRule]
        app.use(proxyMiddleware(proxyRule, options));
    });

    // Handle fallback for HTML5 history API
    app.use(historyAPI());

    // Serve webpack bundle output
    app.use(devRoutes);

    // Enable hot-reload and state-preserving compilation error display
    app.use(hotReloadRoutes);

    // Serve pure static assets
    var assetsPublicPath = config.dev.assetsPublicPath;
    var assetsSubDirectory = config.dev.assetsSubDirectory;
    var staticPath = path.posix.join(assetsPublicPath, assetsSubDirectory);

    app.use(staticPath, express.static(assetsSubDirectory));
}

// Create, set up, and start an Express middleware instance that acts as a
// hot-reloading server for developing static content
function startServer(config) {
    // Create a server instance
    var app = express();
    app.use(morgan('combined'));

    // Set up the server instance
    setupServer(app, config);

    // Get the listening port from the config
    var port = config.dev.port;

    // Listen scheme with port
    var hostPort = 'https://localhost: ' + port;

    // Start the server instance
    var httpsApp = https.createServer({
      key: fs.readFileSync('certs/dev-server.key'),
      cert: fs.readFileSync('certs/dev-server.pem'),
      ciphers: 'ALL',
      dhparam: '-----BEGIN DH PARAMETERS-----\nMIIBCAKCAQEA8RD1NibNrtv7NUSoGiN5oH2ZM7mBIF4XRIbR+ZsUIsnc2RscN1Mb\nV1gSBau2LBiF/AtvAAnDoYkahwZUHkwWQ7QxEWbwsHnDr711CJ8nPYsgg5PT1ROq\ny6eejfh2yrP16h7xK7K9zqXVRvApVo9K7O6kv8vhutXLjsMCmocpUKusmKLAZMmc\nbnJ9lqCRyNxzgHxR/kqXD8KC6FnQsBmJWNhAHLkpJ+PPSZejkaXMePvh8gHtxz1x\nfq/l2sT7u1JQq2OoxD+83LcOz3f5BqgT0PRc2+kpSswujUTunWxJrTG8fMcVFBtG\nTG8GtbNWpBNr3aTqT3DjII3haIWFkNoWqwIBAg==\n-----END DH PARAMETERS-----\n',
    }, app);
    return httpsApp.listen(port, function (err) {
        // Print any errors that occur
        if (err) {
            console.log(err);
            return;
        }

        // Print listening message
        console.log('Listening at ' + hostPort + '\n')
    });
}

module.exports = {
    startServer: startServer
};

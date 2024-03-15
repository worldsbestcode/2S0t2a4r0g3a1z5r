var path = require('path');
var fxWebBase = require('./fxWebBase.js');

var product = 'kmes';

var productWebRoot = fxWebBase.makeProductWebRoot(product);

var aliases = {
    'kmes': path.resolve(__dirname, productWebRoot),
    'src': path.resolve(__dirname, productWebRoot),
    'components': path.resolve(__dirname, productWebRoot, 'components'),
};

module.exports = function (buildDir) {
    return fxWebBase.webExport(product, aliases, buildDir);
};

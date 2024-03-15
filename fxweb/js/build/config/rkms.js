var path = require('path');
var fxWebBase = require('./fxWebBase.js');

var product = 'rkms';

var productWebRoot = fxWebBase.makeProductWebRoot(product);

var aliases = {
    'rkms': path.resolve(__dirname, productWebRoot),
    'components': path.resolve(__dirname, productWebRoot, 'components'),
};

module.exports = function (buildDir) {
    return fxWebBase.webExport(product, aliases, buildDir);
};

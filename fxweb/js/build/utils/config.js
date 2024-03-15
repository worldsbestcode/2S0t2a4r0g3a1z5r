var path = require('path');
//var ExtractTextPlugin = require('extract-text-webpack-plugin');

/**
 * Build the "entry" for webpack config JSON
 *
 * @param {string}  pathToMain  path to the js file that provides the app's entry point
 * @param {array}  moduleList  names of modules to be imported with the main js file
 * @return {object}  The value for the "entry" key in the JSON for the webpack config
 */
function entryWebpackConfig(pathToMain, moduleList) {
    var context = [];

    // Add the main js file as the entry point
    if (pathToMain) {
        context.push(pathToMain);
    }

    // Add the modules to the entry context
    if (moduleList) {
        context = context.concat(moduleList);
    }

    // Return the resulting portion of the config JSON
    return {
        app: context
    };
}

/**
 * Build the "output" for webpack config JSON
 *
 * @param {string}  path  directory to write the bundles to
 * @param {string}  filename  what to name each bundle
 * @param {string}  publicPath  base URI before the filename
 * @param {function}  chunkFilename  function that returns the name a given chunk
 * @return {object}  The value for the "output" key in the JSON for the webpack config
 */
function outputWebpackConfig(path, filename, publicPath, chunkFilename) {
    return {
        path: path,
        filename: filename,
        publicPath: publicPath ? publicPath : undefined,
        chunkFilename: chunkFilename ? chunkFilename : undefined
    };
}

/**
 * Build the "resolve" for webpack config JSON
 *
 * @param {array}  modules  directories to search when resolving module names
 * @param {array}  extensions  which extensions to resolve to when importing a file
 * @param {object}  alias  aliases for commonly used paths when calling "import"
 * @param {boolean}  enforceModuleExtension  whether to require a filename extension when calling "import"
 * @return {object}  The value for the "resolve" key in the JSON for the webpack config
 */
function resolveWebpackConfig(modules, extensions, alias, enforceModuleExtension) {
    return {
        modules: modules,
        extensions: extensions,
        alias: alias,
        enforceModuleExtension: enforceModuleExtension
    };
}

/**
 * Build the "resolveLoader" for webpack config JSON
 *
 * @param {array}  modules  directories to search when resolving module names for webpack loaders
 * @return {object}  The value for the "resolveLoader" key in the JSON for the webpack config
 */
function resolveLoaderWebpackConfig(modules) {
    return {
        modules: modules
    };
}

/**
 * Build the "module" for webpack config JSON
 *
 * @param {array}  rules  array of webpack loader config JSON (output of moduleRuleWebpackConfig)
 * @return {object}  The value for the "module" key in the JSON for the webpack config
 */
function moduleWebpackConfig(rules) {
    return {
        rules: rules
    };
}

/**
 * Build a rule for the "rules" under "module" in the webpack config JSON
 *
 * @param {string}  loader  name of the loader
 * @param {regex}  test  regex for the filename to determine whether to load it
 * @param {object}  options  additional options (if needed)
 * @return {object}  The config JSON for a single webpack loader
 */
function moduleRuleWebpackConfig(loader, test, options) {
    // Required keys
    var result = {
        loader: loader,                                                    // name of the loader
        test: test                                                         // input filename regex
    };

    // Additional options
    if (options) {
        result.query = options.query ? options.query : undefined;          // loader query
        result.enforce = options.enforce ? options.enforce : undefined;    // which phase should loader be called (pre, inline, normal, post)
        result.include = options.include ? options.include : undefined;    // files to include
        result.exclude = options.exclude ? options.exclude : undefined;    // files to exclude
        result.options = options.options ? options.options : undefined;    // extra options
    }

    return result;
}

/**
 * Determine the path to some assets based on whether building for development or production
 *
 * @param {string}  _path  subdirectory where the assets are located (images, fonts, etc.)
 * @param {object}  config  product config file
 * @return {string}  path to a type of asset (e.g. prodAssets/images/)
 */
function assetsPath(_path, config) {
    var prodAssetsSubdir = config.prod.assetsSubDirectory;
    var devAssetsSubdir = config.dev.assetsSubDirectory;
    var assetsSubDirectory = process.env.NODE_ENV === 'production' ? prodAssetsSubdir : devAssetsSubdir;

    return path.posix.join(assetsSubDirectory, _path);
}

/**
 * Generate the base webpack config for all the loaders of various stylesheet formats
 * This must be passed to the "vue-loader" options (for style in the .vue files)
 * and be presented as individual loaders to webpack (for loose stylesheet files)
 *
 * @param {object}  options  options for the loaders
 * @return {object}  The base config JSON for all the style loaders
 */
function cssLoaders(options) {
    options = options || {};

    var cssLoader = {
        loader: 'css-loader',
        options: {
            minimize: process.env.NODE_ENV === 'production',
            sourceMap: options.sourceMap
        }
    };

    // Generate the webpack config for the given loader name
    // Note: There is always at least a CSS loader included because all the
    //       stylesheet formats are supersets of CSS
    function generateLoaders (loader, loaderOptions) {
        var loaders = [cssLoader];
        if (loader) {
            loaders.push({
                loader: loader + '-loader',
                options: Object.assign({}, loaderOptions, {
                    sourceMap: options.sourceMap
                })
            });
        }

        return ['vue-style-loader'].concat(loaders);
    }

    return {
        css: generateLoaders(),
        postcss: generateLoaders(),
        less: generateLoaders('less'),
        sass: generateLoaders('sass', { indentedSyntax: true }),
        scss: generateLoaders('sass'),
        stylus: generateLoaders('stylus'),
        styl: generateLoaders('stylus')
    };
}

/**
 * Generate webpack config for the loaders that handle the loose stylesheet files
 *
 * @param {object}  options  options for the loaders
 * @return {array}  The config JSON for all the style loaders
 */
function styleLoaders(options) {
    var output = [];
    var loaders = cssLoaders(options);
    for (var extension in loaders) {
        var loader = loaders[extension];
        output.push({
            test: new RegExp('\\.' + extension + '$'),
            use: loader
        });
    }
    return output;
}

module.exports = {
    entryWebpackConfig: entryWebpackConfig,
    outputWebpackConfig: outputWebpackConfig,
    resolveWebpackConfig: resolveWebpackConfig,
    resolveLoaderWebpackConfig: resolveLoaderWebpackConfig,
    moduleWebpackConfig: moduleWebpackConfig,
    moduleRuleWebpackConfig: moduleRuleWebpackConfig,
    assetsPath: assetsPath,
    cssLoaders: cssLoaders,
    styleLoaders: styleLoaders
};

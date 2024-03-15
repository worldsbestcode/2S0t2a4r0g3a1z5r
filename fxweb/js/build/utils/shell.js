// Command-line argument parser
var minimist = require('minimist');

// Wrapper for *nix shell commands
var shelljs = require('shelljs');

// Common definitions for utils
var utilsDefs = require('./utils.json');

// Display help
function displayHelp(reason) {
    if (reason) {
        console.log(reason + '\n');
    }
    console.log(utilsDefs.help);
}

// Parse the arguments from the command line
function getArgs(argv, prodCallback, debugProdCallback, devCallback) {
    var parsedArgs = minimist(argv.slice(2));
    var canContinue = true;
    var helpReason = '';

    // Name of the product config to use
    var productName = '';
    var buildDir = '';

    // Try to get product name before anything else
    if (canContinue) {
        if (parsedArgs.product) {
            productName = parsedArgs.product;
        }
        // Failed to get product name
        else {
            helpReason = '"--product" argument is required';
            canContinue = false;
        }
    }

    if (canContinue) {
        if (parsedArgs.builddir) {
            buildDir = parsedArgs.builddir;
        } else {
            helpReason = '"--builddir" argument is required';
            canContinue = false;
        }
    }

    // Continue in either production or development mode
    if (canContinue) {
        if (parsedArgs.production) {
            prodCallback(productName, buildDir);
        }
        else if (parsedArgs.debugproduction) {
            debugProdCallback(productName, buildDir);
        }
        else if (parsedArgs.development) {
            devCallback(productName, buildDir);
        }
        // Failed to get which mode for the build script
        else {
            helpReason = 'Must specify either --production, --debugproduction, or --development';
            canContinue = false;
        }
    }

    // Display help if something failed
    if (!canContinue) {
        displayHelp(helpReason);
    }
}

// Ensure the output directory is clean
function makeAssetsDirectory(assetsPath) {
    // Nuke the assets path
    shelljs.rm('-rf', assetsPath);

    // Create the directory again
    shelljs.mkdir('-p', assetsPath);

    // Copy everything in the "static" directory
    shelljs.cp('-R', 'static/', assetsPath);
}

module.exports = {
    displayHelp: displayHelp,
    getArgs: getArgs,
    makeAssetsDirectory: makeAssetsDirectory
};

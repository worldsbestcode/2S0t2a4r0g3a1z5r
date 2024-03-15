// Loading spinner
var ora = require('ora');

// Common definitions for utils
var utilsDefs = require('./utils.json');

// Create a new loading spinner
function startSpinner(message) {
    var spinnerRef = ora(message);
    spinnerRef.start();
    return spinnerRef;
}

// Stop a loading spinner
function stopSpinner(spinnerRef) {
    spinnerRef.stop();
}

// Print random tips while the user waits for the build
function printRandomTip() {
    // Provide formatting
    function formatTip(message) {
        var header = '\nTip:\n';
        var footer = '\n';

        return header + message + footer;
    }

    // Randomly pick one
    function pickTip(tips) {
        var whichTip = Math.floor(Math.random() * tips.length);
        return formatTip(tips[whichTip]);
    }

    // Print a bit of advice
    console.log(pickTip(utilsDefs.tips));
}

module.exports = {
    startSpinner: startSpinner,
    stopSpinner: stopSpinner,
    printRandomTip: printRandomTip
};

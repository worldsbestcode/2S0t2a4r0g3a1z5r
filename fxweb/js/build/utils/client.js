/* eslint-disable */

// Receive push notifications
// see https://www.w3.org/TR/eventsource/
require('eventsource-polyfill');

// Browser-side client for hot-reloading webpack changes
var hotClient = require('webpack-hot-middleware/client?noInfo=true&reload=true');

// Watch for reload events
hotClient.subscribe(function (event) {
    if (event.action === 'reload') {
        window.location.reload();
    }
});

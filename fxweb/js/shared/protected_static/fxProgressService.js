/**
 * @author Matthew Seaworth <mseaworth@futurex.com>
 * @section LICENSE
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, LP. 2018
 * @brief Functions to ease updating a progress bar
 */
fxApp.factory('fxProgressService', ['$interval', '$window', function ($interval, $window) {

    /**
     * Create a progress object
     * @return {object}  A progress object
     */
    function makeProgress() {
        return {
            currentProgress: 0,
            minProgress: 0,
            maxProgress: 100
        };
    }

    /**
     * Update the progress value with a checked range
     * @param {object}  progress  A progress object
     * @param {number}  nextValue  The next progress value
     * @return {object}  progress  The updated progress
     */
    function updateProgress(progress, nextValue) {
        var next = nextValue;
        if (next > progress.maxProgress) {
            next = progress.maxProgress;
        } else if (next < progress.minProgress) {
            next = progress.minProgress;
        }

        progress.currentProgress = next;
        return progress;
    }

    /**
     * Update a progress object
     * @param {object}  progress  The progress object to update
     * @param {number}  delay  The millisecond delay
     * @param {number}  increment  The fractional increment of the progress bar
     * @param {number}  endValue  The target value after all slices have occurred
     */
    function timedUpdate(progress, delay, increment, endValue) {
        var slices = Math.ceil((endValue - progress.currentProgress) / increment) - 1;

        /**
         * Add a slice to the progress
         */
        function addSlice() {
            updateProgress(progress, progress.currentProgress + increment);
        }

        updateProgress(progress, increment);
        if (slices > 0 ) {
           $interval(addSlice, delay, slices);
        }
    }

    /**
     * Calculate an increment size
     * @param {number}  totalIncrement  The total increment after all increments have occurred
     * @param {number}  itemsPerIncrement  The number of things that happen per increment
     * @param {number}  itemCount  The number of items that have to occur
     */
    function incrementSize(totalIncrement, itemsPerIncrement, itemCount) {
        return itemCount <= 0 ? totalIncrement : (totalIncrement * itemsPerIncrement) / itemCount;
    }

    /**
     * Calculate the increment size based on the download size
     * @param {number}  totalIncrement  The total amount to increment
     * @param {number}  incrementTime  The time per increment
     * @param {number}  downloadSize  The uncompressed size of the download logs
     * @return {number}  incrementSize The increment size
     */
    function downloadIncrement(totalIncrement, incrementTime, downloadSize) {
        var landingLoad = $window.performance.timing.responseEnd - $window.performance.timing.responseStart;
        if (landingLoad <= 0) {
            landingLoad = 1;
        }

        // The landing page html is roughly 8kb and should not be cached
        var landingSize = 1024 * 8;
        var bytesPerIncrement = (incrementTime / landingLoad) * landingSize;
        return incrementSize(totalIncrement, bytesPerIncrement, downloadSize);
    }


    return {
        incrementSize: incrementSize,
        downloadIncrement: downloadIncrement,
        makeProgress: makeProgress,
        timedUpdate: timedUpdate,
        updateProgress: updateProgress
    };
}]);

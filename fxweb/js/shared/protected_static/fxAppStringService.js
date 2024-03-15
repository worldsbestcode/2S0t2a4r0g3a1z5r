/**
 * Provides common functions for string manipulation
 *
 * @returns {object}    helper functions for string manipulation
 */

var fxAppStringService = fxApp.factory('fxAppStringService',
    ['$q', '$timeout', '$window', 'fxAppService',
    function($q, $timeout, $window, fxAppService) {

    var MAX_NAME_SIZE = 30;
    var MAX_STR_SIZE = 4096;

	/**
	 * Convert dots to underscores in a string
	 *
	 * @param   {string}    str - a string with dots
	 * @returns {string}    the formatted string
	 */
	function dotsToUnderscores(str) {
		return str.replace(/\./g, '_');
	}

	/**
	 * Convert underscores to dots in a string
	 *
	 * @param   {string}    str - a string with underscores
	 * @returns {string}    the formatted string
	 */
	function underscoresToDots(str) {
		return str.replace(/_/g, '.');
	}

	/**
	 * Replaces all the spaces in a string with underscores
	 *
	 * @param   {string}    str - input string
	 * @returns {string}    resulting string
	 */
	function spacesToUnderscores(str) {
		return str.replace(/ /g, '_');
	}

	/**
	 * Saves a string decoded into an ArrayBuffer as a file
	 *
	 * @param {ArrayBuffer}    fileStr  - a string decoded into an ArrayBuffer
	 * @param {string}         filename - save the file as this name
	 */
	function downloadString(fileStr, filename) {
    var blob = new Blob([fileStr], {type: 'application/octet-stream'});
    downloadBlob(blob, fileStr, filename);
  }

  /** 
	 * Saves a plain text string to a file
	 *
	 * @param {string}    fileStr  - a normal UTF-16 encoded Javascript string 
	 * @param {string}    filename - save the file as this name
	 */
	function downloadPlainTextString(fileStr, filename) {
    var blob = new Blob([fileStr], {type: 'type/plain'});
    downloadBlob(blob, fileStr, filename);
  }

  function downloadBlob(blob, fileStr, filename) {
		if (fxAppService.isInternetExplorer()) {
			blobDownloadMS(blob, filename);
		}
		else if (fxAppService.isSafari()) {
			blobDownloadSafari(fileStr, filename);
		}
		else {
			blobDownloadLink(blob, filename);
		}
	}

	/**
	 * Saves a blob as a file by using msSaveBlob (for Internet Explorer)
	 *
	 * @param {blob}      blob - a Blob object ready to be downloaded
	 * @param {string}    filename - save the file as this name
	 */
	function blobDownloadMS(blob, filename) {
		window.navigator.msSaveBlob(blob, filename);
	}

	/**
	 * Saves a blob as a file (for Safari)
	 *
	 * @param {ArrayBuffer}    data - the data to be downloaded
	 * @param {string}         filename - save the file as this name
	 */
	function blobDownloadSafari(data, filename) {
		var dataURI = 'data:application/octet-stream,' + encodeURIComponent(data);

		var link = document.createElement('a');
		link.style = 'display: none';
		link.download = filename;
		link.href = dataURI;

		// trigger the downlaod
		link.click();
	}

	/**
	 * Saves a blob as a file by clicking a link to a hidden object in the DOM
	 *
	 * @param {blob}      blob - a Blob object ready to be downloaded
	 * @param {string}    filename - save the file as this name
	 */
	function blobDownloadLink(blob, filename) {
		var url = window.URL.createObjectURL(blob);

		var link = document.createElement('a');
		document.body.appendChild(link);
		link.style = 'display: none';
		link.download = filename;
		link.href = url;

		// trigger the download
		link.click();

		setTimeout(function() {
			window.URL.revokeObjectURL(url);
		}, 250);
	}

    /**
     * Saves a string from an encoded base64 string into a file
     * @param {string}  encoded  The base64 encoded string
     * @param {string}  filename  The filename to save the string to
     */
    function downloadBase64String(data, filename) {
        data = $window.atob(data).split('').map(function (character) {
            return character.charCodeAt(0);
        });

        data = new Uint8Array(data);
        downloadString(data, filename);
    }

	/**
	 * Replaces all semicolons in a string with commas
	 *
	 * @param   {string}    str - input string
	 * @returns {string}    resulting string
	 */
	function semicolonsToCommas(str) {
		return str.replace(/;/g, ',');
	}

	/**
	 * Removes all whitespace from a string
	 *
	 * @param   {string}    str - input string
	 * @returns {string}    resulting string
	 */
	function removeWhitespace(str) {
		return str.replace(/\s/g, '');
	}

	/**
	 * Formats CSV strings consistently
	 * (accepts either semicolons or commas as delimiters)
	 *
	 * @param   {string}    str - input string
	 * @returns {string}    resulting string
	 */
	function strToCSV(emails) {
		return removeWhitespace(semicolonsToCommas(emails));
	}

	/**
	 * Capitalizes the first letters of all the words in a string
	 *
	 * @param   {string}    str - A space-delimited string
	 * @returns {string}    the string of capitalized words
	 */
	function capitalizeFirstLetter(str) {

		// capitalize individual words
		function capitalize(word) {
			var firstLetter = word.charAt(0).toUpperCase();
			var restOfWord = word.slice(1).toLowerCase();
			return firstLetter + restOfWord;
		}

		// split string into words
		var words = str.split(' ');

		// the final result
		var capitalizedWords = [];

		// capitalize all the words
		words.map(function(word) {
			capitalizedWords.push(capitalize(word));
		});

		return capitalizedWords.join(' ');
	}

	/**
	 * Converts the output of Date().toISOString() into the expected format
	 *
	 * @param   {string}    isoTimeStr - ISO-8601 string
	 * @returns {string}    time string without the 'T' and 'Z' chars
	 */
	function ISOTimetoFXTime(isoTimeStr) {
		return isoTimeStr.replace(/T/g, ' ').replace(/\.[0-9]+Z/g, '');
	}

	/**
	 * Convert a comma-delimited string where each item is enclosed by
	 * curly braces into an array of strings
	 *
	 * @param   {array}     str - comma-delimited curly-brace-enclosed string
	 * @returns {string}    an array of strings
	 */
	function curlyBraceStringToArray(str) {
		var substr = str.substring(1, str.length-1);
		return substr.split('},{');
	}

	/**
	 * Convert a number from one base to another
	 *
	 * @param   {integer}    value       - the number
	 * @param   {integer}    source      - base the number is in
	 * @param   {integer}    destination - base to convert the number to
	 * @param   {integer}    padding     - number of digits the string should be
	 * @param   {boolean}    reverse     - whether to reverse the resulting string
	 * @returns {string}     the resulting number in another base
	 */
	function changeBase(value, source, destination, padding, reverse) {
		// Perform conversion
		var result = parseInt(value, source).toString(destination);

		// Add padding
		var zeroPadding = Array(padding+1).join('0');
		result = (zeroPadding + result).slice(-padding);

		// Reverse if needed
		return reverse ? result.split('').reverse().join('') : result;
	}

	/**
	 * Performs regex validation on each item in a CSV string
	 *
	 * @param   {string}     str   - the CSV string being validated
	 * @param   {string}     regex - the regex to validate against
	 * @returns {boolean}    whether all items match the regex
	 */
	function regexForCSV(str, regex) {
		var items = strToCSV(str).split(',');
		for (var i in items) {
			var results = items[i].match(regex);

			if (!(results && results.length > 0)) {
				return false;
			}
		};

		return true;
	}

	/**
	 * Provides the regex used to validate emails
	 * @returns {string}    email regex
	 */
	function emailRegex() {
		return "^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$";
	}

    /**
     * Provides the regex for an IPV4 address
     * @return {string} IPV4 regex
     */
    function ipv4Regex() {
        return "^(25[0-5]\|2[0-4]\\d\|1\\d\\d\|[1-9]\\d\|\\d)(\\.(25[0-5]\|2[0-4]\\d\|1\\d\\d\|[1-9]\\d\|\\d)){3}$";
    }

    /**
     * Provides the restriction for hostname regex
     * @return {string} hostname restriction
     */
    function ipv4Restrict() {
        return "[^0-9\\.]+";
    }

    /**
     * Provides the hostname regex
     * @return {string} hostname regex
     */
    function hostnameRegex() {
        return "[^\\[\\];<>]+";
    }

    /**
     * Provides the restriction for hostname regex
     * @return {string} hostname restriction
     */
    function hostnameRestrict() {
        return "[\\[\\];<>]+";
    }

    /**
     * Builds regex for names with common restricted characters
     *
     * @param minsize the minimum size of the field
     * @param maxsize the maximum size of the field
     *
     * @return {string} sized regex
     */
    function buildFieldRegex(minsize, maxsize) {
        var fullregex = "^[A-Za-z0-9 \\.\\-\\_\\`\\~\\!\\@\\#\\$\\%\\^\\&\\*\\(\\)\\+\\=\\,\\?\\{\\}\\<\\>\\:\\|\\/\\\\\"\']";
        fullregex += "{" + minsize + "," + maxsize + "}";
        fullregex += "$";
        return fullregex;
    }

    /**
     * Builds a regex for name fields
     *
     * @return {string} name field regex
     */
    function nameFieldRegex() {
        return buildFieldRegex(1, MAX_NAME_SIZE);
    }

    /**
     * Builds a regex for string fields
     *
     * @return {string} string field regex
     */
    function stringFieldRegex() {
        return buildFieldRegex(1, MAX_STR_SIZE);
    }

    /**
     * Converts seconds to a day, hour, minutes, seconds format
     *
     * @returns {string}   String in days, hour, minutes seconds format
     */
    function secondsToString(seconds) {
        var days    = Math.floor(seconds/86400);
        var hours   = Math.floor((seconds % 86400)/3600);
        var minutes = Math.floor(((seconds % 86400) % 3600)/60 );
        var seconds = ((seconds % 86400) % 3600) % 60;
        return days + " days " + hours + " hours " + minutes + " minutes " + seconds + " seconds ";
    }

    /**
     * Converts seconds to a day, hour format
     *
     * @returns {string}   String in days, hour format
     */
    function secondsToDayHourString(seconds) {
        var days    = Math.floor(seconds/86400);
        var hours   = Math.floor((seconds % 86400)/3600);
        return days + " days " + hours + " hours ";
    }

    /**
     * Converts seconds to a day, hour, minutes format
     *
     * @returns {string}   String in days, hour format
     */
    function secondsToDayHourMinuteString(seconds) {
        var days    = Math.floor(seconds/86400);
        var hours   = Math.floor((seconds % 86400)/3600);
        var minutes = Math.floor(((seconds % 86400) % 3600) / 60);
        return days + " days " + hours + " hours " +  minutes + " minutes";
    }

    /**
     * Converts seconds to a minute, second format
     *
     * @returns {string}   String in minute, second format
     */
    function secondsToMinuteSecString(seconds) {
     var minutes = Math.floor(((seconds % 86400) % 3600)/60);
     var seconds = ((seconds % 86400) % 3600) % 60;
     return minutes + " minutes " + seconds + " seconds ";
    }

    /**
     * Checks if a string starts with a substring
     * @param str the string
     * @param substr the substring
     * @return true if str starts with substr
     */
    function startsWith(str, substr) {
        return str.substring(0, substr.length) === substr;
    }

    /* Checks if a string includes a substring
     * @param str the string
     * @param substr the substring
     * @return true if str includes substr
     */
    function includes(str, substr) {
        return str.indexOf(substr) !== -1;
    }

	return {
		dotsToUnderscores: dotsToUnderscores,
		underscoresToDots: underscoresToDots,
		spacesToUnderscores: spacesToUnderscores,
        downloadBase64String: downloadBase64String,
    downloadString: downloadString,
    downloadPlainTextString: downloadPlainTextString,
		semicolonsToCommas: semicolonsToCommas,
		removeWhitespace: removeWhitespace,
		strToCSV: strToCSV,
		capitalizeFirstLetter: capitalizeFirstLetter,
		ISOTimetoFXTime: ISOTimetoFXTime,
		curlyBraceStringToArray: curlyBraceStringToArray,
		changeBase: changeBase,
		regexForCSV: regexForCSV,
		emailRegex: emailRegex,
		ipv4Regex: ipv4Regex,
		ipv4Restrict: ipv4Restrict,
		hostnameRegex: hostnameRegex,
		hostnameRestrict: hostnameRestrict,
		nameFieldRegex: nameFieldRegex,
		stringFieldRegex: stringFieldRegex,
        secondsToString: secondsToString,
        secodsToDayHourString : secondsToDayHourString,
        secondsToDayHourMinuteString: secondsToDayHourMinuteString,
        secondsToMinuteSecString : secondsToMinuteSecString,
        startsWith: startsWith,
        includes: includes
	};
}]);

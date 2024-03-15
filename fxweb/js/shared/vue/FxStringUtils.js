const MAX_NAME_SIZE = 30;

export default {
  'MAX_NAME_SIZE': MAX_NAME_SIZE,
  capitalizeFirstLetter: function (str) {
    /**
     * Capitalizes the first letters of all the words in a string
     *
     * @param   {string}    str - A space-delimited string
     * @returns {string}    the string of capitalized words
     */
    // capitalize individual words
    function capitalize (word) {
      var firstLetter = word.charAt(0).toUpperCase();
      var restOfWord = word.slice(1).toLowerCase();
      return firstLetter + restOfWord;
    }

    // split string into words
    var words = str.split(' ');

    // the final result
    var capitalizedWords = [];

    // capitalize all the words
    words.map(function (word) {
      capitalizedWords.push(capitalize(word));
    });

    return capitalizedWords.join(' ');
  },
  dotsToUnderscores: function (str) {
    /**
     * Convert dots to underscores in a string
     *
     * @param   {string}    str - a string with dots
     * @returns {string}    the formatted string
     */
    return str.replace(/\./g, '_');
  },
  underscoresToDots: function (str) {
    /**
     * Convert underscores to dots in a string
     *
     * @param   {string}    str - a string with underscores
     * @returns {string}    the formatted string
     */
    return str.replace(/_/g, '.');
  },
  buildFieldRegex: function (minsize, maxsize) {
    /**
     * Builds regex for names with common restricted characters
     *
     * @param minsize the minimum size of the field
     * @param maxsize the maximum size of the field
     *
     * @return {string} sized regex
     */
    var fullregex = "^[A-Za-z0-9 \\.\\-\\_\\`\\~\\!\\@\\#\\$\\%\\^\\&\\*\\(\\)\\+\\=\\,\\?\\{\\}\\<\\>\\:\\|\\/\\\\\"']";
    fullregex += '{' + minsize + ',' + maxsize + '}';
    fullregex += '$';
    return fullregex;
  },
  nameFieldRegex: function () {
    /**
     * Builds a regex for name fields
     *
     * @return {string} name field regex
     */
    return this.buildFieldRegex(1, this.MAX_NAME_SIZE);
  },
  ipv4Regex: function () {
    /**
     * Provides the regex for an IPV4 address
     * @return {string} IPV4 regex
     */
    return '^(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]\\d|\\d)(\\.(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]\\d|\\d)){3}$';
  },
  ipv4Restrict: function () {
  /**
   * Provides the restriction for hostname regex
   * @return {string} hostname restriction
   */
    return '[^0-9\\.]+';
  },
  removeWhitespace: function (str) {
    /**
    * Removes all whitespace from a string
    *
    * @param   {string}    str - input string
    * @returns {string}    resulting string
    */
    return str.replace(/\s/g, '');
  },
  semicolonsToCommas: function (str) {
    /**
    * Replaces all semicolons in a string with commas
    *
    * @param   {string}    str - input string
    * @returns {string}    resulting string
    */
    return str.replace(/;/g, ',');
  },
  strToCSV: function (emails) {
    /**
     * Formats CSV strings consistently
     * (accepts either semicolons or commas as delimiters)
     *
     * @param   {string}    str - input string
     * @returns {string}    resulting string
     */

    return this.removeWhitespace(this.semicolonsToCommas(emails));
  },
  regexForCSV: function (str, regex) {
    /**
     * Performs regex validation on each item in a CSV string
     *
     * @param   {string}     str   - the CSV string being validated
     * @param   {string}     regex - the regex to validate against
     * @returns {boolean}    whether all items match the regex
     */
    var items = this.strToCSV(str).split(',');
    for (var i in items) {
      var results = items[i].match(regex);

      if (!(results && results.length > 0)) {
        return false;
      }
    };

    return true;
  }
};

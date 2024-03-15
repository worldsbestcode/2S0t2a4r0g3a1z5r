export default {

  'objectFalse': function (obj) {
    /**
     * Checks if an object properties are all false
     * For an object property to be false all its non object properties must be false
     * @param obj the object to check
     * @return true if all properties are false, false otherwise
     */
    for (var prop in obj) {
      var val = obj[prop];
      if (typeof (val) === 'object') {
        if (!this.objectFalse(val)) {
          return false;
        }
      } else if (val) {
        return false;
      }
    }

    return true;
  },
  'calcWidth': function (columns) {
    /** Used to calculate column width as a percentage of the entire row
    * @param columns the number of columns for the row
    */
    var width = 100 / columns;
    return 'calc(' + width + '%)';
  }
};

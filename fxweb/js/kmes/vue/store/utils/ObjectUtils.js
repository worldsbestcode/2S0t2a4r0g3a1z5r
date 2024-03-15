/**
 * @section LICENSE
 *
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, L.P. 2018
 */

/**
 * Assigns all properties from source to dest, if they exist in dest.
 *
 * The 'dest' object should have no circular references, to avoid infinite loops.
 *
 * @param {object} dest - Destination object, where saving properties to.
 * @param {object} source - Source object, where getting properties from.
 */
function assignDefined (dest, source) {
  for (var prop in dest) {
    if (source[prop] === undefined) {
      continue;
    }

    // Recurse into sub-objects
    if (Object.prototype.toString.call(source[prop]) === '[object Object]') {
      assignDefined(dest[prop], source[prop]);
    } else {
      dest[prop] = source[prop];
    }
  }
}

/**
 * Recursively freezes an object.
 *
 * @param {object} target - The object to freeze
 *
 * @returns the frozen object
 */
function deepFreeze (target) {
  Object.freeze(target);

  let propNames = Object.getOwnPropertyNames(target);

  propNames.forEach(function (name) {
    let value = target[name];

    let isObject = value && (typeof value === 'object' || typeof value === 'function');

    if (isObject !== null && !Object.isFrozen(value)) {
      deepFreeze(value);
    }
  });

  return target;
}

export default {
  assignDefined,
  deepFreeze,
};

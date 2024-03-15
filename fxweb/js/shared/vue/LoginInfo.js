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
import utils from 'shared/utils';
import ClassPermissions from 'shared/ClassPermissions';

/**
 * Gets the login information
 *
 * @returns {object} the login information
 */
function getLoginInfo () {
  var cookie = utils.parseCookies('login_info');
  var errorRet = {
    isAdmin: false,
    permissions: {},
  };

  if (!cookie || !cookie.value) {
    return errorRet;
  }

  var loginInfo = JSON.parse(decodeURIComponent(cookie.value));

  if (loginInfo) {
    var permMap = [];

    loginInfo.isAdmin = (loginInfo.name === 'Admin Group');

    if (loginInfo.permissions[0].length > 0) {
      permMap = loginInfo.permissions.map(function (item) {
        var splitPerms = item.split(':');
        var permFlags = splitPerms[1].split('|').filter(function (permFlag) {
          console.log('Got flag: ' + permFlag);
          return permFlag !== '';
        });

        return [splitPerms[0], permFlags];
      });
    }

    loginInfo.permissions = new ClassPermissions(permMap, loginInfo.isAdmin);
  }

  return loginInfo || errorRet;
}

/**
 * Retrieves the class permissions from the login info.
 *
 * @param {object} loginInfo The login info retrieved from cookies
 *
 * @return the class permissions
 */
function getClassPermissions (loginInfo) {
  loginInfo = loginInfo || getLoginInfo();

  return loginInfo.permissions;
}

export default {
  getLoginInfo,
  getClassPermissions,
};

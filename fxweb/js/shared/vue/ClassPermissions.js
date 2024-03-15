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

class ClassPermissions {
  /**
   * Constructor.
   *
   * @param {iterable} permMap iterable of permission key:value pairs
   * @param {bool} isAdmin whether or not the user is admin
   */
  constructor (permMap, isAdmin) {
    this.permissions = new Map(permMap);
    this.isAdmin = isAdmin;
  }

  /**
   * Determines if the currently logged in user has the given class permissions
   *
   * This only checks for class type permissions, not class flag permissions.
   *
   * @param permissionClass The permission class
   *
   * @return True if they have perms, false if they do not
   */
  hasClassPermission (permissionClass) {
    var hasPerms = this.permissions.has(permissionClass);
    return this.isAdmin || hasPerms;
  }

  /**
   * Determines if the currently logged in user has the given class permissions.
   *
   * This checks both for class type and class flag permissions.
   *
   * @param permissionClass The permission class
   *
   * @return True if they have perms, false if they do not
   */
  hasPermission (permissionClass, permissionFlag) {
    var hasPerms = false;

    var activePermissions = this.permissions.get(permissionClass);
    if (activePermissions) {
      hasPerms = activePermissions.includes(permissionFlag);
    }

    return this.isAdmin || hasPerms;
  }

  canAddTokenGroups () {
    return this.hasPermission('Token', 'Add');
  }

  canDeleteTokenGroups () {
    return this.hasPermission('Token', 'Delete');
  }

  canAddCertAuthorities () {
    return this.hasPermission('CertManage', 'Add');
  }

  canDeleteCertAuthorities () {
    return this.hasPermission('CertManage', 'Delete');
  }
}

export default ClassPermissions;

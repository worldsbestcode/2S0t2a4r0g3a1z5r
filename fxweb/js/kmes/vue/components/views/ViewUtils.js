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

import TokenGroupManagement from 'kmes/components/views/TokenGroupManagement';
import CertificateAuthorityManagement from 'kmes/components/views/CertificateAuthorityManagement';
import CertificateManagement from 'kmes/components/views/CertificateManagement';

class ViewInfo {
  constructor (name, printable, cls, icon) {
    this.name = name;
    this.printable = printable;
    this.cls = cls;
    this.icon = icon;
  }
}

// All of the possible views that can be shown in MainCanvas
var views = [
  new ViewInfo(
    'token',
    'Token Groups',
    TokenGroupManagement,
    '/images/icons/token_group.png'),
  new ViewInfo(
    'ca',
    'Certificate Authorities',
    CertificateAuthorityManagement,
    '/images/icons/cert_authority.png'),
  new ViewInfo(
    'certificate',
    'Certificates',
    CertificateManagement,
    '/images/icons/cert_authority.png'),
];

/**
 * Retrieves the view components for the given views.
 *
 * @param {string[]} viewNames - The names of the views whose components we need
 *
 * @returns the components for the given view names
 */
function getViewComponents (viewNames) {
  var components = {};
  for (var idx in views) {
    var view = views[idx];

    if (viewNames == null || viewNames.includes(view.name)) {
      components[view.name] = view.cls;
    }
  }
  return components;
}

/**
 * Get view info for specified views.
 *
 * @param {string[]} viewNames - The names of the views whose info to get.
 *
 * @returns the view info for the given view names
 */
function getViewInfos (viewNames) {
  var infos = [];

  for (var idx in views) {
    var view = views[idx];

    if (viewNames == null || viewNames.includes(view.name)) {
      infos.push(view);
    }
  }

  return infos;
}

export default {
  getViewComponents,
  getViewInfos,
};

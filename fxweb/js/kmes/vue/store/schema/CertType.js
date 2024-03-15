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

import ObjectUtils from 'kmes/store/utils/ObjectUtils';

var certTypes = ObjectUtils.deepFreeze({
  X509Cert: { name: 'X.509', value: 0 },
  EMVCertVisa: { name: 'Visa EMV', value: 1 },
  EMVCertAmex: { name: 'Amex EMV', value: 2 },
  EMVCertMC: { name: 'MasterCard EMV', value: 3 },
  EMVCertJCB: { name: 'JCB EMV', value: 4 },
  EMVCertMultiBanco: { name: 'MultiBanco EMV', value: 5 },
  SCSARoot: { name: 'SCSA Root', value: 6 },
  SCSAUpperLevel: { name: 'SCSA Upper Level', value: 7 },
  EMVCertUP: { name: 'UPI EMV', value: 8 },
});

function fromValue (value) {
  for (var i in certTypes) {
    var type = certTypes[i];
    if (type.value === value) {
      return type;
    }
  }
  return certTypes.X509Cert;
}

function getTypeStrings () {
  return Object.keys(certTypes).map(x => certTypes[x].name);
}

export default {
  ...certTypes,
  fromValue,
  getTypeStrings,
};

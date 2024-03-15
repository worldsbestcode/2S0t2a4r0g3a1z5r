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

import CertType from 'kmes/store/schema/CertType';
import ViewAction from './ViewAction';

class ImportRootCertificateAction extends ViewAction {
  constructor (callback, components, props) {
    super('Import', 'Import Root Certificate', callback, components, props);
  }

  isEnabled (objectData) {
    if (objectData.objectType === 'CERTAUTHORITY') {
      let rootUnset = objectData.rootCertificateID === '-1';
      let typeAllows = objectData.pkiType === CertType.X509Cert.value;
      return rootUnset && typeAllows;
    }
    return false;
  }
}

export default ImportRootCertificateAction;

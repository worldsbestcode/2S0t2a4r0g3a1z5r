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

import ViewAction from './ViewAction';

class ImportCertificateAction extends ViewAction {
  constructor (callback, components, props) {
    super('Import Certificate', 'Import Certificate', callback, components, props);
  }

  isEnabled (objectData) {
    return objectData.objectType === 'X509CERT';
  }
}

export default ImportCertificateAction;

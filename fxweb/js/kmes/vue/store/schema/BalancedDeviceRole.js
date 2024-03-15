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

export default ObjectUtils.deepFreeze({
  INVALID: 'Invalid',
  APPDEVICE: 'Application Device',
  PRODUCTION: 'Production Device',
  BACKUP: 'Backup Device',
  PRIMARY: 'Primary Device',
  VERIFICATION: 'Verification Device',
  VERIFICATION_PRIMARY: 'Verification Primary',
});

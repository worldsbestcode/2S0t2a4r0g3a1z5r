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

import ManagedObjectSchema from './ManagedObjectSchema';

class BalancedDeviceSchema extends ManagedObjectSchema {
  constructor () {
    super();

    this.deviceSerial = '';
    this.deviceFirmware = '';
    this.deviceFeatures = '';
    this.deviceStatus = '';
    this.deviceAddress = '';
    this.currentRole = '';
    this.deviceRole = '';
    this.deviceHash = '';
    this.pingMiss = 0;
    this.statTotalErrors = 0;
    this.statTotalRequests = 0;
    this.statTPS = 0;
    this.statTPSMAX = 0;
    this.statConnCount = 0;
    this.statCPUUsage = 0;
    this.statCPUTemperature = 0;
    this.statCaseTemperature = 0;
    this.statDeviceMemory = 0;
    this.statUptime = 0;
    this.deviceModel = '';
    this.deviceName = '';
    this.deviceHostName = '';
    this.keepAliveStats = false;
    this.keepAliveAdmin = false;
    this.receiveSyslog = false;
  }
}

export default BalancedDeviceSchema;

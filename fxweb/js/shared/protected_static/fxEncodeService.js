/**
 * @section LICENSE
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, LP. 2017
 * @brief Handles Encoding/Decoding
 */
var fxEncodeService = fxApp.factory('fxEncodeService', [function() {

    // Moved to EncodingUtils.js
    return {
        arrayBufferToHex: Scaffolding.EncodingUtils.arrayBufferToHex,
        dataUrlToHex: Scaffolding.EncodingUtils.dataUrlToHex,
        hexDecode: Scaffolding.EncodingUtils.hexDecode,
        hexDecodeOctet: Scaffolding.EncodingUtils.hexDecodeOctet,
        hexEncode: Scaffolding.EncodingUtils.hexEncode,
        hexEncodeOctet: Scaffolding.EncodingUtils.hexEncodeOctet,
        hexToArrayBuffer: Scaffolding.EncodingUtils.hexToArrayBuffer,
        hexToBitLength: Scaffolding.EncodingUtils.hexToBitLength
    };
}]);

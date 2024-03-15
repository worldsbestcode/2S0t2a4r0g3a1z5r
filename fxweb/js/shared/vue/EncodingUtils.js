/**
 * @section LICENSE
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, L.P. 2018
 */

var BASE16 = 16;
var HEX_PER_BYTE = 2;
var NUMBER_BYTES = 256;

// Array of hex bytes from 00 to FF
var HEX = Array.apply(null, Array(NUMBER_BYTES)).map(function (_, index) {
  return ('0' + index.toString(BASE16)).slice(-HEX_PER_BYTE);
});

/**
 * Hex encodes a string (this doesn't work with utf-16)
 *
 * @param   {data}      data - object to hex encode
 * @returns {string}    Hex encoded string
 */
function hexEncode (data) {
  var encodedStr = '';
  for (var i in data) {
    // Take the character index and encode it into hex
    encodedStr += HEX[data.charCodeAt(i) % NUMBER_BYTES];
  }

  return encodedStr;
}

/**
 * Hex decodes a string
 *
 * @param   {data}      data - object to hex decode
 * @returns {string}    Hex decoded string
 */
function hexDecode (data) {
  var decodedStr = '';
  for (var j in data) {
    j = parseInt(j);
    if (j % 2 === 1) {
      var hexCode = parseInt(data.substring(j - 1, j + 1), 16);
      var decodedChar = String.fromCharCode(hexCode);
      decodedStr += decodedChar;
    }
  }

  return decodedStr;
}

/**
 * Converts a hex-encoded string to an ArrayBuffer
 *
 * @param   {string}         hexStr - A hex-encoded string
 * @returns {ArrayBuffer}    the raw binary representation of hexStr
 */
function hexToArrayBuffer (hexStr) {
  var buffer = new ArrayBuffer(hexStr.length / 2);
  var bufferAsUint8 = new Uint8Array(buffer);

  // check for an invalid hex string
  if (hexStr.length % 2 === 1) {
    return null;
  } else {
    // convert to array buffer
    for (var i = 0; i < hexStr.length; i += 2) {
      bufferAsUint8[i / 2] = parseInt(hexStr.substr(i, 2), 16);
    }
    return buffer;
  }
}

/**
 * Byte to hex no bounds checking
 * @param {number}  byteAsNumber  Integer from 0 to 255
 * @returns {string}  The number as a two character hex value
 */
function uncheckedByteToHex (byteAsNumber) {
  return HEX[byteAsNumber];
}

/**
 * Hex encode an ArrayBuffer
 * @param {ArrayBuffer}  buffer  An array buffer to encode
 * @returns {string}  hexValue  The buffer hex encoded
 */
function arrayBufferToHex (buffer) {
  return Array.from(new Uint8Array(buffer)).map(uncheckedByteToHex).join('');
}

/**
 * Hex encode a file read as a data url
 * @param {string}  data  The data url
 */
function dataUrlToHex (data) {
  // strip off the data type
  var binary = atob(data.split(',')[1]);
  return hexEncode(binary);
}

/**
 * Compute the bit length of a hex string
 * @param {string}  hexString  The hex string length
 * @returns {number}  The bit length of the hex string
 */
function hexToBitLength (hexString) {
  return hexString.length * 4;
}

/**
 * Hex encodes an array of octets into a hex string
 *
 * @param   {array}     decodedArr - array of decimal integers to hex encode
 *                      e.g. [ 13, 127, ... ] or [ "13", "127", ... ]
 * @returns {string}    Hex encoded string
 */
function hexEncodeOctet (decodedArr) {
  var encodedStr = '';
  var numDigits = 2;

  for (var i in decodedArr) {
    var num = decodedArr[i];

    // Individual octets can be either integer strings or plain integers
    if (typeof num === 'string') {
      num = parseInt(decodedArr[i]);
    }

    // Convert num to hex
    var hexValue = num.toString(16);

    // Pad by numDigits-1 number of zeros
    var zeroPadding = Array(numDigits).join('0');

    // Prepend the padding, but only use numDigits chars
    encodedStr += (zeroPadding + hexValue).slice(-numDigits);
  }

  return encodedStr;
}

/**
 * Hex decodes a hex string into an array of octets
 *
 * @param   {string}    encodedStr - string to hex decode
 * @returns {array}     Array of decimal integers
 */
function hexDecodeOctet (encodedStr) {
  var decodedArr = [];

  for (var j in encodedStr) {
    j = parseInt(j);
    if (j % 2 === 1) {
      var hexCode = parseInt(encodedStr.substring(j - 1, j + 1), 16);
      decodedArr.push(hexCode);
    }
  }

  return decodedArr;
}

export default {
  arrayBufferToHex: arrayBufferToHex,
  dataUrlToHex: dataUrlToHex,
  hexDecode: hexDecode,
  hexDecodeOctet: hexDecodeOctet,
  hexEncode: hexEncode,
  hexEncodeOctet: hexEncodeOctet,
  hexToArrayBuffer: hexToArrayBuffer,
  hexToBitLength: hexToBitLength
};

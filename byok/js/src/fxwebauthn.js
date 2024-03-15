/**
 * @file      fxwebauthn.js
 * @author    John Torres <jtorres@futurex.com>
 *
 * @section LICENSE
 *
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex, L.P.
 *
 * Copyright by:  Futurex, L.P. 2019
 *
 * This file contains all the utils for managing U2F. The only two functions that should be called
 * directly from this file are registerNewCredential and authenticateCredential. All others should
 * be treated as internal functions.
 */

import CBOR from "../libs/cbor-js";

/**
 * Register a new U2F credential
 */
function registerNewCredential(userName, challenge, userID) {
  // Create params [WebAuthn sec 5.4]
  const publicKeyCredentialCreationOptions = {
    publicKey: {
      rp: { name: "Futurex", id: window.location.hostname },
      user: {
        id: base64ToBuffer(userID),
        name: userName,
        displayName: userName,
      },
      pubKeyCredParams: [
        {
          type: "public-key",
          alg: -7,
        },
      ],
      authenticatorSelection: {
        authenticatorAttachment: "cross-platform",
        userVerification: "discouraged",
      },
      attestation: "direct",
      timeout: 60000,
      challenge: base64ToBuffer(challenge),
    },
  };

  let promise = navigator.credentials.create(
    publicKeyCredentialCreationOptions,
  );

  return (
    promise &&
    promise
      .then((newCred) => {
        return bundleRegisterResponse(newCred);
      })
      .catch((err) => {
        return Promise.reject(err);
      })
  );
}

/**
 * Signs and auth challenge for the u2f 2fa verification step
 */
function authenticateCredential(challenge, credNames) {
  // Request params [WebAuthn sec 5.5]
  const publicKeyCredentialRequestOptions = {
    publicKey: {
      challenge: base64ToBuffer(challenge),
      allowCredentials: makeCredentialFilter(credNames),
      timeout: 60000,
      userVerification: "discouraged",
      rpId: window.location.hostname,
    },
  };

  let promise = navigator.credentials.get(publicKeyCredentialRequestOptions);

  return (
    promise &&
    promise
      .then((assertion) => {
        return bundleAssertionResponse(assertion);
      })
      .catch((err) => {
        return Promise.reject(err);
      })
  );
}

// Bundle the assertion response
function bundleAssertionResponse(assertion) {
  var clientResponse = {};
  clientResponse.clientDataJSON = JSON.parse(
    bufferToString(assertion.response.clientDataJSON),
  );
  clientResponse.authData = parseAuthData(
    new Uint8Array(assertion.response.authenticatorData),
  );
  clientResponse.rawAuthData = new Uint8Array(
    assertion.response.authenticatorData,
  );
  clientResponse.signature = new Uint8Array(assertion.response.signature);
  clientResponse.rawId = new Uint8Array(assertion.rawId);

  // Recursively base64 encode arraybuffers
  encodeObjectRecursive(clientResponse);

  return window.btoa(JSON.stringify(clientResponse));
}

// Makes a credential array given a CSV of credential IDs
// Webauthn will refuse to sign a challenge without at least one ID
function makeCredentialFilter(credArray) {
  var ret = [];

  for (var i = 0; i < credArray.length; i++) {
    var obj = {
      type: "public-key",
      id: base64ToBuffer(credArray[i]),
    };
    ret.push(obj);
  }

  return ret;
}

/**
 * Formats the registration response in the way the firmware expects it to be.
 * The FW doesnt understand CBOR encoding, so we have to decode client side.
 * We also have to base64 encode any binary arrays in the response
 */
function bundleRegisterResponse(newCred) {
  // Bundle response
  var clientResponse = {};
  clientResponse.clientDataJSON = JSON.parse(
    bufferToString(newCred.response.clientDataJSON),
  );
  clientResponse.attestObj = CBOR.decode(newCred.response.attestationObject);
  clientResponse.attestObj.authData = parseAuthData(
    clientResponse.attestObj.authData,
  );
  clientResponse.attestObj.authData.attestCredData.COSEPublicKey = CBOR.decode(
    clientResponse.attestObj.authData.attestCredData.COSEPublicKey.buffer,
  );

  // Recursively base64 encode arraybuffers
  encodeObjectRecursive(clientResponse);

  return window.btoa(JSON.stringify(clientResponse));
}

/**
 * Parse the Authenticator Data object [Webauthn sec 6.1]
 */
function parseAuthData(buffer) {
  var result = {
    rpIdHash: "",
    flags: "",
    counter: "",
    attestCredData: {
      aaguid: undefined,
      credIDLenBuf: undefined,
      credID: undefined,
      COSEPublicKey: undefined,
    },
  };

  // We don't know the maximums but we can test for the minimum.
  // Must be at least 32 plus 1 for the flags
  const minBufferLength = 32 + 1;
  if (buffer.length < minBufferLength) {
    return result;
  }

  result.rpIdHash = buffer.slice(0, 32);
  buffer = buffer.slice(32);

  var flagsBuf = buffer.slice(0, 1);
  buffer = buffer.slice(1);

  result.flags = flagsBuf[0];
  var flagsObj = {
    up: Boolean(result.flags & 0x01),
    uv: Boolean(result.flags & 0x04),
    at: Boolean(result.flags & 0x40),
    ed: Boolean(result.flags & 0x80),
    flags: result.flags,
  };

  var counterBuf = buffer.slice(0, 4);
  buffer = buffer.slice(4);
  result.counter = readBE32(counterBuf);

  if (flagsObj.at) {
    result.attestCredData.aaguid = buffer.slice(0, 16);
    buffer = buffer.slice(16);

    result.attestCredData.credIDLenBuf = buffer.slice(0, 2);
    buffer = buffer.slice(2);

    let credIDLen = readBE16(result.attestCredData.credIDLenBuf);
    result.attestCredData.credID = buffer.slice(0, credIDLen);
    buffer = buffer.slice(credIDLen);

    result.attestCredData.COSEPublicKey = buffer;
  }

  return result;
}

/**
 * Recursively base64 encode all binary fields
 */
function encodeObjectRecursive(obj) {
  if (!obj) return obj;

  if (obj.constructor.name === "Object") {
    const keys = Object.keys(obj);
    for (var i = 0; keys.length && i < keys.length; i++) {
      var modObj = obj[keys[i]];
      if (modObj === null) continue;
      obj[keys[i]] = encodeObjectRecursive(modObj);
    }
  } else if (isTypedArray(obj)) {
    obj = arrayBufferToBase64(obj);
  } else if (obj.constructor === Array) {
    for (var j = 0; j < obj.length; j++) obj[j] = encodeObjectRecursive(obj[j]);
  }

  return obj;
}

function isTypedArray(obj) {
  var ret = false;

  if (typeof obj === "object") {
    var buf = obj.buffer ? obj.buffer : {};
    if (buf.constructor.name === "ArrayBuffer") ret = true;
  }

  return ret;
}

function bufferToString(buff) {
  var enc = new TextDecoder(); // always utf-8

  return enc.decode(buff);
}

/**
 * Convert a JS array buffer to a base64 string
 */
function arrayBufferToBase64(buffer) {
  var binary = "";
  var bytes = new Uint8Array(buffer);
  var len = bytes.byteLength;

  for (var i = 0; i < len; i++) binary += String.fromCharCode(bytes[i]);

  return window.btoa(binary);
}

/**
 * Convert a base64 string to a byte array
 */
function base64ToBuffer(str) {
  return Uint8Array.from(
    window.atob(str.replace(/_/g, "/").replace(/-/g, "+")),
    (c) => c.charCodeAt(0),
  );
}

function readBE32(buffer) {
  if (buffer.length !== 4) throw new Error("Only 4byte buffers allowed!");

  if (getEndian() !== "big") buffer = buffer.reverse();

  return new Uint32Array(buffer.buffer)[0];
}

function readBE16(buffer) {
  if (buffer.length !== 2) throw new Error("Only 2byte buffer allowed!");

  if (getEndian() !== "big") buffer = buffer.reverse();

  return new Uint16Array(buffer.buffer)[0];
}

function getEndian() {
  let arrayBuffer = new ArrayBuffer(2);
  let uint8Array = new Uint8Array(arrayBuffer);
  let uint16array = new Uint16Array(arrayBuffer);
  uint8Array[0] = 0xaa; // set first byte
  uint8Array[1] = 0xbb; // set second byte

  let endian = "big";
  if (uint16array[0] === 0xbbaa) endian = "little";

  return endian;
}

export default {
  registerNewCredential,
  authenticateCredential,
};

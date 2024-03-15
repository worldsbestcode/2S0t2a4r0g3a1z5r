function clusterSessionExpired() {
  alert("Your session expired and you have been logged out");
  location.reload();
}

function download(file, fileName) {
  if (typeof file === "string") {
    file = file.split("");
  }

  let a = document.createElement("a");
  let blob = new Blob(file);
  let blobUrl = window.URL.createObjectURL(blob);
  a.href = blobUrl;
  a.download = fileName;
  a.click();
  window.URL.revokeObjectURL(blobUrl);
}

function copyToClipboard(text) {
  let textArea = document.createElement("textArea");
  document.body.append(textArea);
  textArea.value = text;
  textArea.select();
  document.execCommand("copy");
  textArea.remove();
}

function toHexString(x) {
  return Number(x).toString(16).toUpperCase();
}

function isHex(input) {
  return /^[0-9A-Fa-f]+$/.test(input);
}

function newCanMFKWrap({ keyType, algorithm, modulus, curve }) {
  if (keyType === "Symmetric" && algorithm) {
    return ["DES", "2TDES", "3TDES"].includes(algorithm);
  }
  if (keyType === "RSA" && modulus) {
    return modulus <= 2048;
  }
  if (keyType === "ECC" && curve) {
    // curves where gauiECCurveBits // 2 <= 112 (equivalent to FXK_TYPE_DES3 via FXKGetStrength)
    return [
      "1.2.840.10045.3.1.1" /* T_PRIME_192 */,
      "1.3.132.0.33" /* T_PRIME_224 */,
      "1.3.36.3.3.2.8.1.1.1" /* T_BRAINPOOL_160 */,
      "1.3.36.3.3.2.8.1.1.3" /* T_BRAINPOOL_192 */,
      "1.3.36.3.3.2.8.1.1.5" /* T_BRAINPOOL_224 */,
    ].includes(curve);
  }
  return false;
}

function canMFKWrap(options) {
  const keyType = options.keyType.value;
  const algorithm = options.algorithm && options.algorithm.value;
  const modulus = options.modulus && options.modulus.value;
  const curve = options.curve && options.curve.value;
  return newCanMFKWrap({
    keyType: keyType,
    algorithm: algorithm,
    modulus: modulus,
    curve: curve,
  });
}

function sessionIdFromUri(uri) {
  let match = uri.match(/.*\/clusters\/sessions\/([^/]+)\//);
  return match && match[1];
}

export {
  clusterSessionExpired,
  download,
  copyToClipboard,
  toHexString,
  isHex,
  canMFKWrap,
  newCanMFKWrap,
  sessionIdFromUri,
};

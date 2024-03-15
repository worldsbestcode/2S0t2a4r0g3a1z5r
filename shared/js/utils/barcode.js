const ENCODED_UUID_LENGTH = 37;
const COMPRESSED_UUID_LENGTH = 32;
/**
 * Converts the uuid to the 37 long intenger
 * i.e 01eb7612-5098-0000-0012-8d392cd10bf6 -> 2551812532923314029770827115913087990
 */
function encodeUuidToBarcode(uuid) {
  let strippedUuid = uuid.replace(/-/g, "");
  let uuidDigit = BigInt(`0x${strippedUuid}`);
  let paddedUuidDigit = uuidDigit.toString(16).toUpperCase();
  let encodedUuid = BigInt(`0x${paddedUuidDigit}`).toString();

  if (encodedUuid.length < ENCODED_UUID_LENGTH) {
    encodedUuid.padStart(ENCODED_UUID_LENGTH, "0");
  }
  return encodedUuid;
}

/**
 * Converts the 37 long integer back into a uuid
 */
function decodeUuidFromBarcode(barcode) {
  // remove leading 0
  let unpaddedBarcode = barcode.replace(/^0+/, "");

  let uuidDigit = BigInt(unpaddedBarcode)
    .toString(16)
    .padStart(COMPRESSED_UUID_LENGTH, "0");

  let uuidPart1 = uuidDigit.slice(0, 8);
  let uuidPart2 = uuidDigit.slice(8, 12);
  let uuidPart3 = uuidDigit.slice(12, 16);
  let uuidPart4 = uuidDigit.slice(16, 20);
  let uuidPart5 = uuidDigit.slice(20, 32);
  let uuid = `${uuidPart1}-${uuidPart2}-${uuidPart3}-${uuidPart4}-${uuidPart5}`;

  return uuid;
}

export { decodeUuidFromBarcode, encodeUuidToBarcode, ENCODED_UUID_LENGTH };

import { toHexString } from "@/utils/misc.js";

function generateModifierAliases() {
  const modifierAliases = {
    0x00: "KEK",
    0x01: "PEK",
    0x02: "DEK",
    0x03: "MAK",
    0x04: "PVK",
    0x05: "ATM",
    0x06: "IV",
    0x07: "",
    0x08: "BDK",
    0x09: "PGK",
    0x0a: "",
    0x0b: "",
    0x0c: "",
    0x0d: "EMV",
    0x0e: "DTK",
    0x0f: "DEC TBL",
    0x10: "",
    0x11: "",
    0x12: "",
    0x13: "",
    0x14: "",
    0x15: "",
    0x16: "",
    0x17: "",
    0x18: "",
    0x19: "",
    0x1a: "",
    0x1b: "IDN",
    0x1c: "DAC",
    0x1d: "EVD",
    0x1e: "",
    0x1f: "",
  };

  const result = {};
  for (const [modifier, alias] of Object.entries(modifierAliases)) {
    if (alias) {
      result[modifier] = alias;
    } else {
      result[modifier] = toHexString(modifier).padStart(3, "0");
    }
  }
  return result;
}

const modifierAliases = generateModifierAliases();

const eccCurveOidToName = {
  "1.2.840.10045.3.1.1": "P-192",
  "1.3.132.0.33": "P-224",
  "1.2.840.10045.3.1.7": "P-256",
  "1.3.132.0.34": "P-384",
  "1.3.132.0.35": "P-521",
  "1.3.36.3.3.2.8.1.1.1": "Brainpool 160",
  "1.3.36.3.3.2.8.1.1.3": "Brainpool 192",
  "1.3.36.3.3.2.8.1.1.5": "Brainpool 224",
  "1.3.36.3.3.2.8.1.1.7": "Brainpool 256",
  "1.3.36.3.3.2.8.1.1.9": "Brainpool 320",
  "1.3.36.3.3.2.8.1.1.11": "Brainpool 384",
  "1.3.36.3.3.2.8.1.1.13": "Brainpool 512",
  "1.3.101.112": "Ed25519",
};

let symmetricTypes = ["DES", "2TDES", "3TDES", "AES-128", "AES-192", "AES-256"];

let privateTypes = [
  "RSA-512",
  "RSA-1024",
  "RSA-2048",
  "RSA-3072",
  "RSA-4096",
  "ECC",
];

const validSymmetricKeyUsagesForModifierGpMode = {
  0x00: [["Encrypt", "Decrypt"], ["Encrypt"], ["Decrypt"]],
  0x01: [["Encrypt", "Decrypt"], ["Encrypt"], ["Decrypt"]],
  0x02: [["Encrypt", "Decrypt"], ["Encrypt"], ["Decrypt"]],
  0x03: [["Sign", "Verify"], ["Sign"], ["Verify"]],
  0x04: [["Sign", "Verify"], ["Sign"], ["Verify"]],
  0x05: [["Encrypt", "Decrypt"], ["Encrypt"], ["Decrypt"]],
  0x06: [[]],
  0x07: [[]],
  0x08: [["Derive"]],
  0x09: [["Encrypt"]],
  0x0a: [[]],
  0x0b: [["Derive"]],
  0x0c: [[]],
  0x0d: [["Encrypt", "Decrypt"], ["Encrypt"], ["Decrypt"]],
  0x0e: [["Derive"]],
  0x0f: [[]],
  0x10: [[]],
  0x11: [[]],
  0x12: [[]],
  0x13: [[]],
  0x14: [[]],
  0x15: [[]],
  0x16: [[]],
  0x17: [[]],
  0x18: [[]],
  0x19: [[]],
  0x1a: [[]],
  0x1b: [["Derive"]],
  0x1c: [["Derive"]],
  0x1d: [["Encrypt", "Decrypt"], ["Encrypt"], ["Decrypt"]],
  0x1e: [[]],
  0x1f: [[]],
};

const validSymmetricKeyUsagesForModifierFinancialMode = {
  0x00: [["Wrap", "Unwrap"], ["Wrap"], ["Unwrap"]],
  0x01: [["Encrypt", "Decrypt"], ["Encrypt"], ["Decrypt"]],
  0x02: [["Encrypt", "Decrypt"], ["Encrypt"], ["Decrypt"]],
  0x03: [["Sign", "Verify"], ["Sign"], ["Verify"]],
  0x04: [
    ["Sign", "Verify"],
    ["Sign"],
    ["Verify"],
    ["Encrypt", "Decrypt"],
    ["Encrypt"],
    ["Decrypt"],
  ],
  0x05: [["Encrypt", "Decrypt"], ["Encrypt"], ["Decrypt"]],
  0x06: [[]],
  0x07: [[]],
  0x08: [["Derive"]],
  0x09: [["Sign", "Verify"], ["Sign"], ["Verify"], ["Encrypt"]],
  0x0a: [[]],
  0x0b: [["Derive"]],
  0x0c: [[]],
  0x0d: [
    ["Sign", "Verify"],
    ["Sign"],
    ["Verify"],
    ["Encrypt", "Decrypt"],
    ["Encrypt"],
    ["Decrypt"],
  ],
  0x0e: [["Sign", "Verify"], ["Sign"], ["Verify"], ["Derive"]],
  0x0f: [[]],
  0x10: [[]],
  0x11: [[]],
  0x12: [[]],
  0x13: [[]],
  0x14: [[]],
  0x15: [[]],
  0x16: [[]],
  0x17: [[]],
  0x18: [[]],
  0x19: [[]],
  0x1a: [[]],
  0x1b: [["Derive"]],
  0x1c: [["Derive"]],
  0x1d: [["Encrypt", "Decrypt"], ["Encrypt"], ["Decrypt"]],
  0x1e: [[]],
  0x1f: [[]],
};

const validPrivateKeyUsages = [
  ["Sign", "Verify"],
  ["Sign"],
  ["Verify"],
  ["Decrypt", "Encrypt"],
  ["Decrypt"],
  ["Encrypt"],
  ["Unwrap", "Wrap"],
  ["Unwrap"],
  ["Wrap"],
  ["Derive"],
];

const validPublicKeyUsages = [["Verify"], ["Encrypt"], ["Wrap"], ["Derive"]];

let asymmetricSecurityUsages = [
  "Private",
  "Sensitive",
  "Immutable",
  "Anonymous Signing",
];

let symmetricSecurityUsages = ["Private", "Sensitive", "Immutable"];

let asymmetricUsages = [
  "Encrypt",
  "Decrypt",
  "Wrap",
  "Unwrap",
  "Sign",
  "Verify",
  "Derive",
];

let symmetricUsages = [
  "Encrypt",
  "Decrypt",
  "Wrap",
  "Unwrap",
  "Sign",
  "Verify",
  "Derive",
];

function isSymmetric(type) {
  return symmetricTypes.includes(type.toUpperCase());
}

function isPrivate(type) {
  return privateTypes.includes(type.toUpperCase());
}

function getSecurityUsages(type) {
  if (isSymmetric(type)) {
    return symmetricSecurityUsages;
  } else {
    return asymmetricSecurityUsages;
  }
}

function getUsages(type) {
  if (isSymmetric(type)) {
    return symmetricUsages;
  } else {
    return asymmetricUsages;
  }
}

function getValidUsages({ type, gpMode, modifier }) {
  if (isSymmetric(type)) {
    if (gpMode) {
      return validSymmetricKeyUsagesForModifierGpMode[modifier];
    } else {
      return validSymmetricKeyUsagesForModifierFinancialMode[modifier];
    }
  } else if (isPrivate(type)) {
    return validPrivateKeyUsages;
  } else if (type !== "Diebold" && type !== "Certificate") {
    return validPublicKeyUsages;
  }
}

function disableUsage({ usageValue, usage, validUsages, immutable }) {
  if (immutable) {
    return true;
  }

  if (usage.length === 0) {
    let filteredValidUsages = validUsages
      .filter((x) => x.length === 1)
      .map((x) => x[0]);
    return !filteredValidUsages.includes(usageValue);
  } else {
    let currentUsage = usage[0];
    let dualUsages = validUsages.filter((x) => x.length === 2);
    let filteredValidDualUsages = dualUsages.filter((x) =>
      x.includes(currentUsage),
    )[0];
    if (dualUsages.length === 0 || !filteredValidDualUsages) {
      return currentUsage !== usageValue;
    } else {
      return !filteredValidDualUsages.includes(usageValue);
    }
  }
}

function validLabel(label) {
  return /^[a-zA-Z0-9_]{0,64}$/.test(label);
}

export {
  modifierAliases,
  isSymmetric,
  isPrivate,
  validSymmetricKeyUsagesForModifierGpMode,
  validSymmetricKeyUsagesForModifierFinancialMode,
  validPrivateKeyUsages,
  validPublicKeyUsages,
  asymmetricSecurityUsages,
  symmetricSecurityUsages,
  asymmetricUsages,
  symmetricUsages,
  getSecurityUsages,
  getUsages,
  getValidUsages,
  disableUsage,
  symmetricTypes,
  eccCurveOidToName,
  validLabel,
};

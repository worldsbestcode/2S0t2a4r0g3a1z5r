const eKeyType = Object.freeze({
  eMasterSession: 1,
  eDukptInitialKey: 2,
  eDukptBdkKey: 3,
  eMacKey: 4,
  ePinEncryptionKey: 5,
  eKeyTransferKey: 6,
  eHostVerificationKey: 7,
  eDukpt3DesBdkKey: 8,
  eDefaultKtk: 9,
  eDataEncryptionKey: 10,
  eDataDecryptionKey: 11,
  eDetachBdkKey: 12,
  eTerminalMasterKey: 13,
  eSerialNumberBdk: 14,
  eIvBdkKey: 15,
  eGenericBdk: 16,
  ePinGenerationKey: 17,
  eXacDKLK: 18,
  eTradeRootDukpt: 19,
  eAeviKbpk: 20,
  eAesDukptBdk: 25,
  eAesDukptInitial: 26,
});

const eKeyTypeToString = (eType) => {
  let sKeyType = "UNKNOWN";

  switch (eType) {
    case eKeyType.eMasterSession:
      sKeyType = "Master Session";
      break;
    case eKeyType.eDukptInitialKey:
      sKeyType = "DUKPT Initial";
      break;
    case eKeyType.eDukptBdkKey:
      sKeyType = "DUKPT BDK";
      break;
    case eKeyType.eMacKey:
      sKeyType = "MAC";
      break;
    case eKeyType.ePinEncryptionKey:
      sKeyType = "Pin Encryption";
      break;
    case eKeyType.eKeyTransferKey:
      sKeyType = "Key Transfer Key";
      break;
    case eKeyType.eHostVerificationKey:
      sKeyType = "Host Verification";
      break;
    case eKeyType.eDefaultKtk:
      sKeyType = "Default KTK";
      break;
    case eKeyType.eDukpt3DesBdkKey:
      sKeyType = "DUKPT 3DES BDK";
      break;
    case eKeyType.eDataEncryptionKey:
      sKeyType = "Data Encryption";
      break;
    case eKeyType.eDataDecryptionKey:
      sKeyType = "Data Decryption";
      break;
    case eKeyType.eDetachBdkKey:
      sKeyType = "Detach DBK";
      break;
    case eKeyType.eTerminalMasterKey:
      sKeyType = "Terminal master";
      break;
    case eKeyType.eSerialNumberBdk:
      sKeyType = "Serial Number BDK";
      break;
    case eKeyType.eIvBdkKey:
      sKeyType = "IV BDK";
      break;
    case eKeyType.eGenericBdk:
      sKeyType = "Generic BDK";
      break;
    case eKeyType.ePinGenerationKey:
      sKeyType = "Pin Generation";
      break;
    case eKeyType.eXacDKLK:
      sKeyType = "XAC DKLK";
      break;
    case eKeyType.eTradeRootDukpt:
      sKeyType = "Trade root DUKPT";
      break;
    case eKeyType.eAeviKbpk:
      sKeyType = "AEVI KBPK";
      break;
    case eKeyType.eAesDukptBdk:
      sKeyType = "AES DUKPT BDK";
      break;
    case eKeyType.eAesDukptInitial:
      sKeyType = "AES DUKPT INITIAL";
      break;
  }
  return sKeyType;
};

const eKeyLength = Object.freeze({
  eDES: 1,
  e2DES3: 2,
  e3DES3: 3,
  eAES128: 4,
  eAES192: 5,
  eAES256: 6,
});

const eKeyLengthToString = (eLength) => {
  let sKeyLength = "UNKNOWN";

  switch (eLength) {
    case eKeyLength.eDes:
      sKeyLength = "DES";
      break;
    case eKeyLength.e2DES3:
      sKeyLength = "2DES3";
      break;
    case eKeyLength.e3DES3:
      sKeyLength = "3DES3";
      break;
    case eKeyLength.eAES128:
      sKeyLength = "AES128";
      break;
    case eKeyLength.eAES192:
      sKeyLength = "AES192";
      break;
    case eKeyLength.eAES256:
      sKeyLength = "AES256";
      break;
  }

  return sKeyLength;
};

class KeyRestrictionSet {
  constructor() {
    this.allowedTypes = new Map();
  }

  setCombo(iKeyType, iKeyLength) {
    if (!this.allowedTypes.has(iKeyType)) {
      this.allowedTypes.set(iKeyType, new Set());
    }

    let tKeyLengthSet = this.allowedTypes.get(iKeyType);
    tKeyLengthSet.add(iKeyLength);
  }

  setComboSet(iKeyType, tKeyLengthSet) {
    if (tKeyLengthSet instanceof Set) {
      this.allowedTypes.set(iKeyType, tKeyLengthSet);
    }
  }

  setComboArray(iKeyType, vKeyLengths) {
    if (!this.allowedTypes.has(iKeyType)) {
      this.allowedTypes.set(iKeyType, new Set());
    }

    let tKeyLengthSet = this.allowedTypes.get(iKeyType);
    if (vKeyLengths instanceof Array) {
      vKeyLengths.forEach((iKeyLength) => {
        tKeyLengthSet.add(iKeyLength);
      });
    }
  }

  allowsCombo(iKeyType, iKeyLength) {
    let bAllowed = false;

    if (this.allowedTypes.has(iKeyType)) {
      let tKeyLengthSet = this.allowedTypes.get(iKeyType);
      bAllowed = tKeyLengthSet.has(iKeyLength);
    }

    return bAllowed;
  }

  flatten() {
    let result = [];
    for (let [keyType, keyLengthSet] of this.allowedTypes) {
      result.push({
        keyType: keyType,
        keyLengths: [...keyLengthSet],
      });
    }
    return result;
  }
}

// this is from FirmwareUtils.h
const FXKBitSize = [0, 64, 128, 192, 128, 192, 256];
const FXKEffectiveBitSize = [0, 56, 112, 168, 128, 192, 256];

function getKeyLengthFromBitSize(iBitSize, bIsAes) {
  let iTypeStart = bIsAes ? eKeyLength.eAES128 : eKeyLength.eDES;
  let iTypeEnd = bIsAes ? eKeyLength.eAES256 : eKeyLength.e3DES3;

  let iKeyType = 0;
  for (let iTypeLoop = iTypeStart; iTypeLoop <= iTypeEnd; iTypeLoop++) {
    if (
      FXKEffectiveBitSize[iTypeLoop] <= iBitSize &&
      iBitSize <= FXKBitSize[iTypeLoop]
    ) {
      iKeyType = iTypeLoop;
    }
  }
  return iKeyType;
}

class FXKey {
  constructor(uuid = "", name = "unknown", iKeyType = 0, iKeyLength = 0) {
    this.eKeyType = iKeyType;
    this.eKeyLength = iKeyLength;
    this.name = name;
    this.uuid = uuid;
  }

  fromProtoKey(key) {
    this.name = key.name;
    this.eKeyType = key.keyType;

    let bIsAes = false;
    if (key.algo === "Aes") {
      bIsAes = true;
    }

    this.eKeyLength = getKeyLengthFromBitSize(key.strength, bIsAes);
  }
}

export {
  eKeyLength,
  eKeyLengthToString,
  eKeyType,
  eKeyTypeToString,
  KeyRestrictionSet,
  FXKey,
};

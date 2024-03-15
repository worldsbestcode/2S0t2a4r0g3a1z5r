const eProtocols = Object.freeze({
  eProtocolNone: -1,
  eFuturex: 400,
  eVeriFonePP1000SE: 402,
  eVeriFoneIPP8: 403,
  eIngenicoNar: 408,
  eFXSP: 425,
  eIngenicoKiTBridge: 426,
});
const getProtocolName = (eProtocol) => {
  let name = "";
  switch (eProtocol) {
    case eProtocols.eVeriFoneIPP8:
      name = "VeriFone IPP8";
    case eProtocols.eVeriFonePP1000SE:
      name = "VeriFonePP1000SE";
      break;
    case eProtocols.eIngenicoNar:
      name = "Ingenico NAR/SSA";
      break;
    case eProtocols.eIngenicoKiTBridge:
      name = "Ingenico KitBridge";
      break;
    case eProtocols.eFXSP:
      name = "Futurex Secure";
      break;
    case eProtocols.eFuturex:
      name = "Futurex PED";
      break;
    default:
      break;
  }
  return name;
};

const generateDefaultKeyOptionsForProtocol = (eProtocol) => {
  let keyOptions = {};

  switch (eProtocol) {
    case eProtocols.eVeriFoneIPP8:
    case eProtocols.eVeriFonePP1000SE:
      keyOptions = {
        "@type": "fx/rkproto.cuserv.VeriFoneKeyOptions",
        keyUsage: "KeyEncryption",
      };
      break;
    case eProtocols.eIngenicoNar:
      keyOptions = {
        "@type": "fx/rkproto.cuserv.IngenicoNARKeyOptions",
        keyType: "Master",
        keyPurpose: "MSPinEncryption",
        appIds: [],
      };
      break;
    case eProtocols.eIngenicoKiTBridge:
      keyOptions = {
        "@type": "fx/rkproto.cuserv.KitBridgeKeyOptions",
        keyType: "Terminal",
        keyPurpose: "MSPinEncryption",
      };
      break;
    default:
      break;
  }
  return keyOptions;
};

const generateDefaultProtocolOptions = (eProtocol) => {
  let protocolOptions = {};

  switch (eProtocol) {
    case eProtocols.eVeriFoneIPP8:
    case eProtocols.eVeriFonePP1000SE:
      protocolOptions = {
        "@type": "fx/rkproto.cuserv.VeriFoneOptions",
        useTdes: true,
        zeroKey: false,
        emptyGiske: false,
        clearKeys: true,
      };
      break;
    case eProtocols.eIngenicoNar:
      protocolOptions = {
        "@type": "fx/rkproto.cuserv.IngenicoNAROptions",
        terminalBased: true,
        keyPattern: false,
        macPrompts: false,
        injectSerialNumberFirst: false,
        eraseAfterSn: false,
        macLength: "DontChange",
        promptMessages: [],
      };
      break;
    case eProtocols.eIngenicoKiTBridge:
      protocolOptions = {
        "@type": "fx/rkproto.cuserv.KitBridgeOptions",
        zmk: "",
      };
      break;
    case eProtocols.eFXSP:
      protocolOptions = {
        "@type": "fx/rkproto.cuserv.FXSPOptions",
        kbpk: "",
      };
      break;
    case eProtocols.eFuturex:
      protocolOptions = {
        "@type": "fx/rkproto.cuserv.FuturexOptions",
        ktkSlot: 0,
        deleteKeys: false,
        version2: false,
        tr31Mode: false,
        injectionScheme: "Legacy",
        bindingMethod: "VersionA",
        ktkKeyType: "KeyTransferKey",
        errors: false,
      };
      break;
    default:
      break;
  }
  return protocolOptions;
};

export {
  eProtocols,
  generateDefaultKeyOptionsForProtocol,
  generateDefaultProtocolOptions,
  getProtocolName,
};

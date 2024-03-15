import store from "@/store";
import router from "@/router";
import { httpV2 } from "@/plugins";

function getActiveCluster() {
  const route = router.currentRoute.value;
  const clusters = store.state.byok.clusters;
  return clusters.find((x) => x.id === route.params.clusterId);
}

function getSessionId() {
  return getActiveCluster().session.id;
}

function isGpMode() {
  return getActiveCluster().features.includes("GP");
}

function sessionUrl() {
  return `/clusters/sessions/${getSessionId()}`;
}

export function randomKey({
  loadingToKeySlot,
  keyType,
  keySlot,
  label,
  majorKey,
  usage,
  securityUsage,
  algorithm,
  modifier,
  modulus,
  exponent,
  curve,
}) {
  function buildUrl({ loadingToKeySlot, keyType, keySlot }) {
    let url;
    if (loadingToKeySlot) {
      url = `${sessionUrl()}/keytable`;
      if (!isGpMode()) {
        url += "/";
        if (keyType === "Symmetric") {
          url += "symmetric";
        } else {
          url += "asymmetric";
        }
      }
      if (keySlot !== -1) {
        url += `/${keySlot}`;
      }
    } else {
      url = `${sessionUrl()}/keyblock`;
    }
    return url;
  }

  const url = buildUrl({ loadingToKeySlot, keyType, keySlot });

  const key = {
    label: label,
    majorKey: majorKey,
    usage: usage.length === 0 ? null : usage,
    securityUsage: securityUsage,
  };
  switch (keyType) {
    case "Symmetric":
      key.type = algorithm;
      key.modifier = modifier;
      break;
    case "RSA":
      key.modulus = modulus;
      key.exponent = exponent;
      break;
    case "ECC":
      key.curve = curve;
      break;
  }

  const body = {
    key: key,
  };

  return new Promise((resolve, reject) => {
    async function generateKey() {
      try {
        const data = await httpV2.post(url, body, { silenceToastError: true });
        resolve(data);
      } catch (error) {
        if (error.message === "Key generation in progress") {
          setTimeout(generateKey, 1000);
        } else {
          reject(error);
        }
      }
    }
    generateKey();
  });
}

export function translateKey({
  keyType,
  keyBlock,
  keyModifier,
  keyAlgorithm,
  outputFormat,
  iv,
  clearIv,
  padding,

  wrappedByMajorKey,
  wrappingMajorKey,
  wrappingKekKeySlot,

  newWrappingKeyIsMajorKey,
  newWrappingMajorKey,
  newWrappingKekKeySlot,

  newKeyBlockHeader,
  newUsage,
  newSecurityUsage,
  newOutputFormat,
  newIv,
  newClearIv,
  newPadding,
}) {
  const url = `${sessionUrl()}/keyblock/translate`;
  const body = {
    key: {},
    outputFormat: {},
    usage: newUsage.length === 0 ? null : newUsage,
    securityUsage: newSecurityUsage,
    header: newKeyBlockHeader,
  };

  if (newKeyBlockHeader) {
    body.header = newKeyBlockHeader;
  }

  if (keyType === "Symmetric") {
    body.key.keyBlock = keyBlock;

    if (wrappedByMajorKey) {
      body.key.modifier = keyModifier;
    } else {
      body.key.type = keyAlgorithm;
    }
  } else {
    // keyType is private
    body.key.privateKeyBlock = keyBlock;

    if (!wrappedByMajorKey) {
      // Back end does not care about private key type
      // so we hard code ECC.
      body.key.type = "ECC";
    }
  }

  if (wrappedByMajorKey) {
    body.key.majorKey = wrappingMajorKey;
  } else {
    // wrapped by a KEK
    body.key.kekSlot = wrappingKekKeySlot;

    if (["KWP", "ECB", "CBC"].includes(outputFormat)) {
      body.key.cipher = {
        type: outputFormat,
        iv,
        clearIv,
        padding,
      };
    }
  }

  if (newWrappingKeyIsMajorKey) {
    body.outputFormat.majorKey = newWrappingMajorKey;

    if (!wrappedByMajorKey) {
      if (keyType === "Symmetric") {
        body.outputFormat.modifier = keyModifier;
      }
    }
  } else {
    // wrapped by a KEK
    body.outputFormat.kekSlot = newWrappingKekKeySlot;

    if (["KWP", "ECB", "CBC"].includes(newOutputFormat)) {
      body.outputFormat.cipher = {
        type: newOutputFormat,
        iv: newIv,
        clearIv: newClearIv,
        padding: newPadding,
      };
    }
  }

  return httpV2.post(url, body, { silenceToastError: true });
}

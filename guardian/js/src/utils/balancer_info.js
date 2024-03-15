export function deviceTypeToProtocols(device_type) {
  var available_protocols = ["Excrypt", "Http"];
  if (device_type == "Hsm") {
    available_protocols.push("Standard");
    available_protocols.push("International");
  }

  return available_protocols;
}

export function allDeviceTypes() {
  return ["Hsm", "Kmes", "Rkms", "CryptoHub", "MultiHsm"];
}

export function protocolToCommandSets(device_type, protocol) {
  var all_command_sets = [];
  if (protocol == "Excrypt") {
    if (
      device_type == "Kmes" ||
      device_type == "Rkms" ||
      device_type == "CryptoHub"
    ) {
      all_command_sets.push("HostApi");
      all_command_sets.push("Peering");
    }
    if (device_type == "Rkms") {
      all_command_sets.push("RemoteKeyLoading");
    }
    if (device_type == "Hsm" || device_type == "MultiHsm") {
      all_command_sets.push("HsmManagement");
      all_command_sets.push("HsmProduction");
    }
  } else if (protocol == "Http") {
    if (
      device_type == "Kmes" ||
      device_type == "Rkms" ||
      device_type == "CryptoHub"
    ) {
      all_command_sets.push("RestApi");
      all_command_sets.push("RemoteDesktop");
    }
    if (device_type == "Kmes" || device_type == "CryptoHub") {
      all_command_sets.push("Ocsp");
      all_command_sets.push("Scep");
      all_command_sets.push("RegistrationAuthority");
    }
    if (device_type == "CryptoHub") {
      all_command_sets.push("GuardianConfiguration");
      all_command_sets.push("GuardianByok");
    }
    all_command_sets.push("JsonExcrypt");
  }

  return all_command_sets;
}

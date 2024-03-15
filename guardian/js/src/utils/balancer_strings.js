export function deviceTypeDisplay(device_type) {
  if (device_type == "Hsm") return "HSM";
  if (device_type == "Kmes") return "KMES";
  if (device_type == "Rkms") return "RKMS";
  if (device_type == "CryptoHub") return "CryptoHub";
  if (device_type == "MultiHsm") return "Multi-HSM";
  return device_type;
}

export function protocolDisplay(protocol) {
  if (protocol == "Http") return "HTTP";
  return protocol;
}

export function commandSetDisplay(command_set) {
  if (command_set == "HostApi") return "Host-API";
  if (command_set == "RestApi") return "REST API";
  if (command_set == "RemoteKeyLoading") return "Remote Key Loading";
  if (command_set == "RemoteDesktop") return "Remote Desktop";
  if (command_set == "GuardianConfiguration") return "Guardian Configuration";
  if (command_set == "GuardianByok") return "Guardian BYOK";
  if (command_set == "Ocsp") return "OCSP";
  if (command_set == "Scep") return "SCEP";
  if (command_set == "JsonExcrypt") return "JSON Excrypt Production";
  if (command_set == "RegistrationAuthority") return "Registration Authority";
  if (command_set == "HsmProduction") return "HSM Production";
  if (command_set == "HsmManagement") return "HSM Management";
  return command_set;
}

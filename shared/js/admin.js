export const adminSetups = [
  { type: "License", path: "license", text: "License" },
  { type: "SecureMode", path: "secure", text: "Secure Mode" },
  { type: "MajorKeys", path: "major", text: "Major Keys" },
  { type: "Networking", path: "networking", text: "Networking" },
  { type: "DateTime", path: "date", text: "Date & Time" },
  { type: "AutomaticBackups", path: "automatic", text: "Automatic Backups" },
  { type: "JoinCluster", path: "join", text: "Join Clusters" },
];

export const hardwareTasks = ["Networking", "DateTime"];
export const cloudRestrictedTasks = ["SecureMode", "MajorKeys", "JoinCluster"];
export const dualControlTasks = ["SecureMode", "MajorKeys"];

export const adminSetupsOrder = adminSetups.map((x) => x.type);

export function adminLink(type) {
  const path = adminSetups.find((x) => x.type === type)?.path;
  if (path) {
    return `/admin/#/pending/${path}`;
  } else {
    return undefined;
  }
}

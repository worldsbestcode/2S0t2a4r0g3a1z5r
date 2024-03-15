import TimeAgo from "javascript-time-ago";
import en from "javascript-time-ago/locale/en";

TimeAgo.addDefaultLocale(en);
const timeAgo = new TimeAgo("en-US");

export function toTimeAgo(timestamp) {
  const date = new Date(Number(timestamp * 1000));
  return timeAgo.format(date);
}

export function download(file, fileName) {
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

export function arrayToCsv(data) {
  // https://stackoverflow.com/a/68146412
  return data
    .map(
      (row) =>
        row
          .map(String) // convert every value to String
          .map((v) => v.replaceAll('"', '""')) // escape double colons
          .map((v) => `"${v}"`) // quote it
          .join(",") // comma-separated
    )
    .join("\r\n"); // rows starting on new lines
}

// https://stackoverflow.com/a/16245768
const b64toBlob = (b64Data, contentType = "", sliceSize = 512) => {
  const byteCharacters = atob(b64Data);
  const byteArrays = [];

  for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
    const slice = byteCharacters.slice(offset, offset + sliceSize);

    const byteNumbers = new Array(slice.length);
    for (let i = 0; i < slice.length; i++) {
      byteNumbers[i] = slice.charCodeAt(i);
    }

    const byteArray = new Uint8Array(byteNumbers);
    byteArrays.push(byteArray);
  }

  const blob = new Blob(byteArrays, { type: contentType });
  return blob;
};

export function downloadEndpointFile(
  endpointFiles,
  endpointName,
  endpointObjectName,
) {
  const decodedEndpointFiles = b64toBlob(endpointFiles);
  const a = document.createElement("a");
  const blobUrl = window.URL.createObjectURL(decodedEndpointFiles);
  a.href = blobUrl;
  a.download = `${endpointObjectName}-${endpointName}.zip`.replaceAll(" ", "_");
  a.click();
  window.URL.revokeObjectURL(blobUrl);
}

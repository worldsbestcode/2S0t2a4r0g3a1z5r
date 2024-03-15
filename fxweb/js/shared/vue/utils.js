export default {
  parseCookies (name) {
    var cookies = document.cookie.split(';').map(function (cookieStr) {
      // Remove whitespace
      var trimmedStr = cookieStr.trim();
      // Split into key and value
      var keyValuePair = trimmedStr.split('=');
      return {
        name: keyValuePair[0],
        value: keyValuePair[1]
      };
    });

    // Return the cookie requested by name if specified
    if (name) {
      var results = cookies.filter(function (cookie) {
        return cookie.name === name;
      });

      return results.length ? results[0] : {};
    }
  },
  downloadFile (fileString, fileType, fileName) {
    var data = encodeURIComponent(fileString);
    var dataURL = 'data:' + fileType + ';charset=utf-8,' + data;

    var downloadLink = document.createElement('a');
    downloadLink.setAttribute('href', dataURL);
    downloadLink.setAttribute('download', fileName);
    downloadLink.setAttribute('style', 'display: none');

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
  },
};

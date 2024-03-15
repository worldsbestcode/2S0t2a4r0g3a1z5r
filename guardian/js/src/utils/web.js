// Set an error from an axios error
export function unwrapErr(err) {
  var ret = "";
  try {
    ret = err.response.data.message;
  } catch (trash) {
    ret = err;
  }

  if (ret == undefined || ret == null || ret.length == 0)
    ret = "Internal error.";

  return ret;
}

// Parse out the hash parameters
// Ignores the beginning part which is the router
export function getHashParams() {
  var hash = window.location.hash;
  var pos = hash.indexOf("?");
  if (pos == -1) hash = "";
  else hash = hash.substr(pos + 1);
  var result = hash.split("&").reduce(function (res, item) {
    var parts = item.split("=");
    res[parts[0]] = parts[1];
    return res;
  }, {});

  return result;
}

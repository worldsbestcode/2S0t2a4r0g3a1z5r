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
    res[parts[0]] = decodeURIComponent(parts[1]);
    return res;
  }, {});

  return result;
}

// Encode a dictionary into URL parameters
export function encodeUrlParams(params) {
  var str = [];
  for (var p in params)
    str.push(encodeURIComponent(p) + "=" + encodeURIComponent(params[p]));
  return str.join("&");
}

// Set a URL hash parameter
export function setHashParam(param, value) {
  var hash = window.location.hash;
  var pos = hash.indexOf("?");
  var route = "";
  if (pos == -1) {
    route = hash;
    hash = "";
  } else {
    route = hash.substr(0, pos);
    hash = hash.substr(pos + 1);
  }

  var result = hash.split("&").reduce(function (res, item) {
    var parts = item.split("=");
    res[parts[0]] = parts[1];
    return res;
  }, {});

  result[param] = value;
  window.location.hash = route + "?" + encodeUrlParams(result);
}

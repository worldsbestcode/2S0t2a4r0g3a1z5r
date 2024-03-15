$('#container').append($('<div/>').text('Loading...'));

if (typeof window.fxctx === 'undefined') {
  var fxctx = {
    keys: {
      isExcryptTouch: (fn) => fn(false),
      getVersion: (fn) => fn('Unsupported'),
    },
  };
}

function __init__ () {
  fxctx.keys.getVersion((version) => console.log('JS API version: ' + version));

  function failQueue (msg) {
    console.log(msg);
    $('#container').append($('<div/>', { id: 'errorMessage' }).text(msg));
    $(this).clearQueue();
  }

  $({})
    .queue(function (next) {
      fxctx.keys.isExcryptTouch((result) => {
        if (!result) failQueue('Device not supported');

        next();
      });
    })
    .queue(function (next) {
      fxctx.keys.getPKIAuthCert((result) => {
        if (!result.success) return failQueue(result.msg);

        this.authCertData = result.value
          .match(/.{1,2}/g)
          .map(function (v) {
            return String.fromCharCode(parseInt(v, 16));
          })
          .join('');
        next();
      });
    })
    .queue(function (next) {
      $.ajax({
        url: '/byok/v1/login',
        method: 'POST',
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        data: JSON.stringify({
          authType: 'pkiChallenge',
          authCredentials: {
            certData: btoa(this.authCertData),
          },
        }),
      })
        .fail((result) =>
          failQueue(result.statusText + (result.responseJSON ? ': ' + result.responseJSON.message : ''))
        )
        .success((result) => {
          this.pkiChallengeNonce = atob(result.response.challenge);
          next();
        });
    })
    .queue(function (next) {
      fxctx.login.signAuthPKI(this.pkiChallengeNonce, (result) => {
        if (!result.success) return failQueue(result.msg);

        this.pkiSignedNonce = result.value
          .match(/.{1,2}/g)
          .map(function (v) {
            return String.fromCharCode(parseInt(v, 16));
          })
          .join('');
        next();
      });
    })
    .queue(function (next) {
      $.ajax({
        url: '/byok/v1/login',
        method: 'POST',
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        data: JSON.stringify({
          authType: 'pkiSignature',
          authCredentials: {
            signature: btoa(this.pkiSignedNonce),
          },
        }),
      })
        .fail((result) =>
          failQueue(result.statusText + (result.responseJSON ? ': ' + result.responseJSON.message : ''))
        )
        .success((result) => next());
    })
    .queue(function (next) {
      window.location = '/byok/landing';
    });
}

// Wait for the qwebchannel to be injected
$(() => setTimeout(__init__, 200));

<template>
  <div style="width: 0px; height: 0px">
    <!-- just made it a component so the code is modular -->
    <!-- erlliam gonna delete this -->
  </div>
</template>

<script>
import axios from "axios";
import fxwebauthn from "$shared/utils/fxwebauthn";
import { unwrapErr } from "$shared/utils/web";

export default {
  name: "FidoEvents",
  mounted() {
    setTimeout(this.pollEvents.bind(this), 100);
  },
  methods: {
    pollEvents() {
      const fido = this;
      try {
        axios.get("/rd/v1/fido").then(async function (res) {
          if (res.data.command && res.data.command == "check") {
            fido.checkDevice();
          } else if (res.data.command && res.data.command == "newCredential") {
            await fido.newCredential(
              res.data.data.username,
              res.data.data.userId,
              res.data.data.challenge,
            );
          } else if (res.data.command && res.data.command == "signChallenge") {
            await fido.signChallenge(
              res.data.data.credentials,
              res.data.data.challenge,
            );
          }
        });
        // Handle error
      } catch (err) {
        fido.setError(err);
      }

      setTimeout(this.pollEvents.bind(this), 2000);
    },
    checkDevice() {
      // We can't check if the device is plugged in
      // But we can tell the back-end they made it
      // to the front-end
      try {
        var params = {
          response: "true",
        };
        axios.post("/rd/v1/fido", params);
      } catch {
        // Ignore
      }
    },
    async newCredential(username, userId, challenge) {
      try {
        let attestation = await fxwebauthn.registerNewCredential(
          username,
          challenge,
          userId,
        );
        this.respond({ response: attestation });
      } catch (error) {
        this.setError(error.message);
      }
    },
    async signChallenge(credentials, challenge) {
      try {
        let attestation = await fxwebauthn.authenticateCredential(
          challenge,
          credentials,
        );
        this.respond({ response: attestation });
      } catch (error) {
        this.setError(error.message);
      }
    },
    setError(err) {
      // Tell the back-end there was an error
      err = unwrapErr(err);
      this.respond({ error: err });
    },
    respond(params) {
      try {
        axios.post("/rd/v1/fido", params);
      } catch {
        // Ignore
      }
    },
  },
};
</script>

<template>
  <div id="base">
    <header class="login-header">
      <p id="name">{{ currentCluster.name }}</p>
      <img class="fx-logo-small" :src="logoMarkUrl" />
    </header>

    <div id="body">
      <form id="form">
        <div id="descriptor-wrap">
          <div
            v-if="challengesAnswered !== null && amountOfChallenges !== null"
          >
            <p>
              {{ challengesAnswered }} / {{ amountOfChallenges }} challenges
              answered.
            </p>
            <p>
              Insert your security key and if it has a button, press the button.
            </p>
          </div>
          <p id="descriptor">Identity {{ numUsers + 1 }} login</p>
          <span class="small-name-badge small-name-badge-2"
            ><i :class="icon"></i
          ></span>
          <span class="small-name-badge small-name-badge-2"
            ><i class="fa fa-user-slash"></i
          ></span>
        </div>
        <div id="interactive">
          <div id="submit-wrap">
            <button
              id="submit"
              :disabled="authButtonDisabled"
              @click.prevent="authenticateUser"
            >
              <i class="fa fa-arrow-right"></i>
            </button>
          </div>
          <section id="inputs" :key="numUsers">
            <input
              id="top-input"
              ref="usernameInput"
              v-model="username"
              placeholder="Username"
            />
            <input
              id="bottom-input"
              v-model="password"
              type="password"
              placeholder="Password"
            />
          </section>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import fxwebauthn from "@/fxwebauthn";
import logoMarkUrl from "/fx_logo_mark_official.png";

export default {
  props: {
    currentCluster: Object,
  },
  setup: function () {
    return { logoMarkUrl };
  },
  data: function () {
    return {
      username: null,
      password: null,
      authButtonDisabled: false,
      amountOfChallenges: null,
      challengesAnswered: null,
    };
  },
  computed: {
    numUsers: function () {
      if (this.$store.state.byok.clusters.length === 0) {
        return 0;
      } else {
        return this.currentCluster.session.identities.length;
      }
    },
    icon: function () {
      if (this.currentCluster.session.identities.length === 1) {
        return "fas fa-user";
      } else {
        return "fas fa-user-slash";
      }
    },
  },
  mounted: function () {
    if (this.$refs.usernameInput) {
      this.$refs.usernameInput.focus();
    }
  },
  methods: {
    validateInput: function () {
      let validationError = null;
      if (!this.username) {
        validationError = "Username required";
      } else if (!this.password) {
        validationError = "Password required";
      } else if (
        this.currentCluster.session.identities.includes(this.username)
      ) {
        validationError = "User already logged in";
      }

      if (validationError) {
        this.$bus.emit("toaster", { message: validationError });
        throw Error("Invalid input");
      }
    },

    initializeSession: function () {
      if (this.currentCluster.session.id) {
        return;
      }

      let url = "/clusters/sessions";
      let body = {
        group: this.currentCluster.id,
      };
      return this.$httpV2
        .post(url, body, {
          errorContextMessage: "Failed to create cluster session",
        })
        .then((data) => {
          this.$store.commit("byok/makeClusterSession", {
            cluster: this.currentCluster,
            sessionId: data.id,
          });
        });
    },

    userPassLogin: function () {
      let loginUrl = `/clusters/sessions/${this.currentCluster.session.id}/login`;
      let loginBody = {
        authType: "userpass",
        authCredentials: {
          username: this.username,
          password: btoa(this.password),
        },
      };
      return this.$httpV2.post(loginUrl, loginBody, {
        errorContextMessage: "Failed to login",
      });
    },

    u2fLogin: async function (loginData) {
      let loginUrl = `/clusters/sessions/${this.currentCluster.session.id}/login`;
      let u2fLogin = false;
      let challenges = loginData.u2fChallenge;
      let credentials = loginData.u2fCredentials;

      let attestations = [];
      if (challenges && credentials) {
        u2fLogin = true;
        this.amountOfChallenges = challenges.length;
        this.challengesAnswered = 0;
        for (let challenge of challenges) {
          try {
            let attestation = await fxwebauthn.authenticateCredential(
              challenge.challenge,
              credentials[attestations.length],
            );
            attestations.push({
              attestation: attestation,
              memqueueId: challenge.memqueueId,
            });
            this.challengesAnswered++;
          } catch (error) {
            this.$bus.emit("toaster", {
              message: `Failed to authenticate credential: ${error.message}`,
            });
            this.amountOfChallenges = null;
            this.challengesAnswered = null;
            throw error;
          }
        }
        this.amountOfChallenges = null;
        this.challengesAnswered = null;
      }
      let u2fLoginBody = {
        authType: "u2f",
        authCredentials: {
          username: this.username,
          data: attestations,
        },
      };

      if (u2fLogin) {
        return this.$httpV2.post(loginUrl, u2fLoginBody, {
          errorContextMessage: "Failed U2F login ",
        });
      } else {
        return loginData;
      }
    },

    authenticateUser: async function () {
      try {
        this.authButtonDisabled = true;

        this.validateInput();

        await this.initializeSession();

        let loginData;
        loginData = await this.userPassLogin();
        loginData = await this.u2fLogin(loginData);

        this.$store.commit("byok/login", {
          response: loginData,
          cluster: this.currentCluster,
        });

        if (loginData.loginComplete) {
          this.$bus.emit("toaster", {
            message: "Login complete",
            type: "success",
          });
          this.$router.push({ name: "actions" });
        } else {
          this.$bus.emit("toaster", { message: "Success", type: "success" });
          this.username = null;
          this.password = null;
        }
      } catch (error) {
        this.password = null;
      } finally {
        this.authButtonDisabled = false;
        this.$nextTick(() => {
          if (this.$refs.usernameInput) {
            this.$refs.usernameInput.focus();
          }
        });
      }
    },
  },
};
</script>

<style scoped>
#base {
  border: 1px solid var(--border-color);
  border-radius: 3px;
  box-shadow: 0px 1px 1px 0px var(--border-color);
  width: calc(100% - 100px);
  margin: 50px;
}

.login-header {
  padding: 10px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: rgb(241, 241, 241);
  border-bottom: 1px solid var(--border-color);
  border-top-right-radius: 3px;
  border-top-left-radius: 3px;
}

#name {
  color: #3c8dbc;
  margin: 0px;
  height: full;
}

.fx-logo-small {
  height: 24px;
}

#body {
  padding: 15px;
  width: 100%;
}

#form {
  padding: 10px 20px 20px 20px;
  width: 100%;
}

#descriptor-wrap {
  font-size: 13px;
  margin-bottom: 10px;
  width: 100%;
}

#descriptor {
  display: inline-flex;
  margin: 0px;
}

#ispan {
  border: 1px dotted var(--border-color);
  width: 10px;
}

#interactive {
  background: linear-gradient(
    180deg,
    rgba(249, 249, 249, 1) 0%,
    rgba(241, 241, 241, 1) 35%,
    rgba(238, 238, 238, 1) 100%
  );
  width: 100%;
  height: 69px;
  border: 1px solid var(--border-color);
  border-radius: 3px;
}

#submit-wrap {
  float: right;
  margin: 0px;
  width: 100px;
  height: 100%;
  vertical-align: top;
}

#submit {
  width: 100%;
  height: 100%;
  border: none;
  background: linear-gradient(
    180deg,
    rgba(249, 249, 249, 1) 0%,
    rgba(241, 241, 241, 1) 35%,
    rgba(230, 230, 230, 1) 100%
  );
  padding: 0px;
  color: var(--text-color-blue-lighter);
}

#submit:active,
#submit:disabled,
#submit[disabled] {
  background: linear-gradient(
    180deg,
    rgba(237, 237, 237, 1) 0%,
    rgba(229, 229, 229, 1) 35%,
    rgba(226, 226, 226, 1) 100%
  );
  color: var(--text-color-blue-lighter);
}

#inputs {
  width: calc(100% - 100px);
  height: 67px;
  margin-right: -4px;
}

#top-input {
  display: block;
  padding: 6px 12px;
  border: 0px;
  border-bottom: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
  border-top-left-radius: 3px;
  width: 100%;
  font-size: 14px;
  color: inherit;
}

#bottom-input {
  display: block;
  padding: 6px 12px;
  border: 0px;
  border-right: 1px solid var(--border-color);
  border-bottom-left-radius: 3px;
  width: 100%;
  font-size: 14px;
  color: inherit;
}
</style>

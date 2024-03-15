<template>
  <modal-base @esc="$emit('closeModal')">
    <template #header>
      <p>U2F Management</p>
      <button @click="$emit('closeModal')">
        <i class="fa fa-times" />
      </button>
    </template>
    <template #main>
      <div v-if="challengesAnswered !== null && amountOfChallenges !== null">
        <p>
          {{ challengesAnswered }} / {{ amountOfChallenges }} challenges
          answered.
        </p>
        <p>
          Insert your security key and if it has a button, press the button.
        </p>
      </div>

      <ul class="wizard-page-list">
        <li>
          <label for="u2f-management-credential-name">Credential name</label>
          <input
            id="u2f-management-credential-name"
            v-model="credentialName"
            class="input"
            maxlength="32"
            @keydown.enter="$refs.registerButton.click()"
          />
          <button
            ref="registerButton"
            :disabled="credentialNameInvalid"
            class="button blue-button"
            @click="handleRegister"
          >
            Register
          </button>
        </li>
      </ul>

      <ul
        v-if="u2fCredentials && u2fCredentials.length > 0"
        class="wizard-page-list credentials-list"
      >
        <li v-for="credential in u2fCredentials" :key="credential">
          <span>{{ credential }}</span>
          <button class="button" @click="deleteU2fCredential(credential)">
            <i class="fa fa-times" />
          </button>
        </li>
      </ul>
    </template>
    <template #footer>
      <button class="button icon-text-button" @click="$emit('closeModal')">
        <i class="fa fa-times" />
        Close
      </button>
    </template>
  </modal-base>
</template>

<script>
import fxwebauthn from "@/fxwebauthn";
import ModalBase from "@/components/ModalBase.vue";

export default {
  components: {
    "modal-base": ModalBase,
  },
  inject: ["getSessionId", "isGpMode"],
  props: {
    username: {
      type: String,
      required: true,
    },
  },
  data: function () {
    return {
      u2fCredentials: null,
      credentialName: "",
      amountOfChallenges: null,
      challengesAnswered: null,
    };
  },
  computed: {
    credentialNameInvalid: function () {
      return !/^[a-zA-Z0-9]{1,32}$/.test(this.credentialName);
    },
  },
  mounted: function () {
    this.initializeU2fCredentials();
  },
  methods: {
    initializeU2fCredentials: function () {
      let url = `/clusters/sessions/${this.getSessionId()}/identities/${
        this.username
      }`;
      this.$httpV2
        .get(url, { errorContextMessage: `Failed to fetch identities` })
        .then((data) => {
          this.u2fCredentials = data.u2fCredentials;
        });
    },

    handleRegister: async function () {
      let url = `/clusters/sessions/${this.getSessionId()}/identities/${
        this.username
      }/u2f/${this.credentialName}`;
      let data = await this.$httpV2.post(
        url,
        {},
        { errorContextMessage: "Failed to fetch U2F challenges" },
      );
      let challenges = data.data;
      let userId = data.userId;

      this.amountOfChallenges = challenges.length;
      this.challengesAnswered = 0;

      let attestations = [];
      for (let challenge of challenges) {
        try {
          let attestation = await fxwebauthn.registerNewCredential(
            this.username,
            challenge.challenge,
            userId,
          );
          attestations.push({
            attestation: attestation,
            memqueueId: challenge.memqueueId,
          });
          this.challengesAnswered++;
        } catch (error) {
          this.$bus.emit("toaster", {
            message: `Failed to register new credential: ${error.message}`,
          });
          this.amountOfChallenges = null;
          this.challengesAnswered = null;
          throw error;
        }
      }
      this.amountOfChallenges = null;
      this.challengesAnswered = null;

      let body = { data: attestations };
      await this.$httpV2.post(url, body, {
        errorContextMessage: "Failed to respond to U2F challenges",
      });

      this.$bus.emit("toaster", {
        message: "Successfully registered new credential",
        type: "success",
      });
      this.initializeU2fCredentials();
      this.credentialName = "";
    },

    deleteU2fCredential: function (credential) {
      let url = `/clusters/sessions/${this.getSessionId()}/identities/${
        this.username
      }/u2f/${credential}`;
      this.$httpV2
        .delete(url, { errorContextMessage: "Failed to delete credential" })
        .then(() => {
          this.$bus.emit("toaster", {
            message: "Successfully deleted credential",
            type: "success",
          });
        })
        .finally(() => {
          this.initializeU2fCredentials();
        });
    },
  },
};
</script>

<style scoped>
.credentials-list {
  margin-top: 1rem;
}
</style>

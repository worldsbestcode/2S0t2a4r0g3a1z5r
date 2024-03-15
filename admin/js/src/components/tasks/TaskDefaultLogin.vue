<template>
  <div class="cover-screen" style="top: 0; padding-top: 2rem">
    <WizardPage
      title="Default Login"
      :loading="loading"
      @finish="setDefaultLogin"
    >
      <ChcInput v-model="state.managerRoleName" label="Management role name" />

      <ChcLabel
        v-for="(newLogin, index) in state.newLogins"
        :key="newLogin"
        div
        :label="`Login #${index + 1}`"
      >
        <ChcLabel div class="modal-stuff-container">
          <form>
            <ChcInput v-model="newLogin.username" label="Username" />
            <ChcInput
              v-model="newLogin.password"
              label="Password"
              type="password"
            />
          </form>
        </ChcLabel>
      </ChcLabel>
    </WizardPage>
    <WizardPageFooter>
      <ChcButton secondary @click="logOut">Log out</ChcButton>
      <ChcButton @click="setDefaultLogin">Complete</ChcButton>
    </WizardPageFooter>
  </div>
</template>

<script setup>
import axios from "axios";
import { reactive, ref } from "vue";
import { useStore } from "vuex";

import { sendToLogin } from "$shared";
import ChcButton from "$shared/components/ChcButton.vue";
import ChcInput from "$shared/components/ChcInput.vue";
import ChcLabel from "$shared/components/ChcLabel.vue";
import WizardPage from "$shared/components/wizard/WizardPage.vue";
import WizardPageFooter from "$shared/components/wizard/WizardPageFooter.vue";

const store = useStore();

const loading = ref(false);

const state = reactive({
  managerRoleName: "",
  newLogins: [
    {
      username: "",
      password: "",
    },
    {
      username: "",
      password: "",
    },
  ],
});

function logOut() {
  store.dispatch("auth/logout").finally(() => {
    sendToLogin();
  });
}

function setDefaultLogin() {
  axios
    .post(
      "/admin/v1/init",
      {
        managerRoleName: state.managerRoleName,
        newLogins: state.newLogins,
      },
      {
        loading,
        errorContext: "Failed to set default login",
      },
    )
    .then(async (response) => {
      store.commit("auth/login", response.data);

      // todo: Use the login redirect function here, move that logic out of home
      // Let login view do the redirection stuff for us
      window.location.href = "/";
    });
}
</script>

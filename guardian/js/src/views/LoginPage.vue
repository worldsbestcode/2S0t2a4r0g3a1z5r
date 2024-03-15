<template>
  <br />
  <div class="content rounded">
    <div class="text-center">
      <img src="@/assets/logo.png" />
    </div>

    <div>
      <LoginForm />
    </div>
  </div>
</template>

<script>
import store from "@/store";
import LoginForm from "@/components/LoginForm.vue";
import { getHashParams } from "@/utils/web";

export default {
  name: "LoginPage",
  components: {
    LoginForm,
  },
  // Initialize state from server
  setup() {
    var hash = getHashParams();
    // If there is a JWT, attempt JWT login
    if (hash["jwt"] !== undefined) {
      var jwt = hash["jwt"];
      store.dispatch("auth/tokenLogin", jwt);
    }
  },
};
</script>

<style scoped>
.content {
  width: 800px;
  margin: auto;
  border: 1px solid black;
}
</style>

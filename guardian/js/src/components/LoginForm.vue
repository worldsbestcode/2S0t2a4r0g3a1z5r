<template>
  <div id="content-login" class="fade show active">
    <div class="text-center mb-3 padded-div">
      <br />
      <form>
        <!-- Login status -->
        <div class="text-box info-box">
          {{ loginStatus }}
        </div>

        <br />

        <!-- Username input -->
        <div class="form-outline mb-4">
          <input
            id="username"
            ref="usernameRef"
            v-model="username"
            type="text"
            class="form-control"
            placeholder="Username"
          />
        </div>

        <!-- Password input -->
        <div class="form-outline mb-4">
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-control"
            placeholder="Password"
          />
        </div>

        <!-- Submit button -->
        <button
          type="submit"
          class="btn btn-primary btn-block mb-4"
          @click="login()"
        >
          Sign in
        </button>

        <!-- Error message on failed login -->
        <div
          v-if="error !== null && error !== undefined"
          class="text-box error-box"
        >
          {{ error }}
        </div>

        <!-- Success message on good login -->
        <div
          v-if="msg !== null && msg !== undefined"
          class="text-box success-box"
        >
          {{ msg }}
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from "vue";
import { unwrapErr } from "@/utils/web";
import store from "@/store";
import axios from "axios";

export default {
  name: "LoginForm",

  // SETUP
  setup() {
    // Input fields
    const error = ref(null);
    const msg = ref(null);
    const username = ref("");
    const password = ref("");

    return {
      msg,
      error,
      username,
      password,
    };
  },

  // COMPUTED
  computed: {
    // Create login status text
    loginStatus: function () {
      var ret = "Please login";
      var users = store.state.auth.users;
      var roles = store.state.auth.roles;
      if (users.length > 0) {
        ret = "Logged in users: ";
        for (let i = 0; i < users.length; i++) {
          if (i > 0) ret += ", ";
          ret += users[i].name;
        }

        if (roles.length > 0) {
          ret += "\nLogged in roles: ";
          for (let i = 0; i < roles.length; i++) {
            if (i > 0) ret += ", ";
            ret += roles[i].name;
          }
        }

        if (store.state.auth.fully_logged_in) ret += "\nFully authorized";
      }

      return ret;
    },
  },

  // ON MOUNT
  mounted() {
    this.focusInput();
  },

  // METHODS
  methods: {
    // Submit login
    login: async function () {
      const form = this;
      this.error = null;
      this.msg = null;

      try {
        // Ask server to login
        await axios
          .post("/v1/login", {
            authType: "userpass",
            authCredentials: {
              username: this.username,
              password: btoa(this.password),
            },
            // Update vuex login state
          })
          .then(function (res) {
            store.dispatch("auth/reload");
            form.loginSuccess(res);
          });
        // Failed login
      } catch (err) {
        this.error = unwrapErr(err);
        this.msg = null;
      }
    },

    // Update form on successful login
    loginSuccess: function (res) {
      this.msg = res.data.message;
      this.username = "";
      this.password = "";
      this.focusInput();
    },

    // Focus default input field
    focusInput() {
      this.$refs.usernameRef.focus();
    },
  },
};
</script>

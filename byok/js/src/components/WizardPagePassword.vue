<template>
  <ul class="wizard-page-list">
    <li>
      <span>Password</span>
      <input v-model="password" type="password" class="input input-wide" />
    </li>
  </ul>
</template>

<script>
export default {
  title: "Password",
  description: "Enter the password",
  continueButtonAtBottom: true,
  defaultData: function () {
    return {
      password: {
        value: "",
      },
    };
  },
  mounted: function () {
    this.$emit("wizardContinueButtonDisabled", false);
  },
};
</script>

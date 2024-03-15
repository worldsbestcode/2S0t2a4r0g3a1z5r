<template>
  <ul class="wizard-success-ul">
    <li>
      Checksum: <span class="checksum">{{ keyChecksum }}</span>
    </li>
    <li>Major key: {{ majorKey }}</li>
    <li>Security usage: {{ securityUsage.join(", ") || "None" }}</li>
    <li>Usage: {{ usage.join(", ") || "None" }}</li>
    <li>TR-31: {{ tr31.header }}</li>
  </ul>
</template>

<script>
export default {
  data: function () {
    return {
      keyChecksum: null,
      majorKey: null,
      securityUsage: null,
      usage: null,
      tr31: null,
    };
  },
};
</script>

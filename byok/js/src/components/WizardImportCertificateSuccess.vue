<template>
  <ul class="wizard-success-ul">
    <li>Slot: {{ slot }}</li>
    <li>
      Checksum: <span class="checksum">{{ keyChecksum }}</span>
    </li>
  </ul>
</template>

<script>
export default {
  data: function () {
    return {
      slot: null,
      keyChecksum: null,
    };
  },
};
</script>

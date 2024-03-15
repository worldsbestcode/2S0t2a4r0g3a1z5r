<template>
  <ul class="wizard-success-ul">
    <li>{{ have }} / {{ want }} components loaded.</li>
    <li>
      Part key checksums: <span class="checksum">{{ partKcv }}</span>
    </li>
    <li v-if="kcv">
      Key checksum: <span class="checksum">{{ kcv }}</span>
    </li>
  </ul>
</template>

<script>
export default {
  data: function () {
    return {
      have: null,
      partKcv: null,
      want: null,
      kcv: null,
    };
  },
};
</script>

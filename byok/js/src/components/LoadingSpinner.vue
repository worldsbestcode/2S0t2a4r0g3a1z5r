<template>
  <div :class="['spinner', { 'activate-spinner': loading }]" />
</template>

<script>
export default {
  props: {
    loading: {
      type: Boolean,
      required: true,
    },
  },
};
</script>

<style scoped>
.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid transparent;
  border-radius: 1rem;
}

.activate-spinner {
  border-top-color: #0044cc;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

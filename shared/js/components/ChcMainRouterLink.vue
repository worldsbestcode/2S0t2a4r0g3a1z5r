<template>
  <RouterLink
    active-class="chc-main-router-link-active"
    class="chc-main-link chc-main-router-link"
  >
    &nbsp;&nbsp;<slot />&nbsp;&nbsp;
  </RouterLink>
</template>

<style scoped>
.chc-main-router-link {
  text-decoration: underline;
  text-decoration-color: var(--border-color);
  text-underline-offset: 0.8rem;

  margin: 0 -0.5rem;
}

.chc-main-router-link-active {
  color: var(--primary-color);
  text-decoration-thickness: 3px;
  text-decoration-color: var(--primary-color);
}
</style>

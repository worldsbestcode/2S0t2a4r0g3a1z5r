<template>
  <div
    ref="modalDiv"
    tabindex="-1"
    class="modal-v2"
    @keydown.esc="$emit('esc')"
  >
    <div class="modal-v2-container">
      <header>
        <slot name="header"></slot>
      </header>
      <main>
        <slot name="main"></slot>
      </main>
      <footer>
        <slot name="footer"></slot>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  mounted: function () {
    this.$refs.modalDiv.focus();
  },
};
</script>

<style>
.modal-v2 {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(0, 0, 0, 0.3);
  z-index: 1;
  overflow: auto;
}

.modal-v2-container {
  width: 600px;
  margin: auto;
  margin-top: 2rem;
}

.modal-v2-container > header {
  background-color: #eee;
  border-top-right-radius: 4px;
  border-top-left-radius: 4px;
  border-bottom: 1px solid var(--border-color);
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
}

.modal-v2-container > header > p {
  margin: 0;
}

.modal-v2-container > header > button {
  width: 2rem;
  height: 2rem;
  border: 0;
  background: transparent;
  padding: 0;
  color: inherit;
}

.modal-v2-container > main {
  background-color: white;
  border-bottom: 1px solid var(--border-color);
  padding: 1rem;
}

.modal-v2-container > footer {
  background: #f5f5f5;
  padding: 1rem;
  display: flex;
  justify-content: flex-end;
}

.modal-v2-container > footer button + button {
  margin-left: 0.5rem;
}
</style>

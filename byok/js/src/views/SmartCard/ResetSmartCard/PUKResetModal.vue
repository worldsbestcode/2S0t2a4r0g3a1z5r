<template>
  <div>
    <div id="scr-puk">
      <p id="scr-label">Enter current PUK</p>
      <input
        v-model="puk"
        class="scr-input"
        placeholder="PUK"
        type="password"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: "EnterPUK",
  data: function () {
    return {
      puk: null,
    };
  },
};
</script>

<style>
#scr-puk {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 3px;
  padding: 10px 15px 10px 15px;
  margin: 0px;
}

#scr-label {
  margin: 0px;
  display: inline-block;
  width: calc(100% - 204px);
}

.scr-input {
  display: inline-block;
  width: 200px;
  padding: 6px 12px 6px 12px;
  color: var(--text-color);
  border: 1px solid #ccc;
  border-radius: 3px;
}
</style>

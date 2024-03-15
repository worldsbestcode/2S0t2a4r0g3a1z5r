<template>
  <div>
    <p id="scr-set-pin">Set new PIN.</p>
    <div id="scr-new-pin-box">
      <p id="scr-label">Enter new PIN (must be 8 characters)</p>
      <input
        v-model="newPIN"
        class="scr-input"
        placeholder="PIN"
        type="password"
      />
    </div>
    <div id="scr-confirm-pin-box">
      <p id="scr-label">Re-enter new PIN</p>
      <input
        v-model="confirmPIN"
        class="scr-input"
        placeholder="PIN"
        type="password"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: "EnterPin",
  data: function () {
    return {
      newPIN: null,
      confirmPIN: null,
    };
  },
};
</script>

<style>
#scr-set-pin {
  margin: 0px 0px 20px 0px;
}

#scr-new-pin-box {
  border-top-right-radius: 3px;
  border-top-left-radius: 3px;
}

#scr-new-pin-box,
#scr-confirm-pin-box {
  background-color: #eee;
  padding: 10px 15px 10px 15px;
  border: 1px solid #ddd;
}

#scr-confirm-pin-box {
  border-top: 0px;
  border-bottom-right-radius: 3px;
  border-bottom-left-radius: 3px;
}
</style>

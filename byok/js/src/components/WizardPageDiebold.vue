<template>
  <div>
    <input
      ref="fileInput"
      class="hidden"
      type="file"
      @change="handleFileSelected"
    />

    <table class="diebold-table">
      <tr>
        <th />
        <th v-for="n in 16" :key="n">
          {{ n }}
        </th>
      </tr>
      <tr v-for="n in 16" :key="n">
        <th>{{ n }}</th>
        <td v-for="m in 16" :key="m">
          <input
            type="password"
            maxlength="2"
            :value="dieboldTable[_2d21d(n, m)]"
            :data-index="_2d21d(n, m)"
            @input="handleInput"
            @keydown="handleKeydown"
            @focus="$event.target.type = 'text'"
            @focusout="$event.target.type = 'password'"
          />
        </td>
      </tr>
    </table>

    <nav class="diebold-buttons">
      <button class="button" @click="handleLoadFileClick">Load</button>
      <button class="button" @click="handleRandomizeClick">Randomize</button>
      <button class="button" @click="dieboldTable = emptyDieboldTable()">
        Clear
      </button>
      <button
        :disabled="wizardContinueButtonDisabled"
        class="button"
        @click="handleExportClick"
      >
        Export
      </button>
    </nav>
  </div>
</template>

<script>
import { download, isHex } from "@/utils/misc.js";

function _2d21d(n, m) {
  return (n - 1) * 16 + (m - 1);
}

function emptyDieboldTable() {
  return Array(256).fill("");
}

function stringToArrayOfTwoCharacters(string) {
  return string.match(/.{2}/g);
}

export default {
  title: "Load Diebold",
  continueButtonAtBottom: true,
  defaultData: function () {
    return {
      dieboldTable: {
        value: emptyDieboldTable(),
      },
    };
  },
  computed: {
    wizardContinueButtonDisabled: function () {
      return this.dieboldTable.join("").length !== 512;
    },
  },
  watch: {
    wizardContinueButtonDisabled: function (newValue) {
      this.$emit("wizardContinueButtonDisabled", newValue);
    },
  },
  mounted: function () {
    this.$emit(
      "wizardContinueButtonDisabled",
      this.wizardContinueButtonDisabled,
    );
    let firstInput = document.querySelector('input[data-index="0"');
    if (firstInput) {
      firstInput.focus();
    }
  },
  methods: {
    _2d21d: _2d21d,
    emptyDieboldTable: emptyDieboldTable,
    handleLoadFileClick: function () {
      this.$refs.fileInput.click();
    },
    handleFileSelected: async function (event) {
      let file = event.target.files[0];
      let text = (await file.text()).trim();

      let newArray = stringToArrayOfTwoCharacters(text);
      if (!isHex(text) || newArray === null || newArray.length !== 256) {
        this.$bus.emit("toaster", {
          message: `Failed to load diebold: invalid data`,
          type: "error",
        });
      } else {
        this.dieboldTable = newArray;
      }
    },
    handleExportClick: function () {
      download(this.dieboldTable, "diebold");
    },
    handleRandomizeClick: function () {
      this.$httpV2
        .post(
          "/keyblock/diebold/random",
          {},
          { errorContextMessage: "Failed to randomize diebold" },
        )
        .then((data) => {
          this.dieboldTable = stringToArrayOfTwoCharacters(data.table);
        });
    },
    handleKeydown: function (event) {
      let target = event.target;
      if (target.value === "" && event.key === "Backspace") {
        let previousTd = target.parentElement.previousElementSibling;
        if (previousTd === null || previousTd.tagName === "TH") {
          let previousTr =
            target.parentElement.parentElement.previousElementSibling;
          if (previousTr === null) {
            return;
          }
          previousTd = previousTr.querySelector("td:last-child");
          if (previousTd === null) {
            return;
          }
        }
        let previousTdInput = previousTd.querySelector("input");
        if (previousTdInput) {
          previousTdInput.focus();
          previousTdInput.select();
        }
        event.preventDefault();
      }
    },
    handleInput: function (event) {
      let target = event.target;
      let value = target.value;
      let lastCharacter = value.charAt(value.length - 1);
      if (isHex(lastCharacter) || lastCharacter === "") {
        target.value = value.toUpperCase();
        let index = target.dataset.index;
        this.dieboldTable[index] = target.value;
      } else {
        target.value = value.slice(0, -1);
      }

      if (target.value.length === 2) {
        let nextTd = target.parentElement.nextElementSibling;
        if (nextTd === null) {
          let nextTr = target.parentElement.parentElement.nextElementSibling;
          if (nextTr === null) {
            return;
          }
          nextTd = nextTr.querySelector("td");
        }
        let nextTdInput = nextTd.querySelector("input");
        if (nextTdInput) {
          nextTdInput.focus();
          nextTdInput.select();
        }
      }
    },
  },
};
</script>

<style scoped>
.diebold-table {
  --box-size: 24px;
  margin: auto;
}

.diebold-table th {
  background: linear-gradient(
    180deg,
    rgba(249, 249, 249, 1) 0%,
    rgba(241, 241, 241, 1) 35%,
    rgba(238, 238, 238, 1) 100%
  );
  border: 1px solid var(--border-color);
  height: var(--box-size);
  width: var(--box-size);
  padding: 0;
  border-collapse: collapse;
  text-align: center;
  font-weight: 400;
}

.diebold-table td {
  border: 1px solid var(--border-color);
  padding: 0;
}

.diebold-table input {
  height: var(--box-size);
  width: var(--box-size);
  font-family: monospace;
  text-align: center;
  border: 0;
  padding: 0;
}

.diebold-buttons {
  display: flex;
  width: max-content;
  margin: auto;
  margin-top: 1rem;
}

.diebold-buttons button + button {
  margin-left: 0.5rem;
}
</style>

<template>
  <div>
    <p v-if="!majorKeyLoad">
      {{ components.length }} / {{ _numberOfComponents }} loaded
    </p>

    <div v-if="majorKeyLoad || components" class="components-container">
      <div
        v-for="i in componentTypeLines[_componentType] * 4"
        :key="i"
        class="components-wrapper"
      >
        <input
          v-for="j in 4"
          :key="j"
          class="input component-input"
          type="password"
          :data-index="_2d21d(i, j)"
          maxlength="1"
          :value="component[_2d21d(i, j)]"
          @focus="$event.target.type = 'text'"
          @focusout="$event.target.type = 'password'"
          @input="handleInput"
          @keydown="handleKeydown"
        />
      </div>
    </div>

    <footer class="wrap-component-footer">
      <button
        :disabled="component.length === 0"
        class="button"
        @click="component = []"
      >
        Clear
      </button>
      <button
        :disabled="wrapComponentButtonDisabled"
        class="button blue-button"
        @click="wrapClearComponent"
      >
        Wrap component
      </button>
    </footer>
  </div>
</template>

<script>
import { isHex } from "@/utils/misc.js";

let componentTypeLines = {
  DES: 1,
  "2TDES": 2,
  "3TDES": 3,
  "AES-128": 2,
  "AES-192": 3,
  "AES-256": 4,
};

function _2d21d(n, m) {
  return (n - 1) * 4 + (m - 1);
}

export default {
  title: "Load Component",
  defaultData: function () {
    return {
      component: {
        value: [],
      },
      components: {
        value: [],
      },
      wrappedComponent: {
        value: null,
      },
      wrappedComponents: {
        value: null,
      },
    };
  },
  inject: ["getSessionId", "isGpMode"],
  props: {
    majorKey: {
      type: Function,
      default: () => {},
    },
    majorKeyLoad: {
      type: Boolean,
      default: false,
    },
    componentType: {
      type: [String, Function],
      required: true,
    },
    numberOfComponents: {
      type: Function,
      required: false,
    },
  },
  data: function () {
    return {
      componentTypeLines,
    };
  },
  computed: {
    _componentType: function () {
      return typeof this.componentType === "function"
        ? this.componentType()
        : this.componentType;
    },
    _numberOfComponents: function () {
      return this.numberOfComponents();
    },
    wrapComponentButtonDisabled: function () {
      let componentTypeToComponentLength = {
        DES: 1 * 16,
        "2TDES": 2 * 16,
        "3TDES": 3 * 16,
        "AES-128": 2 * 16,
        "AES-192": 3 * 16,
        "AES-256": 4 * 16,
      };
      return !(
        componentTypeToComponentLength[this._componentType] ===
        this.component.join("").length
      );
    },
  },
  mounted: function () {
    this.component = [];
    this.$nextTick(() => {
      let firstInput = document.querySelector('input[data-index="0"]');
      if (firstInput) {
        firstInput.focus();
      }
    });
  },
  methods: {
    _2d21d,

    handleInput: function (event) {
      let target = event.target;
      let value = target.value;
      let lastCharacter = value.charAt(value.length - 1);
      if (isHex(lastCharacter) || lastCharacter === "") {
        target.value = value.toUpperCase();
        let index = target.dataset.index;
        this.component[index] = target.value;
      } else {
        target.value = value.slice(0, -1);
      }

      if (target.value.length === 1) {
        let next = target.nextElementSibling;
        if (next === null) {
          let nextDiv = target.parentElement.nextElementSibling;
          if (nextDiv === null) {
            return;
          }
          next = nextDiv.querySelector("input");
        }
        if (next) {
          next.focus();
          next.select();
        }
      }
    },

    handleKeydown: function (event) {
      let target = event.target;
      if (target.value === "" && event.key === "Backspace") {
        let previous = target.previousElementSibling;
        if (previous === null) {
          let previousDiv = target.parentElement.previousElementSibling;
          if (previousDiv === null) {
            return;
          }
          previous = previousDiv.querySelector("input:last-child");
          if (previous === null) {
            return;
          }
        }
        if (previous) {
          previous.focus();
          previous.select();
        }
        event.preventDefault();
      }
    },

    getPublicKey: async function () {
      let publicKeyResponse = await window.fxctx.keys.getEphemeralPublicKey();
      if (publicKeyResponse.success) {
        return publicKeyResponse.value;
      } else {
        let loginMessage = `Missing ephemeral ECC key: Key component loading step 'ephemeral ECC key generation' requires a local login.`;
        let message = "Failed to get ephemeral public key: ";
        if (publicKeyResponse.msg === loginMessage) {
          message += "Local login required";
        } else {
          message += publicKeyResponse.msg;
        }
        this.$bus.emit("toaster", { message: message, type: "error" });
        return publicKeyResponse.value;
      }
    },

    getClearKeySessions: async function (publicKey) {
      let url = `/clusters/sessions/${this.getSessionId()}/keyload/clearkey-sessions`;
      let body = {
        clearPublicKeyBlock: publicKey,
        majorKeyLoad: this.majorKeyLoad,
      };
      let data = await this.$httpV2.post(url, body, {
        errorContextMessage: "Failed to create key loading session",
      });
      let sessions = data.sessions;
      return sessions;
    },

    wrapClearComponent: async function () {
      let publicKey = await this.getPublicKey();
      if (!publicKey) {
        return;
      }

      let component = this.component.join("");

      if (!this.majorKeyLoad) {
        this.components.push(component);
        this.component = [];
        if (this.components.length !== this._numberOfComponents) {
          return;
        }
      }

      let sessions = await this.getClearKeySessions(publicKey);
      if (!sessions) {
        return;
      }

      let componentTypesInt = {
        DES: 1,
        "2TDES": 2,
        "3TDES": 3,
        "AES-128": 4,
        "AES-192": 5,
        "AES-256": 6,
      };
      let componentTypeInt = componentTypesInt[this._componentType];

      let results = [];
      for (let session of sessions) {
        await window.fxctx.keys.setEphemeralKey(session.ephemeralKey);

        if (this.majorKeyLoad) {
          let wrapResponse = await window.fxctx.keys.encryptComponent(
            component,
            componentTypeInt,
          );
          if (!wrapResponse.success) {
            let message = `Failed to wrap component: ${wrapResponse.msg}`;
            this.$bus.emit("toaster", { message: message, type: "error" });
            return;
          }

          results.push({
            memqueueId: session.memqueueId,
            component: wrapResponse.value,
          });
        } else {
          for (let component of this.components) {
            let wrapResponse = await window.fxctx.keys.encryptComponent(
              component,
              componentTypeInt,
            );
            if (!wrapResponse.success) {
              let message = `Failed to wrap component: ${wrapResponse.msg}`;
              this.$bus.emit("toaster", { message: message, type: "error" });
              return;
            }

            results.push({
              memqueueId: session.memqueueId,
              component: wrapResponse.value,
            });
          }
        }
      }

      if (this.majorKeyLoad) {
        this.wrappedComponent = results;
      } else {
        this.wrappedComponents = results;
      }

      this.nextPage();
    },
  },
};
</script>

<style scoped>
.components-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  width: fit-content;
  column-gap: 1.5rem;
  row-gap: 0.75rem;
  margin: auto;
}

.components-wrapper {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.25rem;
}

.component-input {
  width: 1.6rem;
  height: 2.5rem;
  padding: 0;
  text-align: center;
  font-family: monospace;
}

.wrap-component-footer {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
}

.wrap-component-footer button + button {
  margin-left: 0.5rem;
}
</style>

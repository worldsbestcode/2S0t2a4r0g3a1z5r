<template>
  <div class="access-search-container">
    <div class="access-search-input-container">
      <input
        ref="inputRef"
        v-model="state.search"
        class="chc-input"
        :placeholder="props.placeholder"
        style="position: relative; z-index: 1"
        @focus="showResults"
        @keyup.enter="enter"
      />
      <img
        class="access-search-icon"
        src="/shared/static/search-icon.svg"
        style="z-index: 2"
      />
    </div>
    <div v-if="state.showResults" class="access-search-results">
      <div
        v-if="searchResults.length === 0"
        class="access-search-results__empty"
        @mousedown.prevent
      >
        {{ props.noSearchResults }}
      </div>
      <template v-else>
        <!-- @mousedown.prevent is to stop focusout from firing when clicking a search result -->
        <div
          v-for="result in searchResults"
          :key="props.getObjectUuid(result.item)"
          class="access-search-results__result"
          @mousedown="mousedown($event, result.item)"
        >
          <div class="access-search-results__name">
            {{ props.getObjectName(result.item) }}
          </div>
          <img
            class="access-search-results__add-circle"
            src="/shared/static/add-circle.svg"
          />
          <img
            class="access-search-results__add-circle-inactive"
            src="/shared/static/add-circle-inactive.svg"
          />
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import Fuse from "fuse.js";
import {
  computed,
  defineEmits,
  defineProps,
  inject,
  reactive,
  ref,
  watch,
  watchEffect,
} from "vue";
import { useToast } from "vue-toastification";

import {
  decodeUuidFromBarcode,
  ENCODED_UUID_LENGTH,
} from "$shared/utils/barcode.js";

// props
const props = defineProps({
  objectName: {
    required: true,
  },
  objectUuid: {
    required: true,
  },
  data: {
    type: Array,
    required: true,
  },
  getObjectUuid: {
    type: Function,
    required: true,
  },
  getObjectName: {
    type: Function,
    required: true,
  },
  placeholder: {
    type: String,
    required: true,
  },
  maxShownResults: {
    type: Number,
    required: false,
    default: 10,
  },
  noSearchResults: {
    type: String,
    default: "No results found",
  },
  focus: {
    type: String,
    required: true,
  },
});

const emit = defineEmits([
  "update:objectName",
  "update:objectUuid",
  "objectSelected",
]);

// variables
const toast = useToast();
const inputRef = ref(null);

const fuseOptions = {
  includeMatches: true,
  ignoreLocation: true,
  shouldSort: true,
  threshold: 0.4,
  distance: 5,
  keys: ["objInfo.name", "name"],
};
const fuse = new Fuse([], fuseOptions);

const state = reactive({
  search: "",
  showResults,
});

watch(state, () => {
  fuse.setCollection(props.data);
});

const registerFocus = inject(props.focus);
registerFocus(() => {
  inputRef.value.focus();
  showResults();
});

// computed
const objectName = computed({
  get() {
    return props.objectName;
  },
  set(value) {
    emit("update:objectName", value);
  },
});

const objectUuid = computed({
  get() {
    return props.objectUuid;
  },
  set(value) {
    emit("update:objectUuid", value);
  },
});

const searchResults = computed(() => {
  let results = [];

  if (state.search.length > 0) {
    results = fuse.search(state.search);
  } else {
    results = [...props.data.map((x) => ({ item: x }))];
  }
  return results;
});

// functions
function showResults() {
  state.showResults = !state.showResults;

  if (state.showResults) {
    setTimeout(() => {
      document.addEventListener(
        "focusout",
        () => {
          if (state.showResults) {
            state.showResults = false;
          }
        },
        { once: true },
      );
    });
  }
}

function isNumber(s) {
  return /^[-+]?[0-9]*\.?[0-9]+$/.test(s);
}

function enter() {
  // check if we actually have a uuid encoded as a number
  if (state.search.length == ENCODED_UUID_LENGTH && isNumber(state.search)) {
    let uuid = decodeUuidFromBarcode(state.search);
    let name = getObjectNameByUuid(uuid);

    if (name === null) {
      toast.error("Could not find ped injection service with uuid: " + uuid);
    } else {
      objectUuid.value = uuid;
      objectName.value = name;
      emit("objectSelected");
    }
    state.search = "";
  }
}

function getObjectNameByUuid(uuid) {
  let name = null;
  props.data.forEach((object) => {
    if (props.getObjectUuid(object) === uuid) {
      name = props.getObjectName(object);
    }
  });

  return name;
}

function mousedown(event, object) {
  objectUuid.value = props.getObjectUuid(object);
  objectName.value = props.getObjectName(object);
  emit("objectSelected");
  state.search = "";
  event.preventDefault();
}

watchEffect(() => {
  fuse.setCollection(props.data);
});
</script>

<style scoped>
.access-search-container {
  width: fit-content;
}
.access-search-input-container {
  position: relative;
}

.access-search-icon {
  position: absolute;
  right: 24px;
  top: 50%;
  transform: translateY(-50%);
}

.access-search-results {
  z-index: 1;
  margin-top: -10px;
  margin-left: 1px;
  padding-top: 10px;
  border: 1px solid var(--border-color);
  border-radius: 15px;
  background: var(--secondary-background-color);
  width: 478px;
  /* shows 6 search results... */
  max-height: 145px;
  overflow-y: auto;
}

.access-search-results__name {
  width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: left;
}

.access-search-results__empty {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.access-search-results__result {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 1rem;
  cursor: pointer;
}

.access-search-results__result + .access-search-results__result {
  border-top: 1px solid var(--border-color);
}

.access-search-results__add-circle {
  display: none;
}

.access-search-results__result:hover .access-search-results__name {
  font-weight: 700;
}

.access-search-results__result:hover .access-search-results__add-circle {
  display: initial;
}

.access-search-results__result:hover
  .access-search-results__add-circle-inactive {
  display: none;
}
</style>

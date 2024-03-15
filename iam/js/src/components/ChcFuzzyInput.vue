<template>
  <div class="chc-label">
    <span class="chc-label__text">
      {{ props.label
      }}<span v-if="props.hint" class="chc-label__hint">
        {{ props.hint }}
      </span>
    </span>

    <div class="access-search-container">
      <div class="access-search-input-container">
        <input
          v-model="state.search"
          class="chc-input"
          :placeholder="props.placeholder"
          style="position: relative; z-index: 1"
          @focus="showResults"
        />
        <img
          class="access-search-icon"
          src="/shared/static/search-icon.svg"
          style="z-index: 1"
        />
      </div>
      <div
        v-if="state.showResults"
        v-show="!(props.single && searchResults.length === 0)"
        class="access-search-results"
      >
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
            :key="result.item.uuid"
            class="access-search-results__result"
            @mousedown="mousedown($event, result)"
          >
            <div class="access-search-results__name">
              {{ props.display(result.item) }}
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
      <div v-if="props.example" class="access-search-example">
        eg. {{ props.example }}
      </div>
    </div>
  </div>
</template>

<script setup>
import Fuse from "fuse.js";
import { computed, defineEmits, defineProps, reactive, watchEffect } from "vue";

const emit = defineEmits(["update:selected"]);

const props = defineProps({
  single: {
    type: Boolean,
    default: false,
  },
  keys: {
    type: Array,
    required: true,
  },
  display: {
    type: Function,
    required: true,
  },
  data: {
    type: Array,
    required: true,
  },
  selected: {
    type: undefined,
    default: undefined,
  },
  placeholder: {
    type: String,
    required: true,
  },
  noSearchResults: {
    type: String,
    required: true,
  },
  example: {
    type: String,
    default: undefined,
  },
  label: {
    type: String,
    default: undefined,
  },
  hint: {
    type: String,
    default: undefined,
  },
});

const fuseOptions = {
  includeMatches: true,
  ignoreLocation: true,
  threshold: 0.4,
  keys: props.keys,
};

const fuse = new Fuse([], fuseOptions);

const state = reactive({
  search: "",
  showResults: false,
});

const selected = computed({
  get() {
    return props.selected;
  },
  set(value) {
    emit("update:selected", value);
  },
});

const searchResults = computed(() => {
  let results;
  if (!state.search) {
    results = [...props.data.map((x) => ({ item: x }))];
  } else {
    results = fuse.search(state.search);
  }

  if (props.single) {
    return results;
  } else {
    return results.filter((x) => !selected.value.includes(x.item));
  }
});

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

function mousedown(event, result) {
  if (props.single) {
    selected.value = result.item;
    state.search = result.item;
  } else {
    event.preventDefault(); // prevents click from closing results
    selected.value.push(result.item);
  }
}

watchEffect(() => {
  fuse.setCollection(props.data);
});

if (props.single) {
  state.search = selected.value;
}
watchEffect(() => {
  if (props.single) {
    selected.value = state.search;
  }
});
</script>

<style scoped>
.access-search-container {
  width: 100%;
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

.access-search-example {
  text-align: left;
  margin-left: 21px;
  color: var(--muted-text-color);
  font-size: 14px;
  margin-top: 12px;
  position: absolute;
  z-index: -1;
}

.access-search-results {
  margin-top: -10px;
  margin-left: 1px;
  padding-top: 10px;
  border: 1px solid var(--border-color);
  border-radius: 15px;
  background: var(--secondary-background-color);
  /* shows 6 search results... */
  max-height: 311px;
  overflow-y: auto;
  position: relative;
  width: 100%;
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

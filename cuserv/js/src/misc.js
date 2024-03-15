import { computed } from "vue";

export function computedVModel({ name, emit, props }) {
  return computed({
    get() {
      return props[name];
    },
    set(value) {
      emit(`update:${name}`, value);
    },
  });
}

export function timestampToDate(timestamp) {
  if (timestamp) {
    return new Date(parseInt(timestamp) * 1000).toLocaleString([], {});
  }
}

export function stubsSynchronize(response, state, resultsKey = "results") {
  const results = response.data[resultsKey];

  state.totalPages = response.data.totalPages;
  state.results = results;
  if (results.length === 0) {
    state.page = response.data.previousPage;
  }
}

export const defineModalProps = {
  text: {
    type: Boolean,
  },
  icon: {
    type: Boolean,
  },
  action: {
    type: Boolean,
  },
};

export function useDeleteModalProps(props) {
  return computed(() => {
    const ret = {};
    if (props.icon) {
      ret.icon = "trash";
    }
    if (props.text) {
      ret.text = "Delete";
    }
    if (props.action) {
      ret.action = {
        imgSrc: "/shared/static/trash-active.svg",
        text: "DELETE",
      };
    }
    return ret;
  });
}

export const eHttpsResponse = Object.freeze({
  InvalidRequest: 500,
  Ok: 200,
});

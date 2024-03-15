export const listStyle = {
  type: String,
  required: true,
  validator(value) {
    return ["list", "tile"].includes(value);
  },
};

export const chcLabel = {
  hint: {
    type: String,
    default: undefined,
  },
  label: {
    type: String,
    default: undefined,
  },
  side: {
    type: String,
    default: undefined,
    validator(value) {
      if (value) {
        return ["left", "right"].includes(value);
      }
      return true;
    },
  },
};

import _ from "lodash";
import { markRaw } from "vue";

let wizardMixin = {
  data: function () {
    return {
      currentWizard: null,
      wizards: {},
    };
  },
  methods: {
    setWizard: function (componentName) {
      this.currentWizard = this.wizards[componentName];
    },
    handleWizardClose: function () {
      this.currentWizard = null;
    },
  },
  created: function () {
    this.$bus.on("wizardClose", this.handleWizardClose);
  },
  unmounted: function () {
    this.$bus.off("wizardClose", this.handleWizardClose);
  },
};

function wizardPageMixin(data) {
  let computed = {};
  for (let key in data) {
    computed[key] = {
      get: function () {
        return this.modelValue[key].value;
      },
      set: function (newValue) {
        this.modelValue[key].value = newValue;
      },
    };
  }

  return {
    props: {
      modelValue: {
        type: Object,
        required: true,
      },
    },
    methods: {
      nextPage: function () {
        this.$emit("wizardNextPage");
      },
    },
    computed: computed,
  };
}

function wizards(wizardsObject) {
  for (const wizardKey in wizardsObject) {
    wizardsObject[wizardKey] = markRaw(wizardsObject[wizardKey]);
  }
  return wizardsObject;
}

function wizardPage({
  name,
  title,
  description,
  component,
  data,
  props,
  pageEnabled,
}) {
  if (title === undefined) {
    title = component.title;
  }

  if (description === undefined) {
    description = component.description;
  }

  if (component.defaultData === undefined) {
    data = {};
  } else if (data === undefined) {
    data = component.defaultData();
  } else {
    data = _.merge({}, component.defaultData(), data());
  }

  let componentWithMixin = {
    ...component,
    mixins: [wizardPageMixin(data)],
  };

  return {
    name: name,
    title: title,
    description: description,
    component: markRaw(componentWithMixin),
    continueButtonAtBottom: component.continueButtonAtBottom,
    data: data,
    props: props,
    opened: false,
    pageEnabled: pageEnabled,
  };
}

function wizardData(wizardPages) {
  let data = {};
  for (let wizardPage of wizardPages) {
    if (!wizardPage.name) {
      continue;
    }

    data[wizardPage.name] = {};
    for (let [key, value] of Object.entries(wizardPage.data)) {
      data[wizardPage.name][key] = value.value;
    }
  }
  return data;
}

export { wizardMixin, wizardPage, wizardData, wizards };

import FxCheckbox from './FxCheckbox';
import FxHexInput from './FxHexInput';
import FxNumber from './FxNumber';

import {
  registerComponents,
  vueUse
} from '../../utils/plugins';

const components = {
  'fx-checkbox': FxCheckbox,
  'fx-hex-input': FxHexInput,
  'fx-number': FxNumber,
};

const VuePlugin = {
  install (Vue) {
    registerComponents(Vue, components);
  }
};

vueUse(VuePlugin);

export default VuePlugin;

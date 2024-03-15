import FxButton from './FxButton';
import FxCheckbox from './FxCheckbox';
import FxColumn from './FxColumn';
import FxContentRows from './FxContentRows';
import FxHexInput from './FxHexInput';
import FxInputMask from './FxInputMask';
import FxNumber from './FxNumber';
import FxRow from './FxRow';

import {
  registerComponents,
  vueUse
} from '../../utils/plugins';

const components = {
  'fx-button': FxButton,
  'fx-checkbox': FxCheckbox,
  'fx-column': FxColumn,
  'fx-content-rows': FxContentRows,
  'fx-hex-input': FxHexInput,
  'fx-input-mask': FxInputMask,
  'fx-number': FxNumber,
  'fx-row': FxRow,
};

const VuePlugin = {
  install (Vue) {
    registerComponents(Vue, components);
  }
};

vueUse(VuePlugin);

export default VuePlugin;

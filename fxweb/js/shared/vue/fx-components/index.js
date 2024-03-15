import * as components from './components';
// import * as directives from './directives'
import { vueUse } from './utils/plugins';

const VuePlugin = {
  install: function (Vue) {
    if (Vue._fx_components_installed) {
      return;
    }

    Vue._fx_components_installed = true;

    // Register component plugins
    for (var plugin in components) {
      Vue.use(components[plugin]);
    }

    // Register directive plugins
    /**
    for (var plugin in directives) {
      // TODO: uncomment when custom directives are added
      Vue.use(directives[plugin])
    }
    */
  }
};

vueUse(VuePlugin);

export default VuePlugin;

import FxTreeView from './FxTreeView';
import FxTreeViewItem from './FxTreeViewItem';
import FxTreeViewItemHeader from './FxTreeViewItemHeader';
import FxTreeViewNode from './FxTreeViewNode';
import FxTreeViewHeadingBar from './FxTreeViewHeadingBar';

import {
  registerComponents,
  vueUse
} from '../../utils/plugins';

const components = {
  'fx-treeview': FxTreeView,
  'fx-treeview-item': FxTreeViewItem,
  'fx-treeview-item-header': FxTreeViewItemHeader,
  'fx-treeview-node': FxTreeViewNode,
  'fx-treeview-heading-bar': FxTreeViewHeadingBar

};

const VuePlugin = {
  install (Vue) {
    registerComponents(Vue, components);
  }
};

vueUse(VuePlugin);

export default VuePlugin;

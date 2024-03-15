/**
 * @section LICENSE
 *
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, L.P. 2018
 */

class ViewAction {
  constructor (name, title, callback, component, props) {
    this.name = name;
    this.title = title;
    this.callback = callback;
    this.component = component;
    this.props = props;
  }

  isEnabled (objectData) {
    return true;
  }
}

export default ViewAction;

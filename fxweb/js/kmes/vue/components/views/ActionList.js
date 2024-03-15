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

class ActionList {
  constructor (actions = []) {
    this.actions = actions;
  }

  /**
   * Adds an action to this list.
   *
   * @param {ViewAction} action - The action to add
   */
  addAction (action) {
    this.actions.push(action);
  }

  /**
   * Retrieves an action based on the object type and action name.
   *
   * @param {string} name - The action name
   *
   * @returns A single action matching the object+name, or null if none found
   */
  getAction (name) {
    return this.actions.find(action => action.name === name);
  }

  /**
   * Retrieves the enabled actions for the given object.
   *
   * @param {ManagedObjectSchema} objectData - The object to get actions for
   *
   * @returns A ViewAction[] of enabled actions based on the given object
   */
  getEnabledActions (objectData) {
    return this.actions.filter(action => action.isEnabled(objectData));
  }

  /**
   * Get all of the available actions based on the given data.
   *
   * @param {ManagedObjectSchema} objectData - The object to get actions for
   *
   * @returns A string[] of allowed actions for the given object
   */
  getEnabledActionNames (objectData) {
    return this.getEnabledActions(objectData).map(action => action.name);
  }
}

export default ActionList;

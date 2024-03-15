import {
  adminSetupsOrder,
  cloudRestrictedTasks,
  dualControlTasks,
  hardwareTasks,
} from "$shared/admin.js";
import axios from "$shared/axios.js";

export default {
  namespaced: true,
  state: {
    notifications: [],
    hardwareMode: true,
    cloudMode: false,
  },
  getters: {
    notifications(state, getters) {
      const notifications = state.notifications;
      const tasksBlockList = getters.tasksBlockList;
      return notifications.filter(
        (x) => !tasksBlockList.includes(x.setupStepType)
      );
    },
    hasNotifications(_, getters) {
      return getters.notifications.length > 0;
    },
    tasksBlockList(state, _, rootState) {
      const dualControl = rootState.auth.users.length > 1;

      const tasksBlockList = [];
      if (!state.hardwareMode) {
        tasksBlockList.push(...hardwareTasks);
      }
      if (state.cloudMode) {
        tasksBlockList.push(...cloudRestrictedTasks);
      }
      if (!dualControl) {
        tasksBlockList.push(...dualControlTasks);
      }
      return tasksBlockList;
    },
    setupPending(state, getters) {
      const pendingTasks = state.notifications
        .filter((x) => x.notificationType === "SetupPending")
        .map((x) => x.setupStepType);
      return pendingTasks.filter((x) => !getters.tasksBlockList.includes(x));
    },
    setupCompleted(_, getters) {
      const possibleTasks = adminSetupsOrder;
      const tasksBlockList = [
        ...getters.setupPending,
        ...getters.tasksBlockList,
      ];
      return possibleTasks.filter((x) => !tasksBlockList.includes(x));
    },
  },
  mutations: {
    setNotifications(state, notifications) {
      state.notifications = notifications;
    },
    removeNotification(state, notificationUuid) {
      const notificationIndex = state.notifications.findIndex(
        (x) => x.objInfo.uuid === notificationUuid
      );
      state.notifications.splice(notificationIndex, 1);
    },
    setHardwareMode(state, value) {
      state.hardwareMode = value;
    },
    setCloudMode(state, value) {
      state.cloudMode = value;
    },
  },
  actions: {
    initialize(context) {
      axios.get("/admin/v1/appliance-mode").then((response) => {
        const { hardware, release, cloud } = response.data;
        context.commit("setHardwareMode", hardware || !release);
        context.commit("setCloudMode", cloud && release);
      });
      return axios
        .get("/admin/v1/notifications/")
        .then((response) => {
          context.commit("setNotifications", response.data.results);
        })
        .catch(() => {});
    },
    deleteNotification(context, notificationUuid) {
      return axios
        .delete(`/admin/v1/notifications/${notificationUuid}`)
        .then(() => {
          context.commit("removeNotification", notificationUuid);
        });
    },
    deleteSetupNotification(context, setupType) {
      const setupNotification = context.state.notifications.find(
        (x) => x.setupStepType === setupType
      );

      if (setupNotification) {
        return context.dispatch(
          "deleteNotification",
          setupNotification.objInfo.uuid
        );
      }
    },
  },
};

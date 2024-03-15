import axios from "$shared/axios.js";

// todo: Add toasts

const profileUrl = "/home/v1/profile/";

function postProfile(userProfile) {
  return axios.post(profileUrl, {
    user: userProfile.user,
    profile: btoa(JSON.stringify(userProfile.profile)),
  });
}

async function initializeUserProfile(userProfile) {
  try {
    const profile = JSON.parse(atob(userProfile.profile));
    // todo: Find a more "maintainable" alternative, perhaps a class?
    if (
      !Object.prototype.hasOwnProperty.call(profile, "favoriteServices") ||
      !Object.prototype.hasOwnProperty.call(profile, "recentServices")
    ) {
      throw Error(`Invalid profile for user: ${userProfile.user}`);
    }

    userProfile.profile = profile;
  } catch {
    const defaultProfile = {
      favoriteServices: [],
      recentServices: [],
    };
    userProfile.profile = defaultProfile;
    await postProfile(userProfile);
  }
}

export default {
  namespaced: true,
  state: () => ({
    initializing: true,
    profiles: [],
    activeProfile: null,
  }),
  getters: {
    userProfile(state) {
      return state.profiles.find((x) => x.user === state.activeProfile);
    },
    profile(_, getters) {
      return getters.userProfile?.profile;
    },
    favoriteServices(_, getters) {
      return getters.profile?.favoriteServices;
    },
    recentServices(_, getters) {
      return getters.profile?.recentServices;
    },
  },
  mutations: {
    setProfiles(state, profiles) {
      state.profiles = profiles;
    },
    initializeActiveProfile(state) {
      const previousActiveProfile = sessionStorage.getItem("activeProfile");
      if (previousActiveProfile) {
        state.activeProfile = previousActiveProfile;
      } else {
        const firstProfile = state.profiles[0].user;
        sessionStorage.setItem("activeProfile", firstProfile);
        state.activeProfile = firstProfile;
      }
    },

    addFavoriteService(_, { favoriteServices, serviceName }) {
      favoriteServices.unshift(serviceName);
    },
    removeFavoriteService(_, { favoriteServices, serviceNameIndex }) {
      favoriteServices.splice(serviceNameIndex, 1);
    },

    addRecentService(_, { recentServices, serviceName }) {
      recentServices.unshift(serviceName);
    },
    removeRecentService(_, { recentServices, serviceNameIndex }) {
      recentServices.splice(serviceNameIndex, 1);
    },

    switchActiveProfile(state, user) {
      sessionStorage.setItem("activeProfile", user);
      state.activeProfile = user;
    },

    initializingFinished(state) {
      state.initializing = false;
    },
  },
  actions: {
    initialize(context) {
      return axios
        .get(profileUrl)
        .then(async (response) => {
          const profiles = response.data.profiles;
          for (const userProfile of profiles) {
            await initializeUserProfile(userProfile);
          }
          context.commit("setProfiles", profiles);
          context.commit("initializeActiveProfile");
        })
        .finally(() => {
          context.commit("initializingFinished");
        });
    },

    favorite(context, serviceName) {
      const favoriteServices = context.getters.favoriteServices;
      const serviceNameIndex = favoriteServices.indexOf(serviceName);
      if (serviceNameIndex === -1) {
        context.commit("addFavoriteService", {
          favoriteServices,
          serviceName,
        });
      } else {
        context.commit("removeFavoriteService", {
          favoriteServices,
          serviceNameIndex,
        });
      }

      // todo: Give the user some feedback if we fail to save their profile...
      postProfile(context.getters.userProfile);
    },

    visit(context, serviceName) {
      const recentServices = context.getters.recentServices;
      const serviceNameIndex = recentServices.indexOf(serviceName);
      if (serviceNameIndex !== -1) {
        context.commit("removeRecentService", {
          recentServices,
          serviceNameIndex,
        });
      }
      context.commit("addRecentService", {
        recentServices,
        serviceName,
      });

      // https://stackoverflow.com/a/15724300
      function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
      }

      const csrfToken = getCookie("FXSRF-TOKEN");
      const userProfile = context.getters.userProfile;

      // todo: Give the user some feedback if we fail to save their profile...
      // how would you do that if they are navigating?
      fetch(profileUrl, {
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-FXSRF-TOKEN": csrfToken,
        },
        body: JSON.stringify({
          user: userProfile.user,
          profile: btoa(JSON.stringify(userProfile.profile)),
        }),
        method: "POST",
        keepalive: true, // lets us fire a request that finishes after page navigation
      });
    },
  },
};

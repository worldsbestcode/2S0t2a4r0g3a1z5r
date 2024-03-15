<template>
  <div>
    <div v-if="showMajorKeyError" class="major-key-error">
      <i class="fas fa-exclamation-triangle" />
      No MFK or PMK major key detected. Go to "Major Keys" to load the MFK or
      the PMK.
    </div>

    <nav class="action-links">
      <router-link
        v-for="link in links"
        :key="link.text"
        :class="{ disabled: link.disabled }"
        :to="link.disabled ? '' : link.to"
      >
        <i :class="['top', link.iconClass]" />
        <p class="bottom">{{ link.text }}</p>
      </router-link>
    </nav>
  </div>
</template>

<script>
export default {
  inject: ["canCskl", "isExcryptTouch", "getSessionId"],
  props: {
    currentCluster: Object,
  },
  data: function () {
    let link = (name) => {
      return { name: name };
    };

    let permissions = this.currentCluster.session.permissions;

    return {
      showMajorKeyError: false,
      links: [
        {
          iconClass: "fa fa-key",
          text: "Major Keys",
          disabled: !permissions["Major Keys"] || !this.canCskl(),
          to: link("majorKeys"),
        },
        {
          iconClass: "fa fa-clipboard-list",
          text: "Working Keys",
          disabled: true,
          to: link("workingKeys"),
        },
        {
          iconClass: "fa fa-award",
          text: "Certificates & Requests",
          disabled: true,
          to: link("certificatesAndRequests"),
        },
        {
          iconClass: "fa fa-layer-group",
          text: "Generate Components",
          disabled: false,
          to: link("generateComponents"),
        },
        {
          iconClass: "fa fa-sim-card",
          text: "Smart Cards",
          disabled: true,
          to: link("smartCards"),
        },
        {
          iconClass: "fa fa-user-alt",
          text: "User Management",
          disabled: !permissions["Identity"],
          to: link("userManagement"),
        },
      ],
    };
  },
  mounted: async function () {
    /* todo:
      Figure out permissions required for Certificates & Requests
      Figure out permissions required for Generate Components
    */

    let pmkOrMfkLoaded = await this.pmkOrMfkLoaded();
    this.showMajorKeyError = !pmkOrMfkLoaded;

    let permissions = this.currentCluster.session.permissions;

    let smartCardsLink = this.links.find((x) => x.text === "Smart Cards");
    smartCardsLink.disabled =
      !permissions["Smart Card"] || !(await this.isExcryptTouch());

    let workingKeysDisable = !(
      permissions["Keys"] ||
      (permissions["Excrypt"] && permissions["Excrypt"]["Excrypt:GPKI"])
    );
    let workingKeysLink = this.links.find((x) => x.text === "Working Keys");
    workingKeysLink.disabled = !pmkOrMfkLoaded || workingKeysDisable;

    let certificatesAndRequestsLink = this.links.find(
      (x) => x.text === "Certificates & Requests",
    );
    certificatesAndRequestsLink.disabled = !pmkOrMfkLoaded;
  },
  methods: {
    pmkOrMfkLoaded: async function () {
      let url = `/clusters/sessions/${this.getSessionId()}/major-keys`;
      let data = await this.$httpV2.get(url, {
        errorContextMessage: "Failed to get major key status",
      });
      let majorKeys = data.majorKeys;
      let pmk = majorKeys.find((x) => x.name === "PMK");
      let mfk = majorKeys.find((x) => x.name === "MFK");
      return pmk.loaded || mfk.loaded;
    },
  },
};
</script>

<style scoped>
.major-key-error {
  padding: 1rem;
  margin: 1rem auto 0 auto;
  width: fit-content;
  border: 1px solid var(--border-color);
  background: linear-gradient(to bottom, #f9f9f9 5%, #e9e9e9 100%);
  box-shadow:
    0 1px 3px 0 rgba(0, 0, 0, 0.1),
    0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.major-key-error .fa-exclamation-triangle {
  margin-right: 0.5rem;
  color: var(--bs-warning);
}

.action-links {
  --box-width: 200px;
  display: grid;
  gap: 1rem;
  margin: 2rem;
  grid-template-columns: repeat(auto-fit, var(--box-width));
  justify-content: center;
}
.action-links > a {
  display: block;
  text-decoration: none;
  width: var(--box-width);
  box-shadow:
    0 1px 3px 0 rgba(0, 0, 0, 0.1),
    0 1px 2px 0 rgba(0, 0, 0, 0.06);
  border: 1px solid var(--border-color);
  color: inherit;
}

.top {
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(
    180deg,
    rgba(249, 249, 249, 1) 0%,
    rgba(241, 241, 241, 1) 35%,
    rgba(238, 238, 238, 1) 100%
  );
  font-size: 20px;
  color: var(--text-color-blue-lighter);
  border-bottom: 1px solid var(--border-color);
  height: 60px;
}

.bottom {
  font-size: 13px;
  margin-bottom: 0;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: white;
}

.disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
</style>

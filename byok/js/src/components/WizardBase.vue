<template>
  <div
    ref="wizardDiv"
    tabindex="-1"
    class="wizard"
    @keydown.esc="$bus.emit('wizardClose')"
  >
    <header class="wizard-header">
      <p class="wizard-title">{{ wizardTitle }}</p>
      <button
        class="button button-wide icon-text-button"
        @click="$bus.emit('wizardClose')"
      >
        <i class="fa fa-times" />
        <span>Cancel</span>
      </button>
    </header>

    <div class="wizard-work-area">
      <header>
        <p class="page-title" :title="currentPage.title">
          {{ currentPage.title }}
        </p>
        <nav v-if="!wizardSubmitted">
          <button
            v-for="(wizardPage, index) in _wizardPages"
            :key="wizardPage.title"
            :class="{ active: wizardPage === currentPage }"
            :disabled="!wizardPage.opened"
            :data-page-index="index"
            @click="handleWorkAreaNavButtonClick"
          >
            {{ index + 1 }}
          </button>
        </nav>
      </header>

      <div class="wizard-page">
        <p v-if="currentPage.description" class="wizard-page-description">
          {{ currentPage.description }}
        </p>
        <component
          :is="currentPage.component"
          :key="currentPage.title"
          v-model="currentPage.data"
          v-bind="currentPage.props"
          @wizardNextPage="handleWizardNextPage"
          @wizardSubmit="handleWizardSubmit"
          @wizardContinueButtonDisabled="handleWizardContinueButtonDisabled"
        />
      </div>

      <footer v-if="currentPage.continueButtonAtBottom">
        <button
          class="continue-button blue-button button button-wide"
          :disabled="wizardContinueButtonDisabled"
          @click="handleWizardNextPage"
        >
          Continue <i class="fa fa-arrow-right icon-left" />
        </button>
      </footer>
    </div>
    <!--
      todo: Implement partChecks logic
      :partChecks="['5D79', '234G', '123D']"
    -->
    <wizard-summary
      :wizard-summary-title="wizardSummaryTitle"
      :part-checks="[]"
      :basic-list="wizardSummaryBasicList"
    />
  </div>
</template>

<script>
import WizardSummary from "@/components/WizardSummary.vue";

import "@/assets/wizard-page.css";

export default {
  components: {
    "wizard-summary": WizardSummary,
  },
  props: {
    wizardTitle: {
      type: String,
      required: true,
    },
    wizardSummaryTitle: {
      type: String,
      required: true,
    },
    wizardPages: {
      type: Array,
      required: true,
    },
    wizardSubmit: {
      type: Function,
      required: true,
    },
  },
  data: function () {
    return {
      wizardPageIndex: 0,
      wizardSubmitted: false,
      wizardContinueButtonDisabled: true,
    };
  },
  computed: {
    _wizardPages: function () {
      return this.wizardPages.filter((page) => {
        if (page.pageEnabled === undefined) {
          return true;
        } else {
          return page.pageEnabled();
        }
      });
    },
    currentPage: function () {
      let page = this._wizardPages[this.wizardPageIndex];
      // Perhaps a watch on this.wizardPageIndex
      // would communicate things better?
      // I simply want to keep track of which pages have been opened.
      // The only way to open a page is to:
      // open the wizard (wizardPageIndex is initialized at 0)
      // or change wizardPageIndex.
      page.opened = true;
      return page;
    },
    wizardSummaryBasicList: function () {
      let datas = [];
      for (let wizardPage of this._wizardPages) {
        if (wizardPage.opened) {
          if (Object.keys(wizardPage.data).length > 0) {
            datas.push(wizardPage.data);
          }
        }
      }

      let basicList = [];
      for (let data of datas) {
        for (let item of Object.values(data)) {
          let isFalsy = !item.value && item.value !== 0;
          let isEmptyArray =
            Array.isArray(item.value) && item.value.length === 0;
          let displayItem = item.wizardSummaryText && !isFalsy && !isEmptyArray;
          if (displayItem) {
            basicList.push(item);
          }
        }
      }

      return basicList;
    },
  },
  mounted: function () {
    this.$refs.wizardDiv.focus();
  },
  methods: {
    handleWorkAreaNavButtonClick: function (event) {
      let pageIndex = parseInt(event.target.dataset.pageIndex);
      this.wizardPageIndex = pageIndex;
    },
    handleWizardNextPage: function () {
      if (this.wizardPageIndex !== this._wizardPages.length - 1) {
        this.wizardPageIndex++;
      }
    },
    handleWizardSubmit: function (success, fail) {
      this.wizardSubmitted = true;
      this.wizardSubmit(success, fail);
    },
    handleWizardContinueButtonDisabled: function (disabled) {
      this.wizardContinueButtonDisabled = disabled;
    },
  },
};
</script>

<style>
.wizard {
  --grid-gap: 1rem;
  z-index: 1;
  overflow: auto;
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  padding: 1rem;
  background-color: #f5f5f5;
  font-size: 13px;
  display: grid;
  gap: var(--grid-gap);
  grid-template-columns: 60% calc(40% - var(--grid-gap));
  grid-auto-rows: max-content;
  grid-template-areas:
    "header header"
    "work-area summary";
}

.wizard-header {
  grid-area: header;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.wizard-title {
  font-size: 18px;
  margin-bottom: 0;
}

.wizard-work-area {
  height: max-content;
  grid-area: work-area;
  box-shadow:
    0 1px 3px 0 rgba(0, 0, 0, 0.1),
    0 1px 2px 0 rgba(0, 0, 0, 0.06);
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

/* wizard-work-area header */
.wizard-work-area > :first-child {
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}

/* wizard-work-area contents */
.wizard-work-area > :last-child {
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
}

.wizard-work-area > header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f9f9f9;
  color: #333333;
  padding: 0 1rem;
  border-bottom: 1px solid;
  border-color: var(--border-color);
}

.page-title {
  font-size: 1rem;
  color: var(--text-color-blue);
  margin-bottom: 0;
  /*
      Give the header padding-top/bottom of zero
      Give the padding to the p element (element with smallest height) to prevent
      the layout shift when the nav buttons are removed
    */
  padding: 0.5rem 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.wizard-work-area > header > nav {
  display: flex;
}

.wizard-work-area > header > nav > button + button {
  margin-left: 0.5rem;
}

.wizard-work-area > header > nav > button {
  width: 2rem;
  height: 2rem;
  border: 1px solid;
  border-radius: 1rem;
  background: #ecf0f5;
  color: var(--text-color-blue-lighter);
  border-color: #c6d1df;
  font-family: "Roboto", sans-serif;
}

.wizard-work-area > header > nav > button:disabled {
  background: transparent;
  color: var(--text-color);
  border-color: #dddddd;
}

.wizard-work-area > header > nav > button.active {
  background: #3c8dbc;
  color: white;
  border-color: #347da8;
  text-shadow: 0 -1px 0 rgba(0, 0, 0, 0.25);
}

.wizard-page {
  padding: 1rem;
  background-color: white;
}

.wizard-work-area > footer {
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid;
  border-color: var(--border-color);
  padding: 1rem;
}

.continue-button {
  display: flex;
  justify-content: center;
  align-items: center;
}

.continue-button > i {
  margin-left: 0.5rem;
}
</style>

<template>
  <div class="wizard-summary">
    <p>{{ wizardSummaryTitle }}</p>
    <hr />
    <ul
      v-if="Array.isArray(partChecks) && partChecks.length > 0"
      class="wizard-summary-part-check-list"
    >
      <li v-for="(partCheck, index) in partChecks" :key="partCheck">
        <span>Part {{ index + 1 }} check digits:</span>
        <span class="checksum">{{ partCheck }}</span>
      </li>
    </ul>

    <ul
      v-if="Array.isArray(basicList) && basicList.length > 0"
      class="wizard-summary-basic-list"
    >
      <li v-for="item in basicList" :key="item.wizardSummaryText">
        <span>{{ item.wizardSummaryText }}</span>
        <span :title="joinIfArray(item.value)">{{
          joinIfArray(item.value)
        }}</span>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  props: {
    wizardSummaryTitle: {
      type: String,
      required: true,
    },
    partChecks: {
      type: Array,
      required: false,
    },
    basicList: {
      type: Array,
      required: false,
    },
  },
  methods: {
    joinIfArray: function (value) {
      if (Array.isArray(value)) {
        return value.join(", ");
      } else {
        return value;
      }
    },
  },
};
</script>

<style scoped>
hr {
  color: var(--border-color);
  opacity: 1;
}

.wizard-summary {
  height: max-content;
  grid-area: summary;
  box-shadow:
    0 1px 3px 0 rgba(0, 0, 0, 0.1),
    0 1px 2px 0 rgba(0, 0, 0, 0.06);
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: #f9fafc;
}

.wizard-summary > p {
  font-size: 1rem;
  color: var(--text-color-blue);
  margin-bottom: 0;
}

.wizard-summary > ul {
  list-style: none;
  margin-top: 1rem;
  margin-bottom: 0;
  padding-left: 0;
}

.wizard-summary-part-check-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, 160px);
  justify-content: center;
  font-size: 0.7rem;
  gap: 0.3rem;
}

.wizard-summary-part-check-list > li {
  white-space: nowrap;
  padding: 0.3rem 0.6rem;
  background-color: #ecf0f5;
  color: var(--text-color-blue);
  border: 1px solid #c6d1df;
  border-radius: 3px;
}

.wizard-summary-basic-list > li {
  display: flex;
  justify-content: space-between;
  margin-top: 0.2rem;
}

.wizard-summary-basic-list > li + li {
  border-top: 1px solid var(--border-color);
}

/* left text */
.wizard-summary-basic-list > li > span:first-child {
  white-space: nowrap;
}

/* right text */
.wizard-summary-basic-list > li > span:last-child {
  color: var(--text-color-blue-lighter);
  margin-left: 1rem;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}
</style>

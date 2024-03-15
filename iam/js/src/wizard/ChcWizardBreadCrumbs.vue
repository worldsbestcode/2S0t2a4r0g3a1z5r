<template>
  <div class="wizard-bread-timeline">
    <div
      v-for="(crumb, index) in props.crumbs"
      :key="crumb"
      class="wizard-bread-timeline-event"
    >
      <div class="line-left" :class="props.pageIndex >= index && 'active'" />
      <div
        class="line-right"
        :class="
          (props.pageIndex > index ||
            (props.pageIndex === index && index === crumbs.length - 1)) &&
          'active'
        "
      />
      <div
        class="circle"
        :class="[
          props.pageIndex >= index && 'active',
          props.pageIndex > index && 'active-circle',
        ]"
      >
        <img src="/shared/static/check-mark.svg" />
      </div>
      <div class="text" :class="props.pageIndex >= index && 'active-text'">
        {{ crumb }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from "vue";

const props = defineProps({
  crumbs: {
    type: Array,
    required: true,
  },
  pageIndex: {
    type: Number,
    required: true,
  },
});
</script>

<style scoped>
.wizard-bread-timeline {
  display: flex;
}

.wizard-bread-timeline-event {
  position: relative;
  width: 100%;
}

.line-left,
.line-right {
  height: 3px;
  background: var(--border-color);
  width: 50%;
  position: absolute;
  top: 0;
}

.line-right {
  right: 0;
}

.circle {
  height: 1rem;
  width: 1rem;
  border-radius: 50%;
  background: var(--border-color);
  position: absolute;
  top: 1.5px;
  left: 50%;
  transform: translate(-50%, -50%);
}

.circle img {
  width: 0.75rem;
  height: 0.75rem;
  display: none;
}

.text {
  white-space: nowrap;
  margin-top: 1rem;
  padding: 0 2rem;
  font-weight: 500;
  text-align: center;

  color: var(--muted-text-color);
}

.active {
  background: var(--primary-color);
}

.active-text {
  color: var(--primary-text-color);
}

.active-circle {
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  padding: 6px;
}

.active-circle img {
  display: initial;
}
</style>

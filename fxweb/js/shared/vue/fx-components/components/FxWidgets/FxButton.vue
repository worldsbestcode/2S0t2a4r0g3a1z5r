<style>
</style>
<template>

  <button tabindex="-1" :class="buttonClasses"
    @click="callback"
    :disabled="disabled"
    :style="innerstyle">
    <slot>{{typeObj.name}}</slot>
  </button>
</template>
<script>
export default {
  props: [
    'type',
    'size',
    'innerstyle',
    'disabled',
    'callback'
  ],
  data: function () {
    return {
      'fxButtonTypes': {'noType': {name: 'noType', class: 'default', width: '', size: 'md'},
        'default': {name: 'default', class: 'default', width: 'block', size: 'md'},
        'primary': {name: 'primary', class: 'primary', width: 'block', size: 'md'},
        'success': {name: 'success', class: 'success', width: 'block', size: 'md'},
        'info': {name: 'info', class: 'info', width: 'block', size: 'md'},
        'danger': {name: 'danger', class: 'danger', width: 'block', size: 'md'},
        'warning': {name: 'warning', class: 'warning', width: 'block', size: 'md'}}
    };
  },
  computed: {
    typeObj: function () {
      return this.type ? this.fxButtonTypes[this.type] : this.fxButtonTypes['noType'];
    },
    buttonClasses: function () {
      let classes = [];
      classes.push('btn');
      if (this.typeObj.width) {
        classes.push('btn-' + this.typeObj.width);
      }
      classes.push('btn-' + this.typeObj.class);
      classes.push('btn-' + this.size ? this.size : this.typeObj.size);
      return classes;
    }
  }
};
</script>

<template>
  <div>
    <fx-text-file-input v-model="fileData">
    </fx-text-file-input>
    <major-key-selector
      v-if="loadedMajorKeys.length > 0"
      :major-keys="loadedMajorKeys"
      :major-key.sync="selectedMajorKey"
    >
    </major-key-selector>
  </div>
</template>
<script>
import TextFileInput from 'kmes/components/misc/TextFileInput';
import MajorKeySelector from 'kmes/components/misc/MajorKeySelector';

export default {
  components: {
    'fx-text-file-input': TextFileInput,
    'major-key-selector': MajorKeySelector,
  },
  props: {
    loadedMajorKeys: {
      type: Array,
      required: false,
      default () {
        return [];
      },
    },
    majorKey: {
      type: String,
      default: 'MFK',
    },
  },
  data () {
    return {
      fileData: '',
      selectedMajorKey: this.majorKey,
    };
  },
  watch: {
    fileData () {
      this.$emit('update:fileData', this.fileData);
    },
    selectedMajorKey () {
      this.$emit('update:majorKey', this.selectedMajorKey);
    },
    majorKey () {
      this.selectedMajorKey = this.majorKey;
    },
  }
};
</script>

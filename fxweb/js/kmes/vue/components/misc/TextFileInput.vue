<template>
  <div class="form-group container-fluid">
    <div class="row">
      <label>Data:</label>
      <textarea
        class="form-control"
        :rows="rows"
        :cols="cols"
        v-model="this.fileData"
        readonly
      >
      </textarea>
    </div>
    <div class="row">
      <file-input-button
        :accept="accept"
        @change="selectFile"
      >
        Browse
      </file-input-button>
    </div>
  </div>
</template>
<script>
import FileInputButton from 'kmes/components/misc/FileInputButton';

export default {
  components: {
    'file-input-button': FileInputButton,
  },
  props: {
    // The value shown in file data box
    value: {
      type: String,
      default: '',
    },
    // which File types are allowed
    accept: {
      type: String,
      default: '',
    },
    // number of rows text area is
    rows: {
      required: false,
      default: 15,
    },
    // number of columns the text area is
    cols: {
      required: false,
      default: 60,
    },
  },
  model: {
    property: 'value',
    event: 'update:value',
  },
  data: function () {
    return {
      fileData: this.value,
    };
  },
  watch: {
    value: function () {
      this.fileData = this.value;
    },
    fileData: function () {
      this.$emit('update:value', this.fileData);
    },
  },
  methods: {
    /**
     * Reads the file data, and sets fileData (which updates the displayed file data)
     *
     * @param e The input event after selecting a file.
     */
    selectFile: function (e) {
      let files = e.target.files || e.dataTransfer.files;
      let reader = new window.FileReader();
      let self = this;

      reader.onload = function () {
        let text = reader.result;
        self.fileData = text;
      };
      reader.readAsText(files[0]);
    },
  }
};
</script>

<style scoped>
.namespace {
  width: 500px;
  display: flex;
  flex-wrap: wrap;
}

.namespace__entry {
  width: 50%;
}
</style>
<template>
  <div id="tokenNamespace" class="namespace">
    <div
      v-for="namespaceEntry in namespaceEntries"
      class="namespace__entry"
      :key="namespaceEntry.id"
    >
      <input
        type="checkbox"
        :id="getID(namespaceEntry)"
        @change="updateNamespaceValue(namespaceEntry.value)"
        :checked="isNamespaceChecked(namespaceEntry.value)"
        :disabled="isNamespaceDisabled(namespaceEntry)"
      >
      <label :for="getID(namespaceEntry)">
        {{ namespaceEntry.text }}
      </label>
    </div>
  </div>
</template>
<script>
export default {
  data: function () {
    return {
      tokenNamespace: ['Decimal'],
      namespaceEntries: [
        { id: 1, text: 'Decimal', value: 'Decimal', isSymbol: false },
        { id: 2, text: 'Hex', value: 'Hex', isSymbol: false },
        { id: 3, text: 'Lowercase', value: 'Lowercase', isSymbol: false },
        { id: 4, text: 'Uppercase', value: 'Uppercase', isSymbol: false },
        { id: 5, text: 'Space ( )', value: 'Space', isSymbol: true },
        { id: 6, text: 'Underscore (_)', value: 'Underscore', isSymbol: true },
        { id: 7, text: 'Dash (-)', value: 'Dash', isSymbol: true },
        { id: 8, text: 'Period (.)', value: 'Period', isSymbol: true },
        { id: 9, text: 'At sign (@)', value: 'At', isSymbol: true },
        { id: 10, text: 'Slash (/)', value: 'Slash', isSymbol: true },
        { id: 11, text: 'Back Slash (\\)', value: 'BackSlash', isSymbol: true },
        { id: 12, text: 'Comma (,)', value: 'Comma', isSymbol: true },
        { id: 13, text: 'All Symbols', value: 'All', isSymbol: false },
      ]
    };
  },
  methods: {
    updateNamespaceValue: function (value) {
      if (this.isNamespaceChecked(value)) {
        var idx = this.tokenNamespace.indexOf(value);
        this.tokenNamespace.splice(idx, 1);
      } else {
        this.tokenNamespace.push(value);
      }

      this.$emit('changed', this.tokenNamespace);
    },
    findEntryByValue: function (value) {
      for (var idx in this.namespaceEntries) {
        var entry = this.namespaceEntries[idx];
        if (entry.value === value) {
          return entry;
        }
      }
      return null;
    },
    isNamespaceChecked: function (value) {
      var entry = this.findEntryByValue(value);

      if (this.tokenNamespace.includes(value)) {
        return true;
      }

      if (entry.isSymbol) {
        return this.tokenNamespace.includes('All');
      }

      return false;
    },
    isNamespaceDisabled: function (namespaceEntry) {
      return namespaceEntry.isSymbol && this.isNamespaceChecked('All');
    },
    getID: function (namespaceEntry) {
      return 'entry' + namespaceEntry.value;
    }
  }
};

</script>

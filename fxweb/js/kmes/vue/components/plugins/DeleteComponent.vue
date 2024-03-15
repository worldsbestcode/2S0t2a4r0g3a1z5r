<style lang="scss" scoped>
.table th {
  font-size: 1.4rem;
}
.table td {
  font-size: 1rem;
  padding-left: 1em;
}
</style>
<template>
  <table
    v-if="data.data && data.data.length > 0"
    class="table is-bordered is-striped is-fullwidth"
  >
    <thead>
      <tr>
        <th v-for="header in data['headers']" :key='header'>
          {{ header }}
        </th>
      </tr>
    </thead>

    <tbody>
      <tr v-for="(row, index) in data.data" :key='index'>
        <td v-for="entry in data['order']" :key='entry'>
          <span v-if="row[entry] == null"></span>
          <span v-else-if="row[entry].constructor === Array">
            {{ row[entry].join(', ') }}
          </span>
          <span v-else>
            {{ row[entry] }}
          </span>
        </td>
      </tr>
    </tbody>
  </table>
</template>
<script>
export default {
  props: {
    data: {
      required: true
    },
  },
};
</script>

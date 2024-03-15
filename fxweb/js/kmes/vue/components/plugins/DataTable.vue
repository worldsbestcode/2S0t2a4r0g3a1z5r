<style lang="scss" scoped>
@import '~src/css/variables.scss';

.border {
  border: 2px solid #ddd;
}

.datatable {
  max-height: 70vh;
  overflow-y: auto;
  overflow-y: overlay;
  width: 100%;
  margin-bottom: 15px;
}

.rTable {
  display: table;
  width: 100%;
}
.rTableRow {
  display: table-row;
  vertical-align: inherit;
  border-color: inherit;
}
.rTableCell, .rTableHead {
  display: table-cell;
  padding: 8px;
}

.rTableHeading {
  background-color: #eee;
  display: table-header-group;
  font-weight: bold;
  border-bottom: 2px solid #ddd;
}
.rTableFoot {
  display: table-footer-group;
  font-weight: bold;
}
.rTableBody {
  display: table-row-group;
}

.rTableBody:nth-child(even) {
  background-color: #e4e4e4;
  .inner-row {
    background-color: white;
  }
}
.rTableBody:nth-child(odd) {
  background-color: white ;
  .inner-row {
    background-color: $base;
  }
}

/* table borders */
.rTableRow {
  .rTableHead {
    border-bottom: 2px solid #ddd;
  }
  .rTableCell {
    border-bottom: 1px solid #ddd;
  }
}

.nav-tabs a {
  color: $primary;
}

#loading-dialog {
  text-align: center;
}

label {
  white-space: nowrap;
  font-weight: normal;
}

.pagination {
  li {
    span {
      color: $primary;
    }
  }
}

[v-cloak] {
  display: none;
}
.clickable-row {
  cursor: pointer;

  &:hover {
    background-color: $table-hover-color;
  }
}

.ion-arrow-up-b, .ion-arrow-down-b {
  color: #9c9c9c;
}

.sorted {
  color: #911211;
}

.finalCellData {
  width: initial;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.above-table {
  display: flex;
  align-items: center;
  label {
    margin-bottom: 0px;
    padding-left: 0px;
  }
}

#page-info {
  display: inline-flex;
  align-items: center;
  label:first-child {
    padding-left: 0px;
    margin-bottom: 0px;
  }
}

.no-click {
  pointer-events: none;
  opacity: .5;
  transition: all .1s linear;
}

#table-search {
  justify-content: flex-end;
}

// Override bootstrap's margin setting on checkboxes
.checkbox input[type="checkbox"] {
  margin: 0px;
}
</style>
<template>
  <div :class="{'no-click': loading }">
    <div>
      <div class="column is-12">
        <div class="columns">
          <div id="showEntries" class="column is-6 above-table field is-grouped is-marginless">
            <label class="label control">
              Show
            </label>
            <span class="select control">
              <select v-model="itemsPerPage">
                <option value="10">10</option>
                <option value="25">25</option>
                <option value="50">50</option>
              </select>
            </span>
            <label class="label control">
              entries
            </label>
          </div>

          <div class="column is-3 above-table field is-grouped is-marginless">
            <slot></slot>
          </div>

          <div id="table-search" class="column above-table is-3">
            <span class="control">
              <input
                type="text"
                class="input"
                v-if="showSearch"
                v-model="searchText"
                :placeholder="searchLabel"
                @keyup.enter="searchData()">
            </span>
            <span>
              <button class="button control" v-on:click="clearSearch()">Clear</button>
            </span>
          </div>
        </div>

        <transition name="fade">
          <div v-if="allData && allData.length > 0" class="columns">
            <div id="datatable" class="datatable column is-12">
              <div>
                <div id="loading-dialog" v-if="headers.length === 0" class="columns">
                  <div class="column is-12">
                    <div class="title is-3">Loading...</div>
                  </div>
                </div>
              </div>

              <div
                class="rTable table-striped"
                v-if="typeof allData !== 'undefined' && allData.length > 0"
                :class="{'border': allData.length > 0}"
              >
                <div class="rTableHeading">
                  <div class="rTableRow">
                    <div class="rTableHead" v-if="editable">
                      <label class="checkbox">
                        <input type="checkbox" v-model="checked" @click="selectAll($event.target.checked)">
                      </label>
                    </div>

                    <div
                      v-for="(header, index) in headers"
                      class="rTableHead data"
                      :class="{'click': !disabledSorting.includes(order[index])}"
                      @click="sortBy(order[index])"
                      :key="index"
                    >
                        {{ header }}
                      <span v-if="!disabledSorting.includes(order[index])">
                        <i
                          class="ion-arrow-up-b"
                          :class="{'sorted': sortedByKey == order[index] && !reversed}"
                        >
                        </i>
                        <i
                          class="ion-arrow-down-b"
                          :class="{'sorted': sortedByKey == order[index] && reversed}"
                        >
                        </i>
                      </span>
                    </div>
                  </div>
                </div>

                <div
                  v-for="(row, index) in filteredAllData"
                  class="rTableBody"
                  :class="{'clickable-row': click}"
                  :key='index'
                >
                  <div class="rTableRow">
                    <div class="rTableCell" v-if="editable">
                      <label class="checkbox">
                        <input type="checkbox" :value="stringify(row)" v-model="checkedItems">
                      </label>
                    </div>

                    <div
                      v-for="entry in order"
                      class="rTableCell data"
                      @click="ignoreClick.indexOf(entry) === -1 ? rowClicked(row) : null"
                      :key="entry"
                      :style="{'width': width}"
                    >
                      <span v-if="row[entry] == null"></span>
                      <span v-else-if="row[entry].constructor === Array">
                        {{ row[entry].join(', ') }}
                      </span>
                      <span v-else>
                        {{ row[entry] }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </transition>

        <transition name="fade">
          <div
            v-if="filteredAllData && filteredAllData.length === 0 && headers && headers.length > 0"
            class="columns"
            id="loading-dialog"
          >
            <div class="column is-12">
              <div class="title is-3">No {{ title.toLowerCase() }} found.</div>
            </div>
          </div>
        </transition>

        <div class="columns">
          <div class="column is-10">
            <div class="field is-grouped" id="page-info">
              <div class="control">
                <label class="label">
                  Page
                </label>
              </div>

              <div class="control">
                <input
                  class="input"
                  type="number"
                  min="1"
                  :max="pageCount"
                  v-model.number="currentPage"
                  @keyup.enter="updatePage(currentPage)"
                >
              </div>

              <div class="control">
                <label class="label">
                  of {{ pageCount }} (Total Records: {{totalCount}})
                </label>
              </div>
            </div>
          </div>

          <div class="column is-2">
            <div class="pagination is-centered">
              <ul class="pagination-list">
                <li class="click pagination-link" v-on:click="prevPage">
                  <span aria-hidden="true">&laquo;</span>
                </li>

                <li class="click pagination-link" v-on:click="nextPage">
                  <span aria-hidden="true">&raquo;</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import $ from 'jquery';
import _ from 'lodash';
import Vue from 'vue';

export default {
  props: {
    ignoreClick: {
      type: Array,
      default: function () {
        return [];
      }
    },
    newName: {},
    tableData: {
      required: true,
      default: function () {
        return {
          data: [],
          page: 0,
          pages: 0,
          total: 0,
          order: '',
          headers: [],
          paginate: false,
        };
      },
    },
    title: {
      required: true,
      default: 'records'
    },
    editable: {
      require: false
    },
    inputCheckedItems: {},
    clickCallback: {
      type: Function,
      default: function () {}
    },
    click: {
      type: Boolean,
      default: false
    },
    expand: {
      type: Function,
      default: function () {}
    },
    paginate: {
      default: false
    },
    searchLabel: {
      default: 'Search'
    },
    showSearch: {
      default: true
    },
    disabledSorting: {
      type: Array,
      default: function () {
        return [];
      }
    },
    parentGroup: {},
    initialPage: {
      type: Number,
      default: 1
    },
    bypassClearSearch: {
      type: Boolean,
      default: false
    }
  },
  created () {
    this.currentPage = this.initialPage;
    this.calcAllData();
    this.$on('refreshTable', function () {
      this.updatePage(1);
    });
  },
  beforeDestroy: function () {
    if (!this.bypassClearSearch) {
      this.clearSearch();
    }

    this.$emit('clear-checked');
    this.$off('refreshTable');
  },
  computed: {
    filteredAllData: function () {
      const self = this;

      if (!self.allData) {
        self.allData = [];
      }

      let data = self.limit(self.allData, self.itemsPerPage, self.pageOffset);
      _.forEach(data, function (item) {
        if (item.hasOwnProperty('failed')) { // eslint-disable-line no-prototype-builtins
          if (item.failed === '-1' || item.failed === '-2' || item.failed === 'Locked' || item.failed === '1') {
            item.failed = 'Locked';
          } else if (item.failed === '0' || item.failed === 'Ready') {
            item.failed = 'Ready';
          } else {
            item.failed = (isNaN(parseInt(item.failed))) ? item.failed : 'Failed: ' + item.failed;
          }
        }

        item.json = JSON.stringify(item);

        if (self.tableData.page === self.currentPage) {
          self.loading = false;
        }
      });

      return data;
    },
    width: function () {
      var self = this;
      var width = Math.floor((1 / self.headers.length) * 100);
      return width + '%';
    },
    totalCount: function () {
      if (this.paginate) {
        // Needs to be updated to data.total
        return this.tableData.total;
      }
      return (typeof this.tableData.data !== 'undefined') ? this.tableData.data.length : 0;
    },

    pageCount: function () {
      var self = this;
      var data = self.allData;
      if (this.paginate) {
        // Needs to be updated to data.pages
        return self.tableData.pages;
      }
      if (self.searchText === '') {
        self.setPages(data);
        return self.pages;
      }

      var filteredData = _.filter(data, function (x) {
        return self.textInData(x, self.searchText);
      });

      var dataLength = filteredData.length;
      if (dataLength > 0) {
        self.setPages(filteredData);

        // Ensure we don't go out-of-bounds
        if (self.currentPage > self.pages) {
          self.currentPage = 1;
        }

        self.calculatePageCount(dataLength);
        return self.pages;
      } else {
        self.currentPage = 1;
        self.pages = 1;
        return 1;
      }
    },
    pageOffset: function () {
      return this.itemsPerPage * this.currentPage - this.itemsPerPage;
    },
    order: function () {
      return this.tableData.order;
    },
    headers: function () {
      return this.tableData.headers;
    }
  },
  data () {
    return {
      loading: false,
      currentPage: 1,
      itemsPerPage: 10,
      pages: 1,
      searchText: '',
      sortedByKey: '',
      reversed: false,
      items: {},
      cPages: {},
      open: {},
      checked: false,
      allData: [],
      checkedItems: [],
    };
  },
  watch: {
    itemsPerPage: function () {
      this.currentPage = 1;
      this.updatePage(1);
    },
    pages: function (val, oldVal) {
      this.currentPage = 1;
    },
    tableData: function () {
      $('.nav-tabs li.active').trigger('click');
      this.calcAllData();
    },
    inputCheckedItems: function () {
      const self = this;
      self.checkedItems = self.inputCheckedItems;
      if (self.checkedItems.length !== self.allData.length || self.allData.length === 0) {
        self.checked = false;
      } else {
        self.checked = true;
      }
    },
    checkedItems: function () {
      this.$emit('update-checked', this.checkedItems, this.parentGroup);
    },
    filteredAllData: function () {
      if (this.filteredAllData.length === 0) {
        this.loading = false;
      }
    },
    totalCount: function () {
      // If the total count changes, a query must have been completed
      this.loading = false;
    }
  },

  methods: {
    calcAllData: function () {
      const self = this;
      if (self.paginate) {
        self.allData = self.tableData.data;
        return;
      }
      var data = self.tableData.data;

      self.setPages(data);
      self.allData = data;
    },
    searchData: function () {
      if (this.paginate) {
        this.updatePage(1);
        this.currentPage = 1;
      } else {
        this.allData = this.filterBy(this.searchText);
      }
    },
    clearSearch: function () {
      this.searchText = '';
      this.searchData();
    },
    updatePage: function (page) {
      const self = this;
      let dt = document.getElementById('datatable');
      if (dt != null) {
        dt.scrollTop = 0;
      }
      if (self.paginate) {
        self.loading = true;
      }
      let payload = {
        page: page,
        page_size: self.itemsPerPage,
        search: self.searchText,
        order: self.reversed ? 'desc' : 'asc',
        order_by: self.sortedByKey
      };
      self.currentPage = page;
      self.$emit('page-change', payload);
    },
    sortBy: function (key) {
      if (this.disabledSorting.includes(key)) {
        return;
      }
      if (this.sortedByKey === key && !this.reversed) {
        this.reversed = true;
        if (this.paginate) {
          this.updatePage(1);
          return;
        }
        this.allData = this.allData.reverse();
      } else {
        this.reversed = false;
        this.sortedByKey = key;
        if (this.paginate) {
          this.updatePage(1);
          return;
        }
        this.allData = _.sortBy(this.allData, key);
      }
    },
    nextPage: function () {
      document.getElementById('datatable').scrollTop = 0;
      if (this.currentPage < this.pageCount) {
        this.currentPage = this.currentPage + 1;
        if (this.paginate) {
          this.updatePage(this.currentPage);
        }
      }
    },
    prevPage: function () {
      var self = this;
      if (self.currentPage > 1) {
        self.currentPage = self.currentPage - 1;
        if (this.paginate) {
          this.updatePage(this.currentPage);
        }
      }
    },
    setPages: function (data) {
      try {
        var dataLength = data.length;
      } catch (TypeError) {
        data = [];
        dataLength = 0;
      }

      this.pages = this.calculatePageCount(dataLength);
    },

    calculatePageCount: function (dataLength) {
      var pageCount = Math.ceil(dataLength / this.itemsPerPage);
      if (pageCount === 0) {
        return 1;
      }

      return pageCount;
    },
    fetch: function (row) {
      var self = this;
      Vue.set(self.open, row[self.newName], false);
      self.expand(row[self.newName]);
    },
    toggle: function (row) {
      var self = this;
      Vue.set(self.open, row[self.newName], !(self.open[row[self.newName]]));
      Vue.set(self.items, row[self.newName], !(self.items[row[self.newName]]));
    },
    textInData: function (data, text) {
      const self = this;
      const headers = self.order;
      for (var i = 0; i <= headers.length; i++) {
        if (String(data[headers[i]]).toLowerCase().indexOf(text) > -1) {
          return true;
        }
      }

      return false;
    },
    rowClicked: function (row) {
      if (this.click && this.clickCallback) {
        this.$emit('restored-page', this.currentPage);
        this.clickCallback(row);
      }
    },
    selectAll: function (checked) {
      var self = this;
      self.checkedItems = [];
      // Checked isn't updated yet so we use the event checked
      if (checked) {
        self.allData.forEach(function (row, index) {
          self.checkedItems.push(self.stringify(row));
        });
      } else {
        self.checkedItems = [];
      }
    },
    limit: function (arr, n, offset) {
      if (this.paginate) {
        return arr;
      }

      if (!offset) {
        offset = 0;
      }
      if (typeof n === 'string') {
        n = parseInt(n);
      }
      return typeof n === 'number' ? arr.slice(offset, offset + n) : arr;
    },
    stringify: function (row) {
      return JSON.stringify(row);
    },
    filterBy: function (searchText) {
      const self = this;
      if (_.isEmpty(searchText)) {
        return self.tableData.data;
      } else {
        return _.filter(self.tableData.data, function (item) {
          for (let field in item) {
            if (String(item[field]).indexOf(searchText) !== -1) {
              return true;
            }
          }
        });
      }
    }
  }
};
</script>

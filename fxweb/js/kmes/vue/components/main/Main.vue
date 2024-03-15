<style lang="scss" scoped>
.column {
  transition: all .15s linear;
  position: relative;
}

.columns.is-gapless {
  margin-bottom: 0px !important;
}

#canvas {
  overflow: auto;
}

#main {
  position: relative;
  height: 100%;
}

.sidebar-big {
  width: 20%;
  flex: none;
}

.sidebar-small {
  width: 5%;
  flex: none;
}

.main-big {
  width: 80%;
  flex: none;
}

.main-small {
  width: 95%;
  flex: none;
}
</style>
<template>
  <div id="main" class="columns is-gapless">
    <sidebar
      class="column"
      :class="{ 'sidebar-big': !sidebarToggled, 'sidebar-small': sidebarToggled}"
      @viewChanged="viewChanged"
      :available-views="views"
      :selected-view="selectedView"
      :sidebar-toggled="sidebarToggled"
      :user-name="userName"
    >
    </sidebar>
    <main-canvas
      id="canvas"
      class="column"
      :class="{ 'main-big': !sidebarToggled, 'main-small': sidebarToggled}"
      :selected-view="selectedView"
      :classPerms="classPerms"
    >
    </main-canvas>
  </div>
</template>

<script>
import Sidebar from './Sidebar';
import MainCanvas from './MainCanvas';
import LoginInfo from 'shared/LoginInfo';

export default {
  components: {
    MainCanvas,
    Sidebar
  },
  data () {
    return {
      sidebarToggled: false,
      views: [
        'token',
        'ca',
        'certificate',
      ],
      selectedView: 'token',
      userName: LoginInfo.getLoginInfo().name,
      classPerms: LoginInfo.getClassPermissions(),
    };
  },
  methods: {
    viewChanged: function (view) {
      this.selectedView = view;
    }
  },
  created: function () {
    const self = this;

    self.$bus.$on('toggleSidebar', function (toggled) {
      if (typeof toggled === 'boolean') {
        self.sidebarToggled = toggled;
      } else {
        self.sidebarToggled = !self.sidebarToggled;
      }
    });
  },
};
</script>

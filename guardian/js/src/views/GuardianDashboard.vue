<template>
  <br />
  <div class="dashboard-content rounded">
    <div class="text-center">
      <img src="@/assets/logo.png" />
    </div>

    <div v-if="editorVisible" class="editorFrame">
      <BalancingPortEditor ref="editor" @done="closeEditPort" />
    </div>

    <div class="tiles">
      <BalancingPortTile
        v-for="port in orderedPorts"
        :key="port.obj_info.name"
        :port_name="port.obj_info.name"
        :uuid="port.obj_info.uuid"
        :port="port.port"
        :protocol="port.protocol"
        :excrypt_type="port.excrypt_type"
        :web_type="port.web_type"
        :device_type="port.device_type"
        @editPort="onEditPort"
      />

      <BalancingPortTile port_name="+" @editPort="onEditPort" />
    </div>
  </div>
</template>

<script>
import { ref, nextTick } from "vue";
import store from "@/store";
import BalancingPortTile from "@/components/BalancingPortTile.vue";
import BalancingPortEditor from "@/components/BalancingPortEditor.vue";

export default {
  name: "GuardianDashboard",
  components: {
    BalancingPortTile,
    BalancingPortEditor,
  },
  setup() {
    const editorVisible = ref(false);
    return {
      editorVisible,
    };
  },
  // COMPUTED
  computed: {
    orderedPorts: function () {
      var ret = store.state.balancer.ports;
      // Probably a fancier way to do this in JS
      for (let i = 0; i < ret.length; i++) {
        for (let j = i + 1; j < ret.length; j++) {
          if (ret[i].obj_info.name > ret[j].obj_info.name) {
            var tmp = ret[i];
            ret[i] = ret[j];
            ret[j] = tmp;
          }
        }
      }
      return ret;
    },
  },
  // ON MOUNT
  mounted() {
    // Load port stubs
    store.dispatch("balancer/getPortStubs");
  },
  methods: {
    async onEditPort(uuid) {
      this.editorVisible = true;
      await nextTick();
      this.$refs.editor.writeUi(uuid);
    },
    closeEditPort() {
      this.editorVisible = false;
    },
  },
};
</script>

<style scoped>
.dashboard-content {
  width: 80%;
  margin: auto;
  border: 1px solid black;
}
.tiles {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(10rem, 1fr));
  align-items: center;
  justify-items: center;
  gap: 1rem;
  margin: 1rem;
}
.editorFrame {
  background-color: rgba(230, 230, 255, 0.9);
  position: absolute;
  z-index: 1;
  width: 78%;
  display: flex;
  align-items: center;
  left: 50%;
  transform: translate(-50%, 0);
  top: 1rem;
}
</style>

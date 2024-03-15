<template>
  <div class="editor">
    <!-- Error message on failed login -->
    <div
      v-if="error !== null && error !== undefined"
      class="text-box error-box"
    >
      {{ error }}
    </div>
    <div class="fields">
      <!-- Separator -->
      <div class="field">&nbsp;</div>
      <div class="field category form-title">
        {{ actionText }} Balancing Port
      </div>

      <!-- Name -->
      <div class="field">Name:</div>
      <div class="field">
        <input
          id="port_name"
          ref="nameRef"
          v-model="port_name"
          type="text"
          class="form-control"
          placeholder="Name"
        />
      </div>

      <!-- UUID -->
      <div v-if="uuid !== null && uuid !== undefined" class="field">UUID:</div>
      <div v-if="uuid !== null && uuid !== undefined" class="field">
        {{ uuid }}
      </div>

      <!-- Device Type -->
      <div class="field">Device Type:</div>
      <div class="field">
        <select
          v-if="uuid === null || uuid === undefined"
          id="device_type"
          v-model="device_type"
          class="form-control"
          placeholder="Device Type"
          readonly="uuid !== null && uuid !== undefined"
        >
          <option
            v-for="deviceType in deviceTypes"
            :key="deviceType.display"
            :value="deviceType.name"
            :selected="deviceType.selected"
            placeholder="Device Type"
          >
            {{ deviceType.display }}
          </option>
        </select>
        <div v-if="uuid !== null && uuid !== undefined">
          {{ deviceTypeDisplay(device_type) }}
        </div>
      </div>

      <!-- Separator -->
      <div class="field">&nbsp;</div>
      <div class="field category">Protocol Settings</div>

      <!-- Protocol -->
      <div class="field">Protocol:</div>
      <div class="field">
        <select id="protocol" v-model="protocol" class="form-control">
          <option
            v-for="protocol in protocolChoices"
            :key="protocol.display"
            :value="protocol.name"
            :selected="protocol.selected"
          >
            {{ protocol.display }}
          </option>
        </select>
      </div>

      <!-- Command Set -->
      <div v-if="commandSetShown" class="field">API:</div>
      <div v-if="commandSetShown" class="field">
        <select id="command_set" v-model="command_set" class="form-control">
          <option
            v-for="commandSet in commandSetChoices"
            :key="commandSet.display"
            :value="commandSet.name"
            :selected="commandSet.selected"
          >
            {{ commandSet.display }}
          </option>
        </select>
      </div>

      <!-- Message Size Header -->
      <div v-if="sizeHeaderShown" class="field">Size Header:</div>
      <div v-if="sizeHeaderShown" class="field">
        <select id="size_header" v-model="size_header" class="form-control">
          <option
            v-for="sizeHeader in sizeHeaderChoices"
            :key="sizeHeader.display"
            :value="sizeHeader.name"
            :selected="sizeHeader.selected"
          >
            {{ sizeHeader.display }}
          </option>
        </select>
      </div>

      <!-- International Context Header Length -->
      <div v-if="intlHeaderShown" class="field">Intl Header:</div>
      <div v-if="intlHeaderShown" class="field">
        <input
          id="intl_context_size"
          v-model="intl_context_size"
          type="number"
          class="form-control"
          placeholder="Intl Context Size"
          min="0"
          max="128"
        />
      </div>

      <!-- Separator -->
      <div class="field">&nbsp;</div>
      <div class="field category">Network Settings</div>

      <!-- Port Number -->
      <div class="field">Port:</div>
      <div class="field">
        <input
          id="port"
          ref="portRef"
          v-model="port"
          type="number"
          class="form-control"
          placeholder="Port number"
          min="1024"
          max="32767"
        />
      </div>

      <!-- Ifx -->
      <div class="field">Interface:</div>
      <div class="field">
        <select id="ifx" v-model="ifx" class="form-control">
          <option
            v-for="ifx in ifxChoices"
            :key="ifx.display"
            :value="ifx.name"
            :selected="ifx.selected"
          >
            {{ ifx.display }}
          </option>
        </select>
      </div>

      <!-- Separator -->
      <div class="field">&nbsp;</div>
      <div class="field category">TLS Settings</div>

      <!-- TLS Mode -->
      <div class="field">TLS Mode:</div>
      <div class="field">
        <select id="tls_mode" v-model="tls_mode" class="form-control">
          <option
            v-for="(mode, index) in tlsChoices"
            :key="index"
            :value="mode.name"
            :selected="mode.selected"
          >
            {{ mode.display }}
          </option>
        </select>
      </div>

      <div v-if="tlsProfileEnabled" class="field">Verify TLS:</div>
      <div v-if="tlsProfileEnabled" class="field">
        <b-form-checkbox v-model="tls_verify" value="1" />
      </div>

      <div v-if="tlsProfileEnabled" class="field">TLS Profile:</div>
      <div v-if="tlsProfileEnabled" class="field form-edit-button">
        &nbsp;
        <button
          type="button"
          class="btn btn-primary btn-block"
          @click="chooseTlsProfile()"
        >
          Choose Profile
        </button>
        {{ tlsProfileName }}
      </div>

      <!-- Separator -->
      <div class="field">&nbsp;</div>
      <div class="field category">Devices</div>

      <!-- Devices -->
      <div class="field">Devices:</div>
      <div class="field form-edit-button">
        &nbsp;
        <button
          type="button"
          class="btn btn-primary btn-block"
          @click="chooseDevices()"
        >
          Choose Devices
        </button>
        {{ deviceCount }}
      </div>

      <!-- Buttons Row -->
      <div class="field">&nbsp;</div>
      <div class="field">
        &nbsp;

        <button
          type="submit"
          class="btn btn-primary btn-block"
          @click="confirm()"
        >
          {{ buttonText }}
        </button>

        &nbsp;

        <button
          v-if="uuid !== null && uuid !== undefined"
          type="button"
          class="btn btn-danger btn-block"
          @click="deletePort()"
        >
          Delete
        </button>

        &nbsp;

        <button
          type="button"
          class="btn btn-secondary btn-block"
          @click="cancel()"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from "vue";
import { unwrapErr } from "@/utils/web";
import {
  deviceTypeDisplay,
  protocolDisplay,
  commandSetDisplay,
} from "@/utils/balancer_strings";
import {
  deviceTypeToProtocols,
  protocolToCommandSets,
  allDeviceTypes,
} from "@/utils/balancer_info";
import axios from "axios";
import store from "@/store";

export default {
  name: "BalancingPortEditor",

  // SETUP
  setup() {
    const error = ref(null);
    const uuid = ref(null);
    const port_name = ref(null);
    const port = ref(null);
    const device_type = ref(null);
    const ifx = ref("");
    const size_header = ref(0);
    const protocol = ref(null);
    const excrypt_type = ref(null);
    const command_set = ref(null);
    const web_type = ref(null);
    const intl_context_size = ref(0);
    const devices = ref([]);
    const tls_mode = ref(null);
    const tls_verify = ref(false);
    const tls_profile = ref(null);
    const tls_profile_name = ref("");
    return {
      error,
      uuid,
      port_name,
      port,
      device_type,
      ifx,
      size_header,
      protocol,
      excrypt_type,
      web_type,
      command_set,
      intl_context_size,
      devices,
      tls_mode,
      tls_verify,
      tls_profile,
      tls_profile_name,
    };
  },

  // COMPUTED
  computed: {
    actionText: function () {
      return this.uuid == undefined ? "Create" : "Modify";
    },

    // Save button text
    buttonText: function () {
      return this.uuid == undefined ? "Add" : "Save";
    },

    // Protocols
    protocolChoices: function () {
      if (!this.device_type) return [];

      var available_protocols = deviceTypeToProtocols(this.device_type);

      var ret = [];
      for (let cur_protocol of available_protocols) {
        ret.push({
          name: cur_protocol,
          display: protocolDisplay(cur_protocol),
          selected: this.protocol == cur_protocol,
        });
      }

      return ret;
    },

    // Device types
    deviceTypes: function () {
      // Can't change device type of existing port
      if (this.uuid !== undefined) {
        return [
          {
            name: this.device_type,
            display: deviceTypeDisplay(this.device_type),
            selected: true,
          },
        ];
      }

      var all_types = allDeviceTypes();

      var ret = [];
      for (let cur_type of all_types) {
        ret.push({
          name: cur_type,
          display: deviceTypeDisplay(cur_type),
          selected: this.device_type == cur_type,
        });
      }

      return ret;
    },

    // Command set / API
    commandSetShown: function () {
      return this.protocol == "Excrypt" || this.protocol == "Http";
    },

    commandSetChoices: function () {
      var all_command_sets = protocolToCommandSets(
        this.device_type,
        this.protocol,
      );

      var ret = [];
      for (let cur_set of all_command_sets) {
        ret.push({
          name: cur_set,
          display: commandSetDisplay(cur_set),
          selected: this.excrypt_type == cur_set || this.web_type == cur_set,
        });
      }

      return ret;
    },

    sizeHeaderChoices: function () {
      return [
        {
          name: "0",
          display: "Disabled",
          selected: !this.size_header,
        },
        {
          name: "2",
          display: "2-Byte Binary",
          selected: this.size_header == 2,
        },
        {
          name: "4",
          display: "4-Char Decimal",
          selected: this.size_header == 4,
        },
      ];
    },
    sizeHeaderShown: function () {
      return (
        this.protocol == "Excrypt" ||
        this.protocol == "Standard" ||
        this.protocol == "International"
      );
    },
    intlHeaderShown: function () {
      return this.protocol == "International";
    },

    // Interfaces
    // TODO: Need an endpoint to query all possible interfaces
    ifxChoices: function () {
      return [
        {
          name: "",
          display: "All",
          selected:
            !this.ifx ||
            this.ifx === null ||
            this.ifx === undefined ||
            this.ifx == "" ||
            this.ifx == "All",
        },
        {
          name: "ex0",
          display: "ex0",
          selected: this.ifx == "ex0",
        },
        {
          name: "ex1",
          display: "ex1",
          selected: this.ifx == "ex1",
        },
        {
          name: "bond0",
          display: "bond0",
          selected: this.ifx == "bond0",
        },
      ];
    },

    deviceCount: function () {
      if (!this.devices.length) return "Select devices";
      return this.devices.length;
    },

    tlsChoices: function () {
      return [
        {
          name: "NoTls",
          display: "Disabled",
          selected: !this.tls_mode || this.tls_mode == "NoTls",
        },
        {
          name: "Generated",
          display: "Generated",
          selected: this.tls_mode == "Generated",
        },
        {
          name: "TlsProfile",
          display: "TLS Profile",
          selected: this.tls_mode == "TlsProfile",
        },
      ];
    },

    tlsProfileEnabled: function () {
      return this.tls_mode == "TlsProfile";
    },

    tlsProfileName: function () {
      if (!this.tls_profile_name) return "Select a profile";
      return this.tls_profile_name;
    },
  },

  // ON MOUNT
  mounted() {
    this.focusInput();
  },

  // METHODS
  methods: {
    // Need to do this so I can use the global utility from inside the template
    deviceTypeDisplay(x) {
      return deviceTypeDisplay(x);
    },

    // Focus default input field
    focusInput() {
      this.$refs.nameRef.focus();
    },

    // INITIALIZE
    writeUi(uuid) {
      this.uuid = uuid;
      this.port = null;
      this.ifx = "";
      if (this.uuid != undefined) {
        const form = this;
        try {
          // Get balancer port stubs
          axios.get("/v1/balancingPorts/" + uuid).then(function (res) {
            form.setFields(res.data);
          });
          // Handle error
        } catch (err) {
          form.setError(err);
        }
      }
    },

    setFields(data) {
      this.error = null;
      this.port_name = data.obj_info.name;
      this.port = data.port;
      this.ifx = data["interface"];
      this.protocol = data.protocol;
      this.device_type = data.device_type;
      this.excrypt_type = data.excrypt_type;
      this.web_type = data.web_type;
      if (this.protocol == "Http") this.command_set = this.web_type;
      else this.command_set = this.excrypt_type;
      this.size_header = data.size_header;
      this.intl_context_size = data.intl_context_size;
      this.devices = data.devices;
      this.tls_mode = data.tls_params.tls_mode;
      this.tls_verify = data.tls_params.verify;
      this.tls_profile = data.tls_params.profile_uuid;

      // Get TLS profile name
      if (this.tls_profile != "") this.initTlsProfile(this.tls_profile);
    },

    readFields() {
      // TODO: Validation
      var data = {
        port: this.port,
        protocol: this.protocol,
        device_type: this.device_type,
        size_header: this.size_header,
        intl_context_size: this.intl_context_size,
      };

      data["obj_info"] = {
        name: this.port_name,
      };
      if (this.uuid != undefined) data["obj_info"]["uuid"] = this.uuid;

      if (this.protocol == "Http") data["web_type"] = this.command_set;
      if (this.protocol == "Excrypt") data["excrypt_type"] = this.command_set;
      data["interface"] = this.ifx;

      var tls_params = {
        tls_mode: this.tls_mode,
        verify: this.tls_verify,
        profile_uuid: this.tls_profile ? this.tls_profile : "",
      };
      data["tls_params"] = tls_params;

      var device = {
        device_uuid: "1234",
        role: "Primary",
        enabled: true,
      };
      data["devices"] = [device];

      return data;
    },

    initTlsProfile(uuid) {
      // TODO Need an endpoint to query this
      this.tls_profile_name = uuid;
    },

    setError(resp) {
      this.error = unwrapErr(resp);
      console.log("Upating error to: " + this.error);
    },

    // CHOOSE RELATED OBJECTS
    chooseDevices() {
      // TODO
    },

    chooseTlsProfile() {
      // TODO
    },

    // HANDLE BUTTONS
    cancel() {
      this.$emit("done");
    },

    confirm() {
      var data = this.readFields();
      const form = this;
      try {
        // POST create or update
        axios.post("/v1/balancingPorts/", data).then(function (resp) {
          data.obj_info.uuid = resp.data.uuid;
          store.dispatch("balancer/portChanged", data);
          form.$emit("done");
        });
        // Handle error
      } catch (err) {
        form.setError(err);
      }
    },

    deletePort() {
      const form = this;
      try {
        // Get balancer port stubs
        axios.delete("/v1/balancingPorts/" + this.uuid).then(function () {
          store.dispatch("balancer/removePort", form.uuid);
          form.$emit("done");
        });
        // Handle error
      } catch (err) {
        form.setError(err);
      }
    },
  },
};
</script>

<style scoped>
.editor {
  background-color: rgba(230, 230, 230, 0.9);
  border: 1px solid black;
  border-radius: 4px;
  padding-left: 1rem;
  padding-right: 1rem;
  padding-top: 1rem;
  padding-bottom: 1rem;
  margin-left: 1rem;
  margin-right: 1rem;
  margin-top: 1rem;
  margin-bottom: 1rem;
  display: block;
  width: 100%;
  height: 100%;
}
.fields {
  border: 1px solid black;
  border-radius: 4px;
  display: grid;
  width: 80%;
  grid-template-columns: 10rem 1fr;
  align-items: center;
  justify-content: left;
  justify-items: left;
  position: relative;
  margin: 0 auto;
}
.field {
  border: 1px solid white;
  width: 100%;
  height: 100%;
  padding: 0.5rem 0.5rem;
}
.category {
  font-weight: bold;
  padding: 0.5rem 0.5rem;
}
.form-edit-button {
  font-weight: bold;
}
.form-title {
  font-size: 24px;
  text-align: center;
}
</style>

<template>
  <div class="tile" @click="click">
    <div>
      {{ port_name }}
    </div>
    <div class="uuid">
      {{ uuid }}
    </div>
    <div>
      {{ portInfo }}
    </div>
  </div>
</template>

<script>
export default {
  name: "BalancingPortTile",
  props: [
    "port_name",
    "uuid",
    "port",
    "protocol",
    "excrypt_type",
    "web_type",
    "device_type",
  ],
  computed: {
    portInfo: function () {
      var ret = "";
      if (this.port != undefined) {
        ret = "Port " + this.port + "\n";
        if (this.protocol == "Standard") ret += "Standard";
        else if (this.protocol == "International") ret += "International";
        else if (this.protocol == "Excrypt") {
          if (this.excrypt_type == "HsmProduction") ret += "HSM Production";
          else if (this.excrypt_type == "HsmManagement")
            ret += "HSM Management";
          else if (this.excrypt_type == "HostApi") {
            if (this.device_type == "Kmes") ret += "KMES Host-API";
            else if (this.device_type == "Rkms") ret += "RKMS Host-API";
            else if (this.device_type == "CryptoHub")
              ret += "CryptoHub Host-API";
            else ret += "Host-API";
          } else if (this.excrypt_type == "Peering") ret += "Peering";
          else if (this.excrypt_type == "RemoteKeyLoading")
            ret += "Remote Key Loading";
          else ret += "Excrypt";
        } else if (this.protocol == "Http") {
          if (this.web_type == "RemoteDesktop") ret += "Remote Desktop";
          else if (this.web_type == "RegistrationAuthority")
            ret += "Registration Authority";
          else if (this.web_type == "GuardianConfiguration")
            ret += "Guardian Configuration";
          else if (this.web_type == "GuardianByok") ret += "Guardian BYOK";
          else if (this.web_type == "RestApi") {
            if (this.device_type == "Kmes") ret += "KMES REST API";
            else if (this.device_type == "Rkms") ret += "RKMS REST API";
            else if (this.device_type == "CryptoHub")
              ret += "CryptoHub REST API";
            else ret += "REST API";
          } else if (this.web_type == "Ocsp") ret += "OCSP";
          else if (this.web_type == "Scep") ret += "SCEP";
          else if (this.web_type == "JsonExcrypt") ret += "JSON Excrypt";
          else ret += "HTTP";
        } else {
          ret += this.protocol;
        }
      }
      return ret;
    },
  },
  methods: {
    click() {
      this.$emit("editPort", this.uuid);
    },
  },
};
</script>

<style scoped>
.tile {
  position: relative;
  margin: 3px;
  width: 11rem;
  border: 1px solid black;
  border-radius: 4px;
  padding: 0.5rem;
  text-align: center;
  white-space: pre-wrap;
  word-wrap: break-word;
}
.tile:hover {
  background-color: rgb(230, 230, 255);
  box-shadow: 5px 5px 15px rgba(145, 92, 182, 0.4);
  cursor: pointer;
}
.uuid {
  font-size: 6px;
}
.tile:hover > .uuid {
  color: rgb(60, 179, 113);
}
</style>

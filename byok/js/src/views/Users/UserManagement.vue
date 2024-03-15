<template>
  <div class="management-page no-border-radius-bottom">
    <add-user v-if="show === 'add'" id="modal" @closeModal="close" />

    <change-password-modal
      v-if="show === 'password'"
      id="modal"
      :username="username"
      :session-id="currentCluster.session.id"
      @closeModal="close"
    />

    <delete-user
      v-if="show === 'delete'"
      id="modal"
      :username="username"
      @closeModal="close"
    />

    <modal-u2f-management
      v-if="show === 'token'"
      :username="username"
      @closeModal="close"
    />

    <header>
      <p>User Management</p>
      <button
        class="add-user-button button button-wide"
        :disabled="!canAddIdentity"
        @click="updateShow('add')"
      >
        <i class="fa fa-plus" /> Add user
      </button>
      <close-button @click.prevent="$emit('close')" />
    </header>

    <table class="user-table">
      <thead>
        <tr>
          <th class="user-table-user">User</th>
          <th class="user-table-status">Status</th>
          <th class="user-table-u2f">U2F Token</th>
          <th class="user-table-options"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.name">
          <td :title="user.name">{{ user.name }}</td>
          <td>
            <div :class="status(user).class">
              {{ status(user).text }}
            </div>
          </td>
          <td>
            <div :class="u2fStatus(user).class">
              {{ u2fStatus(user).text }}
            </div>
          </td>
          <td>
            <button
              class="button blue-button"
              data-bs-toggle="dropdown"
              :disabled="!user.manageable"
            >
              <i class="fa fa-caret-down" />
            </button>

            <ul class="dropdown-menu">
              <li v-if="canChangePassword">
                <button
                  class="dropdown-item-custom"
                  @click="updateShow('password', user)"
                >
                  <i class="fa fa-asterisk" />
                  Change password
                </button>
              </li>

              <li v-if="canChangeU2F && isActiveUser(user)">
                <button
                  class="dropdown-item-custom"
                  @click="updateShow('token', user)"
                >
                  <i class="fa fa-lock" />
                  U2F
                </button>
              </li>

              <li v-if="canDeleteIdentity">
                <button
                  class="dropdown-item-custom"
                  @click="updateShow('delete', user)"
                >
                  <i class="fa fa-trash" />
                  Delete user
                </button>
              </li>
            </ul>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import CloseButton from "@/components/CloseButton.vue";
import AddModal from "@/views/Users/AddModal.vue";
import ChangePasswordModal from "@/views/Users/ChangePasswordModal.vue";
import DeleteModal from "@/views/Users/DeleteModal.vue";
import ModalU2fManagement from "@/components/ModalU2fManagement.vue";

export default {
  name: "UserManagement",
  components: {
    "add-user": AddModal,
    "change-password-modal": ChangePasswordModal,
    "delete-user": DeleteModal,
    "close-button": CloseButton,
    "modal-u2f-management": ModalU2fManagement,
  },
  inject: ["getSessionId"],
  props: {
    currentCluster: Object,
  },
  data: function () {
    let permissions = this.currentCluster.session.permissions;
    return {
      show: null,
      username: null,
      users: [],
      canAddIdentity: !!permissions["Identity:Add"],
      canChangePKIAuth: !!permissions["Identity:Change PKI Auth"],
      canChangePassword: !!permissions["Identity:Change Password"],
      canChangeU2F: !!permissions["Identity:Change U2F"],
      canDeleteIdentity: !!permissions["Identity:Delete"],
      canModifyIdentity: !!permissions["Identity:Modify"],
    };
  },
  watch: {
    show: function (value) {
      if (!value) {
        this.fillUsers();
      }
    },
  },
  mounted: function () {
    this.fillUsers();
  },
  methods: {
    isActiveUser: function (user) {
      return this.currentCluster.session.identities.includes(user.name);
    },
    status: function (user) {
      let isSelf = this.isActiveUser(user);
      if (isSelf) {
        return {
          text: "Active",
          class: "isactive",
        };
      }
      if (user.locked) {
        return {
          text: "Locked",
          class: "isdisabled",
        };
      }
      return { text: "Inactive", class: "isinactive" };
    },
    u2fStatus: function (user) {
      if (user.u2fEnabled) {
        return {
          text: "Enabled",
          class: "isactive",
        };
      } else {
        return {
          text: "Disabled",
          class: "isdisabled",
        };
      }
    },
    fillUsers: function () {
      let url = `/clusters/sessions/${this.getSessionId()}/identities`;
      this.$httpV2
        .get(url, { errorContextMessage: "Failed to fetch identity list" })
        .then((data) => {
          this.users = data.identities;
        });
    },
    close: function () {
      this.show = null;
    },
    updateShow: function (value, user) {
      if (user) {
        this.username = user.name;
      }
      this.show = this.show === value ? null : value;
    },
  },
};
</script>

<style scoped>
.no-border-radius-bottom {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}

.add-user-button {
  padding-top: 3px;
  padding-bottom: 3px;
  margin-right: 0.5rem;
}

.isactive,
.isinactive,
.isdisabled {
  border-radius: 4px;
  padding: 0.5rem;
}

.isactive {
  background-color: #ecf5ec;
  border: 1px solid #c6dfca;
  color: #769976;
}

.isinactive {
  background-color: #f9f9f9;
  border: 1px solid var(--border-color);
}

.isdisabled {
  background-color: #f5ecec;
  border: 1px solid #dfc6c6;
  color: #997676;
}

.user-table {
  text-align: center;
  border-collapse: collapse;
  margin: -1px;
  table-layout: fixed;
  width: calc(100% + 2px);
}

.user-table thead {
  background: linear-gradient(
    180deg,
    rgba(249, 249, 249, 1) 0%,
    rgba(241, 241, 241, 1) 35%,
    rgba(238, 238, 238, 1) 100%
  );
}

.user-table tbody tr:nth-child(2n + 1) {
  background-color: white;
}

.user-table tbody tr:nth-child(2n) {
  background-color: #f9f9f9;
}

.user-table th {
  font-weight: 500;
}

.user-table td {
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-table td,
th {
  border: 1px solid #d2d6de;
  padding: 0.5rem;
}

.user-table th:first-child {
  text-align: left;
}

.user-table td:first-child {
  text-align: left;
}

.user-table-status,
.user-table-u2f {
  width: 100px;
}
.user-table-options {
  width: 60px;
}
</style>

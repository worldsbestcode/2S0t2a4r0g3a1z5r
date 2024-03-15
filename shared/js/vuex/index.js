import AuthModule from "$shared/vuex/auth.js";
import NotificationsModule from "$shared/vuex/notifications.js";
import ProfilesModule from "$shared/vuex/profiles.js";
import SharedModule from "$shared/vuex/shared.js";

export default {
  auth: AuthModule,
  profiles: ProfilesModule,
  notifications: NotificationsModule,
  shared: SharedModule,
};

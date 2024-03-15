import { createVuetify } from "vuetify";
import * as components from "vuetify/lib/components";
import * as directives from "vuetify/lib/directives";
import { aliases, mdi } from "vuetify/iconsets/mdi";

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: "mdi",
    aliases,
    sets: mdi,
  },
  theme: {
    defaultTheme: "light",
    themes: {
      light: {
        dark: false,
        variables: {},
        colors: {
          background: "#FFFFFF",
          primary: "#215AB0",
          secondary: "#EAEAEA",
          error: "#FF0000",
          info: "#2196F3",
          success: "#4CAF50",
          warning: "#F57C00",
          systemBar: "#454545",
          systemBarText: "#FFFFFF",
          headerTop: "#F2F2F2",
          headerBottom: "#E1E1E1",
          action: "#215AB0",
          actionText: "#E0E0E0",
          formFieldForeground: "#F2F2F2",
          formFieldBackground: "#FFFFFF",
          weakText: "#474747",
          cardBorder: "#B5B5B5",
          red: "#911211",
          fadedRed: "#885153",
          disabled: "#CCCCCC",
          disabled2: "#F9F9F9",
          offwhiteLight: "FFFFFF",
          offwhiteDark: "E8E8E8",
          greyText: "#A4A4A4",
          blackText: "#181818",
        },
      },
    },
  },
});

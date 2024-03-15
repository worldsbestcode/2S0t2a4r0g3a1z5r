import axios from "axios";

const sharedAxios = axios.create();
sharedAxios.defaults.xsrfCookieName = "FXSRF-TOKEN";
sharedAxios.defaults.xsrfHeaderName = "X-FXSRF-TOKEN";

export default sharedAxios;

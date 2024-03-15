import axios from "axios";
import { useToast } from "vue-toastification";
import { unwrapErr } from "$shared/utils/web";

const toast = useToast();

export function download(filename) {
  const config = {
    params: {
      file: filename,
    },
    responseType: "blob",
  };
  axios
    .get("/rd/v1/files/download", config)
    .then((response) => {
      let a = document.createElement("a");
      let blobUrl = window.URL.createObjectURL(response.data);
      a.href = blobUrl;
      a.download = filename;
      a.click();
      window.URL.revokeObjectURL(blobUrl);
    })
    .catch((error) => {
      toast.error(unwrapErr(error));
    });
}

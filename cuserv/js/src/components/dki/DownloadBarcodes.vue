<template>
  <div class="barcode-settings">
    <ChcSpinner
      v-model:modelValue="barcodeSettings.width"
      title="Width"
      :min="0"
      :max="3"
    />
    <div class="spacer" />
    <ChcSpinner
      v-model:modelValue="barcodeSettings.height"
      title="Height"
      :min="0"
      :max="200"
      :step="10"
    />
  </div>
  <div v-for="barcode in barcodes" :key="barcode.data" class="barcode">
    <BarCode
      :ref="(el) => (barcodeElements[barcode.data] = el)"
      :width="barcodeSettings.width"
      :height="barcodeSettings.height"
      :text-margin="barcodeSettings.textMargin"
      :font-size="barcodeSettings.fontSize"
      :display-text="barcode.title"
      :barcode-text="barcode.data"
    />
  </div>
  <div class="modal-button-bottom">
    <button class="button-secondary" @click="emit('cancel')">CANCEL</button>
    <button class="button-primary" @click="downloadBarcodes">DOWNLOAD</button>
  </div>
</template>

<script setup>
import { PDFDocument } from "pdf-lib";
import { defineEmits, defineProps, reactive, ref } from "vue";

import ChcSpinner from "$shared/components/ChcSpinner.vue";

import BarCode from "@/components/dki/BarCode.vue";

const emit = defineEmits(["cancel", "downloaded"]);
defineProps({
  barcodes: {
    type: Array,
    required: true,
  },
});

const barcodeElements = ref({});
const barcodeSettings = reactive({
  textMargin: 20,
  width: 1.5,
  height: 80,
  fontSize: 12,
});

function download(bytes) {
  const blob = new Blob([bytes], { type: "application/pdf" });
  const blobUrl = URL.createObjectURL(blob);

  let a = document.createElement("a");
  a.href = blobUrl;
  a.download = "barcode.pdf";
  a.click();
  window.URL.revokeObjectURL(blobUrl);
}

async function downloadBarcodes() {
  const pdfDoc = await PDFDocument.create();
  for (const key in barcodeElements.value) {
    let canvas = barcodeElements.value[key].getBarcode();

    const barcodeImage = await pdfDoc.embedPng(
      canvas.toDataURL("image/png").split(",")[1],
    );

    const page = pdfDoc.addPage([barcodeImage.width, barcodeImage.height]);
    page.drawImage(barcodeImage, {
      x: 0,
      y: 0,
      width: barcodeImage.width,
      height: barcodeImage.height,
    });
  }

  const pdfBytes = await pdfDoc.save();
  download(pdfBytes);
  emit("downloaded");
}
</script>

<style scoped>
.barcode-settings {
  display: flex;
  margin-bottom: 1rem;
}

.barcode {
  min-width: 800px;
  border-bottom: 1px solid var(--border-color);
  text-align: center;
  margin-bottom: 2rem;
}

.modal-button-bottom {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  justify-content: space-between;
}

.spacer {
  width: 20px;
}
</style>

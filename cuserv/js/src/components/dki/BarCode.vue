<template>
  <canvas ref="barcode" />
</template>

<script setup>
import JsBarcode from "jsbarcode";
import { defineExpose, defineProps, onMounted, ref, watch } from "vue";

const props = defineProps({
  width: {
    type: Number,
    default: 2,
  },
  height: {
    type: Number,
    default: 100,
  },
  displayText: {
    type: String,
    required: true,
  },
  barcodeText: {
    type: String,
    required: true,
  },
  textMargin: {
    type: Number,
    default: 20,
  },
  fontSize: {
    type: Number,
    default: 20,
  },
});

const barcode = ref(null);

function createBarcode() {
  JsBarcode(barcode.value, props.barcodeText, {
    format: "code128",
    width: props.width,
    height: props.height,
    text: props.displayText,
    textMargin: props.textMargin,
    fontSize: props.fontSize,
    flat: true,
  });
}

function getBarcode() {
  return barcode.value;
}

defineExpose({
  getBarcode,
});

onMounted(createBarcode);
watch(props, () => {
  createBarcode();
});
</script>

<style scoped></style>

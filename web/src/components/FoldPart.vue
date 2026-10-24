<script setup>
import { onMounted, ref } from "vue";

const props = defineProps({
  title: { type: String, required: true },
  open: { type: Boolean, default: false },
});

const root = ref(null);

onMounted(() => {
  if (root.value) root.value.open = !!props.open;
});
</script>

<template>
  <details ref="root" class="item-part fold-part">
    <summary>{{ title }}</summary>
    <slot />
  </details>
</template>

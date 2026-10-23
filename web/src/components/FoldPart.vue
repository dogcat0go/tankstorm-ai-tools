<script setup>
import { onMounted, ref } from "vue";

const props = defineProps({
  title: { type: String, required: true },
  open: { type: Boolean, default: true },
});

const root = ref(null);

onMounted(() => {
  if (root.value && !props.open) root.value.open = false;
});
</script>

<template>
  <details ref="root" class="item-part fold-part" open>
    <summary>{{ title }}</summary>
    <slot />
  </details>
</template>

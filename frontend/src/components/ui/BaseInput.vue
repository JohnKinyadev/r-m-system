<template>
  <div class="flex flex-col gap-1">
    <label v-if="label" class="text-sm font-medium text-gray-700">
      {{ label }} <span v-if="required" class="text-red-500">*</span>
    </label>
    <component
      :is="type === 'textarea' ? 'textarea' : type === 'select' ? 'select' : 'input'"
      v-bind="inputAttrs"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      @change="type === 'select' && $emit('update:modelValue', $event.target.value)"
      class="input-field"
      :class="{ 'border-red-400': error }"
    >
      <slot v-if="type === 'select'" />
    </component>
    <p v-if="error" class="text-xs text-red-500">{{ error }}</p>
    <p v-if="hint && !error" class="text-xs text-gray-400">{{ hint }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  label: String,
  type: { type: String, default: 'text' },
  placeholder: String,
  required: Boolean,
  error: String,
  hint: String,
})

defineEmits(['update:modelValue'])

const inputAttrs = computed(() => ({
  type: props.type !== 'textarea' && props.type !== 'select' ? props.type : undefined,
  placeholder: props.placeholder,
  required: props.required,
}))
</script>

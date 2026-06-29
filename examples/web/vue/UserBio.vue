<template>
  <article>
    <h1>User bio</h1>
    <div v-html="bio"></div>
  </article>
</template>

<script>
export default {
  props: {
    bio: {
      type: String,
      required: true
    }
  }
};
</script>

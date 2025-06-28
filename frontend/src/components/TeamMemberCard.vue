<template>
  <div class="team-member-card">
    <Avatar
      :relativeUrl="member.avatar_url"
      :name="member.name"
      :alt="member.name"
      class="team-avatar"
    />
    <h3 class="team-member-name">{{ member.name }}</h3>
    <p class="team-member-role">{{ member.role }}</p>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';
import Avatar from './Avatar.vue';


const props = defineProps({
  member: {
    type: Object,
    required: true
  }
});

</script>

<style scoped>
.team-member-card {
    background: transparent;
    border: 2px solid var(--border-color);
    padding: 1.5rem;
    cursor: pointer;
    transition: background-color 0.2s, border-color 0.2s, box-shadow 0.2s;
    box-shadow: 5px 5px 0 0 var(--border-color);
    height: 100%;
}
.team-member-card:hover {
    background-color: var(--secondary-bg-color);
    border-color: var(--primary-accent-color);
    box-shadow: 5px 5px 0 0 var(--primary-accent-color);
}
:deep(.team-avatar) {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
    margin-bottom: 1rem;
    border: 2px solid var(--primary-accent-color);
}

.team-avatar {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
    margin-bottom: 1rem;
    border: 2px solid var(--primary-accent-color);
}
.team-member-name {
    margin: 0.5rem 0;
    font-size: 1.2rem;
    color: var(--main-text-color);
}
.team-member-role {
    font-size: 0.9rem;
    color: var(--link-color);
}
</style>
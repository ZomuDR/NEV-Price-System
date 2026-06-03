<script setup>

</script>

<template>
  <router-view/>
</template>

<style>
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f7fa;
  --bg-card: #ffffff;
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --border-color: #e4e7ed;
  --shadow-color: rgba(0, 0, 0, 0.1);
}

:root.dark {
  --bg-primary: #1a1a1a;
  --bg-secondary: #2d2d2d;
  --bg-card: #2d2d2d;
  --text-primary: #e5e5e5;
  --text-secondary: #a0a0a0;
  --border-color: #404040;
  --shadow-color: rgba(0, 0, 0, 0.3);
}

html.dark body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

html.dark .system-container {
  background: var(--bg-secondary);
}

html.dark .header {
  background: linear-gradient(135deg, #1a3a2b 0%, #1a3a2b 100%) !important;
}

html.dark .sidebar {
  background: var(--bg-card);
}

html.dark .menu-item {
  color: var(--text-primary);
}

html.dark .menu-item:hover {
  background: rgba(0, 200, 83, 0.1);
}

html.dark .menu-item.active {
  background: rgba(0, 200, 83, 0.15);
  color: #00c853;
}

html.dark .section-title {
  color: var(--text-secondary);
  border-bottom-color: var(--border-color);
}

html.dark .sidebar-footer {
  border-top-color: var(--border-color);
}

html.dark .theme-toggle {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

html.dark .content-area {
  background: var(--bg-secondary);
}

html.dark .breadcrumb {
  color: var(--text-secondary);
  background: var(--bg-card);
  border-bottom-color: var(--border-color);
}

html.dark .el-breadcrumb__item {
  color: var(--text-secondary);
}

html.dark .el-breadcrumb__inner {
  color: var(--text-secondary) !important;
}

html.dark .el-breadcrumb__separator {
  color: var(--text-secondary) !important;
}

html.dark .page-content {
  background: var(--bg-secondary);
}

html.dark .current-page {
  color: var(--text-secondary);
}

html.dark .username {
  color: var(--text-primary);
}
</style>

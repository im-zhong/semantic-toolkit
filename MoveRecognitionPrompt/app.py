"""
科技文献语义计算工具库

功能：提供多种科技文献分析工具，包括语步识别、自动分类、关键词识别等
前端：使用 Gradio + 自定义 CSS 实现
"""

import json
import gradio as gr
from services.move_recognition import (
    analyze_zh_abstract, analyze_en_abstract, analyze_zh_project,
    EXAMPLE_ZH_ABSTRACT, EXAMPLE_EN_ABSTRACT, EXAMPLE_ZH_PROJECT,
    ZH_ABSTRACT_MOVE_LABELS, EN_ABSTRACT_MOVE_LABELS, ZH_PROJECT_MOVE_LABELS
)

CUSTOM_CSS = """
:root {
  --primary: #2563ff;
  --primary-dark: #1a49e8;
  --primary-light: #5ca9ff;
  --bg-soft: #f4f8ff;
  --panel: rgba(255,255,255,0.76);
  --border: rgba(187, 208, 255, 0.85);
  --text-main: #1e2b50;
  --text-sub: #667799;
  --shadow: 0 20px 45px rgba(37, 99, 255, 0.12);
}

.gradio-container {
  max-width: 100% !important;
  background: linear-gradient(180deg, #f7faff 0%, #eef4ff 100%);
  color: var(--text-main);
  font-family: "Microsoft YaHei", "PingFang SC", "Helvetica Neue", Arial, sans-serif;
}

/* 页面整体布局 */
.page-wrapper {
  max-width: 1500px;
  margin: 0 auto;
  padding: 20px 24px 28px;
  box-sizing: border-box;
}

.top-header {
  height: 84px;
  border-radius: 0 0 22px 22px;
  background: linear-gradient(90deg, #dce8fa 0%, #eef4ff 52%, #ddeaff 100%);
  border: 1px solid rgba(255,255,255,0.85);
  box-shadow: 0 10px 30px rgba(102, 147, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  margin-bottom: 22px;
  width: 100%;
  box-sizing: border-box;
}

/* 主内容区域grid布局 */
.main-content-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  min-height: 800px;
}

/* 侧边栏 */
.sidebar-wrapper {
  width: 320px;
  flex-shrink: 0;
}

/* 内容区域 */
.content-wrapper {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 主内容行 - 确保与header对齐 */
.content-row {
  max-width: 1500px !important;
  margin: 0 auto !important;
  padding: 0 24px !important;
  display: flex !important;
  gap: 24px !important;
}

.sidebar-col {
  min-width: 320px !important;
  max-width: 320px !important;
  width: 320px !important;
  flex: none !important;
}

.main-col {
  flex: 1 !important;
  min-width: 0 !important;
}

.brand-wrap {
  display: flex;
  align-items: center;
  gap: 16px;
}

.brand-icon {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #ffffff 0%, #eef4ff 38%, #d9e6ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
  font-size: 30px;
  font-weight: 800;
  box-shadow: 0 8px 18px rgba(37, 99, 255, 0.14);
}

.brand-title {
  font-size: 18px;
  font-weight: 800;
  line-height: 1.25;
}

.brand-subtitle {
  color: var(--text-sub);
  font-size: 14px;
  margin-top: 2px;
}

.header-center-title {
  font-size: 26px;
  font-weight: 800;
  color: #1f3d7a;
  letter-spacing: 1px;
}

.header-welcome {
  min-width: 430px;
  height: 42px;
  border-radius: 999px;
  background: rgba(255,255,255,0.88);
  border: 1px solid rgba(231,238,255,1);
  display: flex;
  align-items: center;
  padding: 0 20px;
  color: #5f6f96;
  font-size: 14px;
}

.main-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  min-height: 800px;
}

.sidebar {
  border-radius: 24px;
  background: linear-gradient(180deg, #dfe9ff 0%, #eef4ff 100%);
  border: 1px solid rgba(255,255,255,0.9);
  padding: 20px;
  box-shadow: 0 14px 32px rgba(126, 164, 255, 0.12);
  overflow-y: auto;
  height: fit-content;
}

.sidebar-hero {
  border-radius: 20px;
  padding: 20px;
  color: white;
  background: linear-gradient(135deg, #3d87ff 0%, #235dff 55%, #1f4ced 100%);
  box-shadow: 0 16px 32px rgba(37, 99, 255, 0.25);
  margin-bottom: 20px;
}

.sidebar-hero h3 {
  font-size: 18px;
  margin: 0 0 6px 0;
  color: white;
}

.sidebar-hero p {
  margin: 0;
  font-size: 13px;
  color: rgba(255,255,255,0.88);
}

/* 导航样式 */
.nav-tree {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-group {
  background: rgba(255,255,255,0.6);
  border-radius: 16px;
  padding: 12px;
}

.nav-parent {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 8px;
}

.nav-parent-icon {
  font-size: 18px;
}

.nav-children {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-left: 8px;
}

.nav-child {
  padding: 10px 14px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-sub);
  background: transparent;
  border: none;
  width: 100%;
  text-align: left;
}

.nav-child:hover {
  background: rgba(255,255,255,0.8);
  color: var(--text-main);
}

.nav-child.active {
  background: rgba(37, 99, 255, 0.15);
  color: var(--primary);
  font-weight: 600;
}

/* 内容区域 */
.content-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-container {
  display: none;
}

.page-container.active {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  background: rgba(255,255,255,0.85);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(195, 214, 255, 0.8);
  box-shadow: 0 8px 20px rgba(90, 126, 216, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(90, 126, 216, 0.12);
}

.stat-card-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-bottom: 12px;
}

.stat-card-icon.blue { background: linear-gradient(135deg, #e8f0ff 0%, #d4e4ff 100%); color: var(--primary); }
.stat-card-icon.green { background: linear-gradient(135deg, #e8fff0 0%, #d4ffe4 100%); color: #22c55e; }
.stat-card-icon.orange { background: linear-gradient(135deg, #fff4e8 0%, #ffe8d4 100%); color: #f97316; }
.stat-card-icon.purple { background: linear-gradient(135deg, #f4e8ff 0%, #e8d4ff 100%); color: #a855f7; }

.stat-card-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--text-main);
  line-height: 1;
  margin-bottom: 6px;
}

.stat-card-label {
  font-size: 13px;
  color: var(--text-sub);
}

.stat-card-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  margin-top: 10px;
}

.stat-card-trend.up { color: #22c55e; }
.stat-card-trend.down { color: #ef4444; }

/* 图表区域 */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin: 28px 0;
}

.chart-card {
  background: rgba(255,255,255,0.85);
  border-radius: 20px;
  padding: 24px;
  border: 1px solid rgba(195, 214, 255, 0.8);
  box-shadow: 0 8px 20px rgba(90, 126, 216, 0.08);
}

.chart-card-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 16px 0;
}

.chart-container {
  position: relative;
  height: 160px;
}

/* 工具介绍卡片 */
.tool-intro-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
  margin-bottom: 24px;
}

.tool-intro-card {
  background: rgba(255,255,255,0.85);
  border-radius: 20px;
  padding: 24px;
  border: 1px solid rgba(195, 214, 255, 0.8);
  box-shadow: 0 8px 24px rgba(90, 126, 216, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;
}

.tool-intro-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(90, 126, 216, 0.12);
}

.tool-intro-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.tool-intro-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  background: linear-gradient(135deg, #e8f0ff 0%, #d4e4ff 100%);
}

.tool-intro-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0;
}

.tool-intro-desc {
  font-size: 13px;
  color: var(--text-sub);
  line-height: 1.6;
  margin: 0 0 12px 0;
}

.tool-intro-features {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tool-intro-tag {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  background: linear-gradient(180deg, #f5f9ff 0%, #ebf2ff 100%);
  color: var(--primary);
}

/* 功能页面容器 */
.func-page {
  display: none;
}

.func-page.active {
  display: block;
}

/* 页面头部 */
.func-header {
  background: linear-gradient(135deg, #3d87ff 0%, #235dff 55%, #1f4ced 100%);
  border-radius: 20px;
  padding: 28px 32px;
  margin-bottom: 24px;
  color: white;
  box-shadow: 0 16px 40px rgba(37, 99, 255, 0.25);
}

.func-header h1 {
  font-size: 26px;
  font-weight: 800;
  margin: 0 0 8px 0;
}

.func-header-desc {
  font-size: 15px;
  opacity: 0.92;
  line-height: 1.6;
  margin: 0;
}

.func-header-tags {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.func-tag {
  background: rgba(255,255,255,0.2);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

/* 面包屑 */
.breadcrumb {
  font-size: 13px;
  color: rgba(255,255,255,0.8);
  margin-bottom: 12px;
}

.breadcrumb span {
  color: white;
  font-weight: 500;
}

/* 测试区域 */
.test-section {
  background: rgba(255,255,255,0.9);
  border-radius: 20px;
  padding: 28px;
  margin-bottom: 24px;
  border: 1px solid rgba(195, 214, 255, 0.8);
  box-shadow: 0 8px 24px rgba(90, 126, 216, 0.08);
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title::before {
  content: "";
  width: 4px;
  height: 20px;
  background: linear-gradient(180deg, #3d87ff, #235dff);
  border-radius: 2px;
}

/* 输入区域样式 */
.input-textarea {
  width: 100%;
  min-height: 180px;
  border: 2px solid #d6e4ff !important;
  border-radius: 16px !important;
  padding: 16px !important;
  font-size: 14px !important;
  line-height: 1.8 !important;
  resize: vertical;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%) !important;
  color: var(--text-main);
  font-family: inherit;
  box-sizing: border-box;
}

.input-textarea:focus {
  outline: none;
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgba(37, 99, 255, 0.1);
}

.input-textarea::placeholder {
  color: #9ca3af;
}

/* 按钮行 */
.btn-row {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.btn-primary {
  height: 48px;
  padding: 0 28px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #3680ff 0%, #245cff 60%, #2250f2 100%);
  color: white;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(37, 99, 255, 0.24);
  transition: all 0.2s;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 28px rgba(37, 99, 255, 0.32);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  height: 48px;
  padding: 0 24px;
  border: 2px solid #d6e4ff;
  border-radius: 12px;
  background: rgba(255,255,255,0.9);
  color: var(--primary);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: rgba(37, 99, 255, 0.05);
  border-color: var(--primary);
}

/* 结果展示区域 */
.result-section {
  margin-top: 24px;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.result-card {
  background: rgba(255,255,255,0.9);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(195, 214, 255, 0.8);
  box-shadow: 0 4px 12px rgba(90, 126, 216, 0.06);
}

.result-card.full-width {
  grid-column: 1 / -1;
}

.result-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.result-card-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.result-card-icon.bg { background: linear-gradient(135deg, #e0f2fe, #bae6fd); color: #0284c7; }
.result-card-icon.pu { background: linear-gradient(135deg, #fef3c7, #fde68a); color: #d97706; }
.result-card-icon.me { background: linear-gradient(135deg, #d1fae5, #a7f3d0); color: #059669; }
.result-card-icon.re { background: linear-gradient(135deg, #ede9fe, #ddd6fe); color: #7c3aed; }
.result-card-icon.co { background: linear-gradient(135deg, #fce7f3, #fbcfe8); color: #db2777; }
.result-card-icon.basis { background: linear-gradient(135deg, #e0f2fe, #bae6fd); color: #0284c7; }
.result-card-icon.obj { background: linear-gradient(135deg, #fef3c7, #fde68a); color: #d97706; }
.result-card-icon.cont { background: linear-gradient(135deg, #d1fae5, #a7f3d0); color: #059669; }
.result-card-icon.app { background: linear-gradient(135deg, #ede9fe, #ddd6fe); color: #7c3aed; }
.result-card-icon.exp { background: linear-gradient(135deg, #fce7f3, #fbcfe8); color: #db2777; }
.result-card-icon.val { background: linear-gradient(135deg, #fef3c7, #fde68a); color: #f59e0b; }

.result-card-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
}

.result-card-content {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-main);
}

.result-item {
  padding: 8px 12px;
  margin: 4px 0;
  background: #f8faff;
  border-radius: 8px;
  border-left: 3px solid var(--primary);
}

.result-empty {
  color: var(--text-sub);
  font-style: italic;
}

/* JSON展示 */
.json-display {
  background: #1e293b;
  border-radius: 12px;
  padding: 16px;
  font-family: "JetBrains Mono", "Fira Code", monospace;
  font-size: 12px;
  color: #e2e8f0;
  overflow-x: auto;
  line-height: 1.6;
  max-height: 300px;
  overflow-y: auto;
}

/* 表格样式 */
.table-card {
  background: rgba(255,255,255,0.85);
  border-radius: 20px;
  padding: 24px;
  border: 1px solid rgba(195, 214, 255, 0.8);
  box-shadow: 0 8px 24px rgba(90, 126, 216, 0.08);
}

.table-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 16px 0;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 12px 14px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-sub);
  background: #f8faff;
  border-radius: 8px;
}

.data-table th:first-child { border-radius: 8px 0 0 8px; }
.data-table th:last-child { border-radius: 0 8px 8px 0; }

.data-table td {
  padding: 14px;
  font-size: 13px;
  color: var(--text-main);
  border-bottom: 1px solid #eef2ff;
}

.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: #f8faff; }

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
}

.status-badge.success { background: #dcfce7; color: #16a34a; }
.status-badge.pending { background: #fef3c7; color: #d97706; }
.status-badge.failed { background: #fee2e2; color: #dc2626; }

.module-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  background: linear-gradient(180deg, #f5f9ff 0%, #ebf2ff 100%);
  color: var(--primary);
}

/* 分页样式 */
.pagination-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
}

.pagination-btn {
  min-width: 40px !important;
  height: 36px !important;
  border-radius: 8px !important;
  border: 1px solid #d6e4ff !important;
  background: rgba(255,255,255,0.9) !important;
  color: #667799 !important;
  font-size: 14px !important;
  font-weight: 500 !important;
}

.pagination-btn:hover {
  background: rgba(37, 99, 255, 0.1) !important;
  color: var(--primary) !important;
  border-color: var(--primary) !important;
}

.pagination-btn.active {
  background: #2563ff !important;
  color: white !important;
  border-color: #2563ff !important;
}

.pagination-info {
  font-size: 13px;
  color: #667799;
  padding: 0 12px;
}

.pagination-row {
  display: flex !important;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 8px;
}

.pagination-row .pagination-btn {
  min-width: 100px !important;
  height: 40px !important;
  border-radius: 10px !important;
  border: 1px solid #d6e4ff !important;
  background: rgba(255,255,255,0.95) !important;
  color: #667799 !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  cursor: pointer;
}

.pagination-row .pagination-btn:hover {
  background: rgba(37, 99, 255, 0.1) !important;
  color: #2563ff !important;
  border-color: #2563ff !important;
}

@media (max-width: 1280px) {
  .main-grid { grid-template-columns: 1fr; }
  .header-center-title { display: none; }
  .header-welcome { min-width: 240px; }
  .tool-intro-grid { grid-template-columns: repeat(2, 1fr); }
}

/* 功能页面容器 - 默认隐藏 */
.func-page-container {
  display: none;
}

/* 默认隐藏功能页面 */
#zh-abstract-page,
#en-abstract-page,
#zh-project-page,
.func-page-container {
  display: none !important;
}

/* 显示状态 */
#zh-abstract-page.show,
#en-abstract-page.show,
#zh-project-page.show,
.func-page-container.show {
  display: flex !important;
  flex-direction: column;
}

/* Gradio Textbox 样式 */
.input-textarea textarea {
  width: 100% !important;
  min-height: 180px !important;
  border: 2px solid #d6e4ff !important;
  border-radius: 16px !important;
  padding: 16px !important;
  font-size: 14px !important;
  line-height: 1.8 !important;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%) !important;
  font-family: inherit !important;
}

/* ==================== ModelScope 风格功能页面 ==================== */

/* Hero 区域 */
.ms-hero {
  border-radius: 28px;
  overflow: hidden;
  margin-bottom: 24px;
  border: 1px solid rgba(255,255,255,0.25);
}

.ms-hero-grid {
  display: grid;
  grid-template-columns: 1.3fr 0.7fr;
  gap: 0;
}

.ms-hero-main {
  padding: 32px;
  color: #fff;
  background: radial-gradient(circle at top left, rgba(255,255,255,0.18), transparent 30%),
              linear-gradient(135deg, #5fa8ff 0%, #3b82ff 38%, #1f5fff 100%);
}

.ms-hero-main.en {
  background: radial-gradient(circle at top left, rgba(255,255,255,0.18), transparent 30%),
              linear-gradient(135deg, #34d399 0%, #10b981 38%, #059669 100%);
}

.ms-hero-main.project {
  background: radial-gradient(circle at top left, rgba(255,255,255,0.18), transparent 30%),
              linear-gradient(135deg, #a78bfa 0%, #8b5cf6 38%, #7c3aed 100%);
}

.ms-hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 12px;
}

.ms-hero-tag {
  padding: 4px 12px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.25);
  background: rgba(255,255,255,0.14);
}

.ms-hero-title {
  font-size: 40px;
  font-weight: 700;
  margin: 0 0 16px 0;
  line-height: 1.15;
}

.ms-hero-desc {
  font-size: 16px;
  line-height: 1.75;
  color: rgba(255,255,255,0.9);
  max-width: 820px;
}

.ms-hero-buttons {
  margin-top: 32px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.ms-hero-stats {
  margin-top: 28px;
  display: grid;
  gap: 12px;
  max-width: 760px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.ms-hero-stat {
  padding: 16px;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.25);
  background: rgba(255,255,255,0.14);
  backdrop-filter: blur(8px);
}

.ms-hero-stat-k {
  font-size: 12px;
  color: rgba(255,255,255,0.8);
}

.ms-hero-stat-v {
  margin-top: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #fff;
}

.ms-hero-side {
  padding: 24px;
  background: #fff;
}

.ms-mini-card {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: #f8fafc;
  margin-bottom: 16px;
}

.ms-mini-card:last-child {
  margin-bottom: 0;
}

.ms-mini-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.ms-feature-list {
  margin-top: 16px;
  display: grid;
  gap: 12px;
  color: #475569;
  font-size: 14px;
  line-height: 1.75;
}

.ms-feature {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.ms-dot {
  width: 8px;
  height: 8px;
  margin-top: 8px;
  border-radius: 999px;
  background: #2f73ff;
  flex: none;
}

.ms-api-chip {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  background: #eff6ff;
  color: #2f73ff;
  font-size: 12px;
  font-weight: 500;
}

.ms-code-line {
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 12px;
  background: #020617;
  color: #e2e8f0;
  font-family: Consolas, monospace;
  font-size: 12px;
}

/* 双列布局 */
.ms-two-col {
  display: grid;
  grid-template-columns: 1.08fr 0.92fr;
  gap: 24px;
}

.ms-section {
  border: 1px solid #e2e8f0;
  border-radius: 24px;
  background: #fff;
  padding: 24px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05), 0 8px 24px rgba(15, 23, 42, 0.04);
}

.ms-section-head {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.ms-section-title {
  font-size: 32px;
  font-weight: 700;
  color: #0f172a;
}

.ms-section-desc {
  margin-top: 4px;
  font-size: 14px;
  color: #64748b;
}

.ms-status {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 14px;
  background: #ecfdf5;
  color: #047857;
}

.ms-textarea-label {
  margin-bottom: 8px;
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.ms-textarea {
  width: 100%;
  height: 300px;
  padding: 16px 20px;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: #f8fafc;
  color: #334155;
  font-size: 14px;
  line-height: 1.75;
  resize: none;
  outline: none;
  transition: border-color 0.2s, background 0.2s;
  font-family: inherit;
}

.ms-textarea:focus {
  border-color: #2f73ff;
  background: #fff;
}

.ms-btn-row {
  margin-top: 32px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.ms-btn-main {
  padding: 12px 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, #5fa8ff 0%, #3b82ff 38%, #1f5fff 100%);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(59,130,255,0.18);
  transition: all 0.2s;
}

.ms-btn-main:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59,130,255,0.25);
}

.ms-btn-sub {
  padding: 12px 20px;
  border-radius: 12px;
  background: #fff;
  color: #334155;
  font-size: 14px;
  font-weight: 600;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s;
}

.ms-btn-sub:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

/* 结果列表 */
.ms-result-list {
  display: grid;
  gap: 12px;
}

.ms-result-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, 1fr);
}

.ms-result-card {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: #f8fafc;
}

.ms-result-top {
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.ms-result-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.ms-result-key {
  padding: 4px 10px;
  border-radius: 999px;
  background: #fff;
  font-size: 12px;
  color: #64748b;
}

.ms-result-item {
  margin-top: 6px;
  padding: 8px 12px;
  border-radius: 12px;
  background: #fff;
  color: #475569;
  font-size: 13px;
  line-height: 1.65;
  border-left: 3px solid #2f73ff;
}

.ms-result-empty {
  color: #94a3b8;
  font-style: italic;
  font-size: 13px;
}

/* API 文档区域 */
.ms-doc-section {
  border: 1px solid #e2e8f0;
  border-radius: 24px;
  background: #fff;
  padding: 24px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05), 0 8px 24px rgba(15, 23, 42, 0.04);
  margin-top: 24px;
}

.ms-doc-grid {
  display: grid;
  grid-template-columns: 0.95fr 1.05fr;
  gap: 20px;
}

.ms-info-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.ms-info-card {
  padding: 16px;
  border-radius: 12px;
  background: #fff;
  border: 1px solid #e2e8f0;
}

.ms-info-k {
  font-size: 12px;
  color: #64748b;
}

.ms-info-v {
  margin-top: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  word-break: break-all;
}

.ms-code-card {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: #020617;
  color: #e2e8f0;
  font-size: 12px;
  margin-top: 20px;
}

.ms-code-title {
  margin-bottom: 12px;
  color: #94a3b8;
}

.ms-code-card pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: Consolas, monospace;
  line-height: 1.6;
}

.ms-tips {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: linear-gradient(180deg, #f8fbff 0%, #f2f7ff 100%);
  margin-top: 20px;
}

.ms-tips-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.ms-tips p {
  margin: 16px 0 0;
  color: #475569;
  font-size: 14px;
  line-height: 1.75;
}

@media (max-width: 1024px) {
  .ms-hero-grid { grid-template-columns: 1fr; }
  .ms-two-col { grid-template-columns: 1fr; }
  .ms-doc-grid { grid-template-columns: 1fr; }
  .ms-result-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .ms-hero-title { font-size: 30px; }
  .ms-section-title { font-size: 24px; }
  .ms-hero-stats { grid-template-columns: 1fr; }
}
"""

# 功能导航数据
NAV_TREE = [
    {
        "name": "语步识别工具",
        "icon": "📝",
        "children": [
            {"name": "中文摘要语步识别", "id": "zh-abstract", "desc": "识别中文科技文献摘要中的研究背景、目的、方法、结果、结论"},
            {"name": "英文摘要语步识别", "id": "en-abstract", "desc": "识别英文科技文献摘要中的研究背景、目的、方法、结果、结论"},
            {"name": "中文基金项目语步识别", "id": "zh-project", "desc": "识别中文基金项目申请书中的立项依据、研究目标、研究内容等"},
        ]
    },
    {
        "name": "自动分类工具",
        "icon": "📂",
        "children": [
            {"name": "中文科技文献分类", "desc": "对中文科技文献进行自动分类，支持多级分类体系"},
            {"name": "英文科技文献分类", "desc": "对英文科技文献进行自动分类，支持多级分类体系"},
            {"name": "专业领域科技文献分类", "desc": "针对专业领域的科技文献进行精细化分类"},
        ]
    },
    {
        "name": "关键词识别工具",
        "icon": "🔑",
        "children": [
            {"name": "中文科技文献关键词识别", "desc": "自动提取中文科技文献的核心关键词"},
            {"name": "英文科技文献关键词识别", "desc": "自动提取英文科技文献的核心关键词"},
        ]
    },
    {
        "name": "研究问题识别工具",
        "icon": "❓",
        "children": [
            {"name": "研究问题识别", "desc": "从科技文献中识别和提取研究问题"},
        ]
    },
    {
        "name": "引用句识别工具",
        "icon": "💬",
        "children": [
            {"name": "引用情感识别", "desc": "识别引用句的情感倾向（正面、负面、中性）"},
            {"name": "引用意图识别", "desc": "识别引用句的引用意图（支持、对比、批判等）"},
        ]
    },
    {
        "name": "概念定义识别工具",
        "icon": "📖",
        "children": [
            {"name": "概念定义句识别", "desc": "从科技文献中识别概念定义句及其核心概念"},
        ]
    },
    {
        "name": "命名实体识别工具",
        "icon": "🏷️",
        "children": [
            {"name": "中英文通用领域命名实体识别", "desc": "识别通用领域的人名、地名、机构名等实体"},
            {"name": "中英文通用科研实体识别", "desc": "识别科研领域的方法、数据集、指标等实体"},
            {"name": "专业领域科研实体识别", "desc": "识别专业领域的特定实体"},
            {"name": "实体关系识别", "desc": "识别实体之间的语义关系"},
        ]
    },
    {
        "name": "深度聚类工具",
        "icon": "🔮",
        "children": [
            {"name": "多文档文本聚类", "desc": "对多篇科技文献进行深度聚类分析"},
        ]
    },
    {
        "name": "聚类标签生成工具",
        "icon": "🏷️",
        "children": [
            {"name": "类簇标签生成", "desc": "为聚类结果生成概括性标签"},
        ]
    },
    {
        "name": "结构化自动综述工具",
        "icon": "📄",
        "children": [
            {"name": "结构化自动综述", "desc": "基于多篇文献自动生成结构化综述"},
        ]
    },
]

RECENT_RECORDS = [
    {"time": "2026-04-16 14:32:15", "module": "语步识别工具", "user": "张三", "status": "success", "duration": "1.2s"},
    {"time": "2026-04-16 14:28:42", "module": "自动分类工具", "user": "李四", "status": "success", "duration": "0.8s"},
    {"time": "2026-04-16 14:25:18", "module": "关键词识别工具", "user": "王五", "status": "success", "duration": "1.5s"},
    {"time": "2026-04-16 14:20:33", "module": "命名实体识别工具", "user": "赵六", "status": "pending", "duration": "-"},
    {"time": "2026-04-16 14:15:07", "module": "语步识别工具", "user": "孙七", "status": "success", "duration": "1.1s"},
    {"time": "2026-04-16 14:10:22", "module": "研究问题识别工具", "user": "周八", "status": "failed", "duration": "-"},
    {"time": "2026-04-16 13:58:45", "module": "引用句识别工具", "user": "吴九", "status": "success", "duration": "0.9s"},
    {"time": "2026-04-16 13:52:30", "module": "概念定义识别工具", "user": "郑十", "status": "success", "duration": "1.3s"},
    {"time": "2026-04-16 13:45:18", "module": "深度聚类工具", "user": "钱十一", "status": "success", "duration": "2.1s"},
    {"time": "2026-04-16 13:38:55", "module": "聚类标签生成工具", "user": "孙十二", "status": "success", "duration": "0.7s"},
    {"time": "2026-04-16 13:30:22", "module": "结构化自动综述工具", "user": "李十三", "status": "pending", "duration": "-"},
    {"time": "2026-04-16 13:22:10", "module": "语步识别工具", "user": "王十四", "status": "success", "duration": "1.0s"},
    {"time": "2026-04-16 13:15:45", "module": "自动分类工具", "user": "赵十五", "status": "success", "duration": "0.6s"},
    {"time": "2026-04-16 13:08:33", "module": "关键词识别工具", "user": "张十六", "status": "failed", "duration": "-"},
    {"time": "2026-04-16 12:55:20", "module": "命名实体识别工具", "user": "李十七", "status": "success", "duration": "1.4s"},
]

PAGE_SIZE = 6


def render_nav_tree() -> str:
    """渲染导航树"""
    # 定义需要跳转到独立页面的功能（Flask 服务器端口 5000）
    external_pages = {
        "zh-abstract": "http://127.0.0.1:5000/frontend/zh-abstract.html",
        "en-abstract": "http://127.0.0.1:5000/frontend/en-abstract.html",
        "zh-project": "http://127.0.0.1:5000/frontend/zh-project.html"
    }

    html_parts = ['<div class="nav-tree">']

    for item in NAV_TREE:
        html_parts.append(f'''
        <div class="nav-group">
          <div class="nav-parent">
            <span class="nav-parent-icon">{item["icon"]}</span>
            <span>{item["name"]}</span>
          </div>
          <div class="nav-children">''')

        for child in item["children"]:
            child_name = child["name"] if isinstance(child, dict) else child
            child_id = child.get("id", child_name) if isinstance(child, dict) else child_name

            # 检查是否需要跳转到独立页面（同一标签页内跳转）
            if child_id in external_pages:
                html_parts.append(f'''
                <a href="{external_pages[child_id]}" class="nav-child" style="text-decoration:none;color:inherit;display:block;">{child_name}</a>''')
            else:
                html_parts.append(f'''
                <button class="nav-child" onclick="showPage('{child_id}')">{child_name}</button>''')

        html_parts.append('</div></div>')

    html_parts.append('</div>')
    return "".join(html_parts)


def render_main_page_no_table() -> str:
    """渲染主页面（不包含表格部分）"""
    tool_intros = []
    for item in NAV_TREE:
        children_names = [c["name"] if isinstance(c, dict) else c for c in item["children"]]
        tool_intros.append({
            "icon": item["icon"],
            "title": item["name"],
            "desc": item["children"][0]["desc"] if item["children"] else "",
            "features": children_names[:3]
        })

    tool_cards_html = "".join([f'''
        <div class="tool-intro-card">
            <div class="tool-intro-header">
                <div class="tool-intro-icon">{t["icon"]}</div>
                <h3 class="tool-intro-title">{t["title"]}</h3>
            </div>
            <p class="tool-intro-desc">{t["desc"]}</p>
            <div class="tool-intro-features">
                {"".join([f'<span class="tool-intro-tag">{f}</span>' for f in t["features"]])}
            </div>
        </div>''' for t in tool_intros])

    return f"""
    <div id="page-main" class="page-container active">
        <!-- 统计卡片 -->
        <div class="stats-cards">
            <div class="stat-card">
                <div class="stat-card-icon blue">📊</div>
                <div class="stat-card-value">12,580</div>
                <div class="stat-card-label">累计调用次数</div>
                <div class="stat-card-trend up">↑ 12.5% 较上月</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-icon green">📈</div>
                <div class="stat-card-value">342</div>
                <div class="stat-card-label">今日调用次数</div>
                <div class="stat-card-trend up">↑ 8.2% 较昨日</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-icon orange">⏱️</div>
                <div class="stat-card-value">1.28s</div>
                <div class="stat-card-label">平均响应时间</div>
                <div class="stat-card-trend down">↓ 0.3s 较上周</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-icon purple">✅</div>
                <div class="stat-card-value">98.6%</div>
                <div class="stat-card-label">成功率</div>
                <div class="stat-card-trend up">↑ 1.2% 较上月</div>
            </div>
        </div>

        <!-- 统计图表 -->
        <div class="charts-grid">
            <div class="chart-card">
                <h3 class="chart-card-title">模块使用分布</h3>
                <div class="chart-container"><canvas id="pieChart"></canvas></div>
            </div>
            <div class="chart-card">
                <h3 class="chart-card-title">近7日调用趋势</h3>
                <div class="chart-container"><canvas id="lineChart"></canvas></div>
            </div>
        </div>

        <!-- 工具介绍 -->
        <div class="tool-intro-grid">
            {tool_cards_html}
        </div>
    </div>
    """


def render_table_page(current_page: int) -> str:
    """渲染当前页的表格数据"""
    total_records = len(RECENT_RECORDS)
    total_pages = (total_records + PAGE_SIZE - 1) // PAGE_SIZE

    start_idx = (current_page - 1) * PAGE_SIZE
    end_idx = min(start_idx + PAGE_SIZE, total_records)

    rows_html = ""
    for i, r in enumerate(RECENT_RECORDS[start_idx:end_idx]):
        actual_idx = start_idx + i + 1
        status_text = '成功' if r['status'] == 'success' else ('处理中' if r['status'] == 'pending' else '失败')
        rows_html += f'''
        <tr>
            <td>{actual_idx}</td>
            <td>{r['time']}</td>
            <td><span class="module-tag">{r['module']}</span></td>
            <td>{r['user']}</td>
            <td><span class="status-badge {r['status']}">{status_text}</span></td>
            <td>{r['duration']}</td>
        </tr>'''

    return f"""
    <div class="table-card">
        <h3 class="table-title">历史使用记录</h3>
        <table class="data-table" id="history-table">
            <thead><tr><th>序号</th><th>时间</th><th>模块</th><th>用户</th><th>状态</th><th>耗时</th></tr></thead>
            <tbody id="history-tbody">
                {rows_html}
            </tbody>
        </table>
    </div>
    """


def get_pagination_info(current_page: int) -> str:
    """获取分页信息文本"""
    total_records = len(RECENT_RECORDS)
    total_pages = (total_records + PAGE_SIZE - 1) // PAGE_SIZE
    return f"第 {current_page} / {total_pages} 页，共 {total_records} 条记录"


def render_js() -> str:
    """渲染 JavaScript（仅用于图表初始化）"""
    return """
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <script>
        function initCharts() {
            setTimeout(function() {
                const pieCtx = document.getElementById('pieChart');
                if (pieCtx) {
                    new Chart(pieCtx, {
                        type: 'doughnut',
                        data: {
                            labels: ['语步识别工具', '自动分类工具', '关键词识别工具', '命名实体识别工具', '研究问题识别工具', '引用句识别工具', '概念定义识别工具', '其他'],
                            datasets: [{
                                data: [3250, 2180, 1890, 1650, 1280, 980, 850, 500],
                                backgroundColor: ['#2563ff', '#3b82f6', '#60a5fa', '#93c5fd', '#22c55e', '#4ade80', '#f97316', '#a855f7'],
                                borderWidth: 0,
                                hoverOffset: 8
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    position: 'right',
                                    labels: { padding: 12, usePointStyle: true, pointStyle: 'circle', font: { size: 11 } }
                                }
                            },
                            cutout: '60%'
                        }
                    });
                }

                const lineCtx = document.getElementById('lineChart');
                if (lineCtx) {
                    new Chart(lineCtx, {
                        type: 'line',
                        data: {
                            labels: ['4/10', '4/11', '4/12', '4/13', '4/14', '4/15', '4/16'],
                            datasets: [{
                                label: '调用次数',
                                data: [285, 312, 298, 345, 328, 367, 342],
                                borderColor: '#2563ff',
                                backgroundColor: 'rgba(37, 99, 255, 0.1)',
                                fill: true,
                                tension: 0.4,
                                borderWidth: 3,
                                pointBackgroundColor: '#2563ff',
                                pointRadius: 5,
                                pointHoverRadius: 7
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: { legend: { display: false } },
                            scales: {
                                y: { beginAtZero: true, grid: { color: 'rgba(195, 214, 255, 0.3)' }, ticks: { font: { size: 11 } } },
                                x: { grid: { display: false }, ticks: { font: { size: 11 } } }
                            }
                        }
                    });
                }
            }, 500);
        }

        if (document.readyState === 'complete' || document.readyState === 'interactive') {
            initCharts();
        } else {
            document.addEventListener('DOMContentLoaded', initCharts);
        }
    </script>
    """


# JavaScript代码，通过head参数注入到页面
APP_JS_SCRIPT = """
<script>
// 将函数挂载到window对象，确保全局可访问
window.showPage = function(pageId) {
    console.log('showPage called with: ' + pageId);

    const homePage = document.getElementById('home-page-content');
    const pageMap = {
        'zh-abstract': document.getElementById('zh-abstract-page'),
        'en-abstract': document.getElementById('en-abstract-page'),
        'zh-project': document.getElementById('zh-project-page')
    };

    document.querySelectorAll('.nav-child').forEach(el => {
        el.classList.remove('active');
        const onclickValue = el.getAttribute('onclick') || '';
        if (onclickValue.includes(pageId)) {
            el.classList.add('active');
        }
    });

    if (homePage) {
        homePage.style.display = pageMap[pageId] ? 'none' : 'flex';
    }

    Object.entries(pageMap).forEach(([key, pageEl]) => {
        if (!pageEl) {
            return;
        }
        if (key === pageId) {
            pageEl.classList.add('show');
        } else {
            pageEl.classList.remove('show');
        }
    });

    if (!pageMap[pageId]) {
        console.warn('Unknown page id: ' + pageId);
    }
};

document.addEventListener('DOMContentLoaded', function() {
    const homePage = document.getElementById('home-page-content');
    if (homePage) {
        homePage.style.display = 'flex';
    }
});

console.log('JavaScript functions loaded and attached to window');
</script>
"""


# ==================== 结果渲染函数 ====================

def render_zh_abstract_result(result_data: dict) -> str:
    """渲染中文摘要识别结果为HTML (ModelScope风格)"""
    if not result_data:
        return ""

    code = result_data.get("code", 500)
    message = result_data.get("message", "未知错误")
    data = result_data.get("data", {})

    if code != 200:
        return f"""
        <div class="ms-section">
            <div class="ms-section-head">
                <div>
                    <div class="ms-section-title">识别结果</div>
                </div>
            </div>
            <div class="ms-result-card" style="border-color: #fecaca; background: #fef2f2;">
                <div style="color: #dc2626;">❌ 分析失败：{message}</div>
            </div>
        </div>
        """

    # 渲染五类结果
    move_labels = {
        "background": "研究背景",
        "purpose": "研究目的",
        "method": "研究方法",
        "result": "研究结果",
        "conclusion": "研究结论"
    }

    result_cards = ""
    for key, label in move_labels.items():
        sentences = data.get(key, [])
        content = ""
        if sentences:
            for s in sentences:
                content += f'<div class="ms-result-item">{s}</div>'
        else:
            content = '<div class="ms-result-empty">未识别到相关内容</div>'

        result_cards += f"""
        <div class="ms-result-card">
            <div class="ms-result-top">
                <div class="ms-result-title">{label}</div>
                <div class="ms-result-key">{key}</div>
            </div>
            {content}
        </div>
        """

    # JSON展示
    json_str = json.dumps(result_data, ensure_ascii=False, indent=2)

    return f"""
    <div class="ms-section">
        <div class="ms-section-head">
            <div>
                <div class="ms-section-title">输出预览</div>
                <div class="ms-section-desc">统一 JSON 结构，便于第三方系统消费</div>
            </div>
        </div>
        <div class="ms-result-list">
            {result_cards}
        </div>
        <div class="ms-code-card" style="margin-top: 16px;">
            <div class="ms-code-title">原始 JSON 响应</div>
            <pre>{json_str}</pre>
        </div>
    </div>
    """


def render_en_abstract_result(result_data: dict) -> str:
    """渲染英文摘要识别结果为HTML (ModelScope风格)"""
    if not result_data:
        return ""

    code = result_data.get("code", 500)
    message = result_data.get("message", "Unknown error")
    data = result_data.get("data", {})

    if code != 200:
        return f"""
        <div class="ms-section">
            <div class="ms-section-head">
                <div>
                    <div class="ms-section-title">Recognition Result</div>
                </div>
            </div>
            <div class="ms-result-card" style="border-color: #fecaca; background: #fef2f2;">
                <div style="color: #dc2626;">❌ Analysis Failed: {message}</div>
            </div>
        </div>
        """

    # 渲染五类结果
    move_labels = {
        "background": "Background",
        "purpose": "Purpose",
        "method": "Method",
        "result": "Result",
        "conclusion": "Conclusion"
    }

    result_cards = ""
    for key, label in move_labels.items():
        sentences = data.get(key, [])
        content = ""
        if sentences:
            for s in sentences:
                content += f'<div class="ms-result-item">{s}</div>'
        else:
            content = '<div class="ms-result-empty">No content identified</div>'

        result_cards += f"""
        <div class="ms-result-card">
            <div class="ms-result-top">
                <div class="ms-result-title">{label}</div>
                <div class="ms-result-key">{key}</div>
            </div>
            {content}
        </div>
        """

    # JSON展示
    json_str = json.dumps(result_data, ensure_ascii=False, indent=2)

    return f"""
    <div class="ms-section">
        <div class="ms-section-head">
            <div>
                <div class="ms-section-title">Output Preview</div>
                <div class="ms-section-desc">Unified JSON structure for easy third-party consumption</div>
            </div>
        </div>
        <div class="ms-result-list">
            {result_cards}
        </div>
        <div class="ms-code-card" style="margin-top: 16px;">
            <div class="ms-code-title">Raw JSON Response</div>
            <pre>{json_str}</pre>
        </div>
    </div>
    """


def render_zh_project_result(result_data: dict) -> str:
    """渲染中文基金项目识别结果为HTML (ModelScope风格)"""
    if not result_data:
        return ""

    code = result_data.get("code", 500)
    message = result_data.get("message", "未知错误")
    data = result_data.get("data", {})

    if code != 200:
        return f"""
        <div class="ms-section">
            <div class="ms-section-head">
                <div>
                    <div class="ms-section-title">识别结果</div>
                </div>
            </div>
            <div class="ms-result-card" style="border-color: #fecaca; background: #fef2f2;">
                <div style="color: #dc2626;">❌ 分析失败：{message}</div>
            </div>
        </div>
        """

    # 渲染六类结果
    move_labels = {
        "basis": "立项依据",
        "objective": "研究目标",
        "content": "研究内容",
        "approach": "技术路线",
        "expected_result": "预期成果",
        "application_value": "应用价值"
    }

    result_cards = ""
    for key, label in move_labels.items():
        sentences = data.get(key, [])
        content = ""
        if sentences:
            for s in sentences:
                content += f'<div class="ms-result-item">{s}</div>'
        else:
            content = '<div class="ms-result-empty">未识别到相关内容</div>'

        result_cards += f"""
        <div class="ms-result-card">
            <div class="ms-result-top">
                <div class="ms-result-title">{label}</div>
                <div class="ms-result-key">{key}</div>
            </div>
            {content}
        </div>
        """

    # JSON展示
    json_str = json.dumps(result_data, ensure_ascii=False, indent=2)

    return f"""
    <div class="ms-section">
        <div class="ms-section-head">
            <div>
                <div class="ms-section-title">输出预览</div>
                <div class="ms-section-desc">统一 JSON 结构，便于第三方系统消费</div>
            </div>
        </div>
        <div class="ms-result-grid">
            {result_cards}
        </div>
        <div class="ms-code-card" style="margin-top: 16px;">
            <div class="ms-code-title">原始 JSON 响应</div>
            <pre>{json_str}</pre>
        </div>
    </div>
    """


with gr.Blocks(title="语义计算工具库") as demo:
    # 状态变量
    current_page_state = gr.State(value=1)

    # 顶部header
    gr.HTML(
        """
        <div class="page-wrapper">
            <div class="top-header">
              <div class="brand-wrap">
                <div class="brand-icon">语</div>
                <div>
                  <div class="brand-title">语义计算工具库</div>
                  <div class="brand-subtitle">Semantic Computing Platform</div>
                </div>
              </div>
              <div class="header-center-title">语义计算工具库</div>
              <div class="header-welcome">欢迎使用</div>
            </div>
        </div>
        """
    )

    # 主内容区域 - 使用Gradio的行列布局
    with gr.Row(elem_classes="content-row") as main_row:
        # 左侧导航栏
        with gr.Column(scale=1, min_width=320, elem_classes="sidebar-col"):
            gr.HTML(
                f"""
                <div class="sidebar">
                    <div class="sidebar-hero">
                      <h3>功能导航</h3>
                      <p>按工具模块浏览平台能力</p>
                    </div>
                    {render_nav_tree()}
                </div>
                """
            )

        # 右侧内容区域
        with gr.Column(scale=3, elem_classes="main-col"):
            # ========== 首页内容 ==========
            with gr.Column(elem_id="home-page-content"):
                gr.HTML(value=render_main_page_no_table())

                # 表格部分
                table_html = gr.HTML(value=render_table_page(1))

                # 分页控件
                with gr.Row(elem_classes="pagination-row"):
                    prev_btn = gr.Button("◀ 上一页", elem_classes="pagination-btn", scale=0, min_width=100)
                    page_info = gr.HTML(value=f"<div class='pagination-info'>{get_pagination_info(1)}</div>")
                    next_btn = gr.Button("下一页 ▶", elem_classes="pagination-btn", scale=0, min_width=100)

            # ========== 中文摘要语步识别页面 ==========
            with gr.Column(elem_id="zh-abstract-page", elem_classes="func-page-container"):
                gr.HTML(
                    """
                    <div class="ms-hero">
                        <div class="ms-hero-grid">
                            <div class="ms-hero-main">
                                <div class="ms-hero-tags">
                                    <span class="ms-hero-tag">语步识别</span>
                                    <span class="ms-hero-tag">中文摘要</span>
                                    <span class="ms-hero-tag">API 可接入</span>
                                </div>
                                <h1 class="ms-hero-title">中文摘要语步识别</h1>
                                <p class="ms-hero-desc">面向系统研发人员与平台接入场景，对中文科技论文摘要进行结构化语步识别，自动抽取研究背景、研究目的、研究方法、研究结果与研究结论，支持在线测试与标准 API 集成。</p>
                                <div class="ms-hero-stats">
                                    <div class="ms-hero-stat">
                                        <div class="ms-hero-stat-k">输入对象</div>
                                        <div class="ms-hero-stat-v">中文科技论文摘要</div>
                                    </div>
                                    <div class="ms-hero-stat">
                                        <div class="ms-hero-stat-k">输出结构</div>
                                        <div class="ms-hero-stat-v">五类语步 JSON</div>
                                    </div>
                                    <div class="ms-hero-stat">
                                        <div class="ms-hero-stat-k">接入方式</div>
                                        <div class="ms-hero-stat-v">RESTful API</div>
                                    </div>
                                </div>
                            </div>
                            <div class="ms-hero-side">
                                <div class="ms-mini-card">
                                    <div class="ms-mini-title">能力摘要</div>
                                    <div class="ms-feature-list">
                                        <div class="ms-feature"><span class="ms-dot"></span><span>支持单段摘要文本输入，适用于研发联调与平台能力验证。</span></div>
                                        <div class="ms-feature"><span class="ms-dot"></span><span>统一输出五类语步字段，适合被其他项目直接调用和消费。</span></div>
                                        <div class="ms-feature"><span class="ms-dot"></span><span>页面内置在线体验、返回预览、请求示例与 Python 调用代码。</span></div>
                                    </div>
                                </div>
                                <div class="ms-mini-card" style="background:#fff;">
                                    <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
                                        <div>
                                            <div class="ms-mini-title">快速接入</div>
                                            <div style="margin-top:4px;font-size:12px;color:#64748b;">统一对外业务接口</div>
                                        </div>
                                        <span class="ms-api-chip">POST</span>
                                    </div>
                                    <div class="ms-code-line">POST /api/move-recognition/chinese-abstract</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """
                )

                with gr.Row():
                    with gr.Column():
                        gr.HTML(
                            """
                            <div class="ms-section">
                                <div class="ms-section-head">
                                    <div>
                                        <div class="ms-section-title">在线体验</div>
                                        <div class="ms-section-desc">输入摘要并查看结构化语步识别结果</div>
                                    </div>
                                    <div class="ms-status">在线可用</div>
                                </div>
                                <label class="ms-textarea-label">摘要内容</label>
                            </div>
                            """
                        )
                        zh_abstract_input = gr.Textbox(
                            label="中文摘要",
                            placeholder="请输入中文科技论文摘要文本...",
                            lines=12,
                            elem_classes="ms-textarea",
                            show_label=False
                        )

                        with gr.Row(elem_classes="ms-btn-row"):
                            zh_abstract_example_btn = gr.Button("填入示例", elem_classes="ms-btn-sub", scale=0, min_width=100)
                            zh_abstract_clear_btn = gr.Button("清空内容", elem_classes="ms-btn-sub", scale=0, min_width=100)
                            zh_abstract_analyze_btn = gr.Button("开始识别", elem_classes="ms-btn-main", scale=0, min_width=120, variant="primary")

                    zh_abstract_result = gr.HTML(value="", visible=False)

            # ========== 英文摘要语步识别页面 ==========
            with gr.Column(elem_id="en-abstract-page", elem_classes="func-page-container"):
                gr.HTML(
                    """
                    <div class="ms-hero">
                        <div class="ms-hero-grid">
                            <div class="ms-hero-main en">
                                <div class="ms-hero-tags">
                                    <span class="ms-hero-tag">Move Recognition</span>
                                    <span class="ms-hero-tag">English Abstract</span>
                                    <span class="ms-hero-tag">API Available</span>
                                </div>
                                <h1 class="ms-hero-title">English Abstract Move Recognition</h1>
                                <p class="ms-hero-desc">Automatically identify and extract research background, purpose, method, results, and conclusion from English scientific abstracts. Designed for system developers and platform integration scenarios.</p>
                                <div class="ms-hero-stats">
                                    <div class="ms-hero-stat">
                                        <div class="ms-hero-stat-k">Input Type</div>
                                        <div class="ms-hero-stat-v">English Scientific Abstract</div>
                                    </div>
                                    <div class="ms-hero-stat">
                                        <div class="ms-hero-stat-k">Output Structure</div>
                                        <div class="ms-hero-stat-v">5 Move Types JSON</div>
                                    </div>
                                    <div class="ms-hero-stat">
                                        <div class="ms-hero-stat-k">Integration</div>
                                        <div class="ms-hero-stat-v">RESTful API</div>
                                    </div>
                                </div>
                            </div>
                            <div class="ms-hero-side">
                                <div class="ms-mini-card">
                                    <div class="ms-mini-title">Capability Summary</div>
                                    <div class="ms-feature-list">
                                        <div class="ms-feature"><span class="ms-dot"></span><span>Support single abstract text input, suitable for development testing and verification.</span></div>
                                        <div class="ms-feature"><span class="ms-dot"></span><span>Unified output with five move fields, ready for direct integration.</span></div>
                                        <div class="ms-feature"><span class="ms-dot"></span><span>Built-in online testing, result preview, request examples and Python code.</span></div>
                                    </div>
                                </div>
                                <div class="ms-mini-card" style="background:#fff;">
                                    <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
                                        <div>
                                            <div class="ms-mini-title">Quick Integration</div>
                                            <div style="margin-top:4px;font-size:12px;color:#64748b;">Unified API endpoint</div>
                                        </div>
                                        <span class="ms-api-chip">POST</span>
                                    </div>
                                    <div class="ms-code-line">POST /api/move-recognition/english-abstract</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """
                )

                with gr.Row():
                    with gr.Column():
                        gr.HTML(
                            """
                            <div class="ms-section">
                                <div class="ms-section-head">
                                    <div>
                                        <div class="ms-section-title">Online Testing</div>
                                        <div class="ms-section-desc">Enter abstract and view structured move recognition results</div>
                                    </div>
                                    <div class="ms-status">Online</div>
                                </div>
                                <label class="ms-textarea-label">Abstract Content</label>
                            </div>
                            """
                        )
                        en_abstract_input = gr.Textbox(
                            label="English Abstract",
                            placeholder="Please enter English scientific abstract...",
                            lines=12,
                            elem_classes="ms-textarea",
                            show_label=False
                        )

                        with gr.Row(elem_classes="ms-btn-row"):
                            en_abstract_example_btn = gr.Button("Fill Example", elem_classes="ms-btn-sub", scale=0, min_width=100)
                            en_abstract_clear_btn = gr.Button("Clear", elem_classes="ms-btn-sub", scale=0, min_width=100)
                            en_abstract_analyze_btn = gr.Button("Start Recognition", elem_classes="ms-btn-main", scale=0, min_width=120, variant="primary")

                    en_abstract_result = gr.HTML(value="", visible=False)

            # ========== 中文基金项目语步识别页面 ==========
            with gr.Column(elem_id="zh-project-page", elem_classes="func-page-container"):
                gr.HTML(
                    """
                    <div class="ms-hero">
                        <div class="ms-hero-grid">
                            <div class="ms-hero-main project">
                                <div class="ms-hero-tags">
                                    <span class="ms-hero-tag">语步识别</span>
                                    <span class="ms-hero-tag">基金项目</span>
                                    <span class="ms-hero-tag">API 可接入</span>
                                </div>
                                <h1 class="ms-hero-title">中文基金项目语步识别</h1>
                                <p class="ms-hero-desc">面向系统研发人员与平台接入场景，对中文基金项目申请书进行结构化语步识别，自动抽取立项依据、研究目标、研究内容、技术路线、预期成果与应用价值，支持在线测试与标准 API 集成。</p>
                                <div class="ms-hero-stats">
                                    <div class="ms-hero-stat">
                                        <div class="ms-hero-stat-k">输入对象</div>
                                        <div class="ms-hero-stat-v">中文基金项目申请书</div>
                                    </div>
                                    <div class="ms-hero-stat">
                                        <div class="ms-hero-stat-k">输出结构</div>
                                        <div class="ms-hero-stat-v">六类语步 JSON</div>
                                    </div>
                                    <div class="ms-hero-stat">
                                        <div class="ms-hero-stat-k">接入方式</div>
                                        <div class="ms-hero-stat-v">RESTful API</div>
                                    </div>
                                </div>
                            </div>
                            <div class="ms-hero-side">
                                <div class="ms-mini-card">
                                    <div class="ms-mini-title">能力摘要</div>
                                    <div class="ms-feature-list">
                                        <div class="ms-feature"><span class="ms-dot"></span><span>支持基金项目文本输入，适用于研发联调与平台能力验证。</span></div>
                                        <div class="ms-feature"><span class="ms-dot"></span><span>统一输出六类语步字段，适合被其他项目直接调用和消费。</span></div>
                                        <div class="ms-feature"><span class="ms-dot"></span><span>页面内置在线体验、返回预览、请求示例与 Python 调用代码。</span></div>
                                    </div>
                                </div>
                                <div class="ms-mini-card" style="background:#fff;">
                                    <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
                                        <div>
                                            <div class="ms-mini-title">快速接入</div>
                                            <div style="margin-top:4px;font-size:12px;color:#64748b;">统一对外业务接口</div>
                                        </div>
                                        <span class="ms-api-chip">POST</span>
                                    </div>
                                    <div class="ms-code-line">POST /api/move-recognition/chinese-project</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """
                )

                with gr.Row():
                    with gr.Column():
                        gr.HTML(
                            """
                            <div class="ms-section">
                                <div class="ms-section-head">
                                    <div>
                                        <div class="ms-section-title">在线体验</div>
                                        <div class="ms-section-desc">输入基金项目文本并查看结构化语步识别结果</div>
                                    </div>
                                    <div class="ms-status">在线可用</div>
                                </div>
                                <label class="ms-textarea-label">基金项目文本</label>
                            </div>
                            """
                        )
                        zh_project_input = gr.Textbox(
                            label="基金项目文本",
                            placeholder="请输入中文基金项目申请书内容...",
                            lines=12,
                            elem_classes="ms-textarea",
                            show_label=False
                        )

                        with gr.Row(elem_classes="ms-btn-row"):
                            zh_project_example_btn = gr.Button("填入示例", elem_classes="ms-btn-sub", scale=0, min_width=100)
                            zh_project_clear_btn = gr.Button("清空内容", elem_classes="ms-btn-sub", scale=0, min_width=100)
                            zh_project_analyze_btn = gr.Button("开始识别", elem_classes="ms-btn-main", scale=0, min_width=120, variant="primary")

                    zh_project_result = gr.HTML(value="", visible=False)

    # 图表JS
    gr.HTML(render_js())

    # ==================== 分页回调 ====================
    def go_prev_page(current_page):
        total_records = len(RECENT_RECORDS)
        total_pages = (total_records + PAGE_SIZE - 1) // PAGE_SIZE
        new_page = max(1, current_page - 1)
        return new_page, render_table_page(new_page), get_pagination_info(new_page)

    def go_next_page(current_page):
        total_records = len(RECENT_RECORDS)
        total_pages = (total_records + PAGE_SIZE - 1) // PAGE_SIZE
        new_page = min(total_pages, current_page + 1)
        return new_page, render_table_page(new_page), get_pagination_info(new_page)

    prev_btn.click(fn=go_prev_page, inputs=[current_page_state], outputs=[current_page_state, table_html, page_info])
    next_btn.click(fn=go_next_page, inputs=[current_page_state], outputs=[current_page_state, table_html, page_info])

    # ==================== 中文摘要语步识别回调 ====================
    def zh_abstract_fill_example():
        return EXAMPLE_ZH_ABSTRACT

    def zh_abstract_clear():
        return "", ""

    def zh_abstract_do_analyze(text: str):
        if not text or not text.strip():
            return "", gr.update(value='<div class="test-section result-section"><p style="color: #d97706;">⚠️ 请先输入中文摘要内容</p></div>', visible=True)
        result = analyze_zh_abstract(text.strip())
        result_html = render_zh_abstract_result(result)
        return text, gr.update(value=result_html, visible=True)

    zh_abstract_example_btn.click(fn=zh_abstract_fill_example, inputs=[], outputs=[zh_abstract_input])
    zh_abstract_clear_btn.click(fn=zh_abstract_clear, inputs=[], outputs=[zh_abstract_input, zh_abstract_result])
    zh_abstract_analyze_btn.click(fn=zh_abstract_do_analyze, inputs=[zh_abstract_input], outputs=[zh_abstract_input, zh_abstract_result])

    # ==================== 英文摘要语步识别回调 ====================
    def en_abstract_fill_example():
        return EXAMPLE_EN_ABSTRACT

    def en_abstract_clear():
        return "", ""

    def en_abstract_do_analyze(text: str):
        if not text or not text.strip():
            return "", gr.update(value='<div class="test-section result-section"><p style="color: #d97706;">⚠️ Please enter English abstract first</p></div>', visible=True)
        result = analyze_en_abstract(text.strip())
        result_html = render_en_abstract_result(result)
        return text, gr.update(value=result_html, visible=True)

    en_abstract_example_btn.click(fn=en_abstract_fill_example, inputs=[], outputs=[en_abstract_input])
    en_abstract_clear_btn.click(fn=en_abstract_clear, inputs=[], outputs=[en_abstract_input, en_abstract_result])
    en_abstract_analyze_btn.click(fn=en_abstract_do_analyze, inputs=[en_abstract_input], outputs=[en_abstract_input, en_abstract_result])

    # ==================== 中文基金项目语步识别回调 ====================
    def zh_project_fill_example():
        return EXAMPLE_ZH_PROJECT

    def zh_project_clear():
        return "", ""

    def zh_project_do_analyze(text: str):
        if not text or not text.strip():
            return "", gr.update(value='<div class="test-section result-section"><p style="color: #d97706;">⚠️ 请先输入基金项目内容</p></div>', visible=True)
        result = analyze_zh_project(text.strip())
        result_html = render_zh_project_result(result)
        return text, gr.update(value=result_html, visible=True)

    zh_project_example_btn.click(fn=zh_project_fill_example, inputs=[], outputs=[zh_project_input])
    zh_project_clear_btn.click(fn=zh_project_clear, inputs=[], outputs=[zh_project_input, zh_project_result])
    zh_project_analyze_btn.click(fn=zh_project_do_analyze, inputs=[zh_project_input], outputs=[zh_project_input, zh_project_result])


if __name__ == "__main__":
    import os
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    demo.launch(
        server_name="127.0.0.1",
        server_port=7862,
        share=False,
        css=CUSTOM_CSS,
        head=APP_JS_SCRIPT,
        allowed_paths=[frontend_dir]
    )

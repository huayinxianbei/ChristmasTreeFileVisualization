## Language

- [English](#english)
- [中文](#中文)

---

### English
# 🎄 Santa 2025 · Tree Packing Visualizer
https://www.kaggle.com/competitions/santa-2025
---

## 📖 Overview

This project is a local **scoring and visualization tool** for the **Santa 2025 Tree Packing** challenge.

It reads a submission CSV file, validates its format, checks for tree collisions, computes group-based scores, and visualizes the packing result for a selected number of trees (`N`) using a Tkinter GUI. Raw CSV row data can be inspected via hover interaction.

---

## ✨ Features

- CSV format validation
- Rotatable geometric tree modeling
- Fast collision detection using STRtree
- Automatic group-based scoring
- Tkinter-based GUI visualization
- Hover inspection of raw CSV data

---

## 🧮 Scoring Rules

### Grouping

- Trees are grouped by the prefix of the `id` field  
- Example:
  - `002_0`
  - `002_1`

These entries belong to `group = 002`, corresponding to `N = 2`.

### Collision Constraints

- ❌ Overlapping trees are not allowed
- ✅ Touching boundaries are allowed

### Score Formula

For each group:

score = side² / N



Where:

- `side` is the side length of the minimal bounding square
- `N` is the number of trees in the group

### Total Score

total_score = Σ score(group)


---

## 🖥️ Graphical Interface

- Load CSV and automatically compute scores
- Select `N (1 ~ 200)` via slider or input
- Render the packing visualization
- Display the bounding square
- Hover interaction:
  - Highlight tree
  - Show raw CSV row data

---

## 📦 Requirements

- Python 3.9 or later
- Dependencies:
  - `pandas`
  - `shapely`
  - `matplotlib`
  - `tkinter`

---

## 📥 Installation

pip install pandas shapely matplotlib

---
🚀 Usage
Run the application

Workflow
Click Load CSV and select a submission file

The application validates the CSV and computes scores

Choose the number of trees N

Click Render N to visualize the group

🧾 CSV Format
Required Columns
Column	Description
id	Tree identifier, prefix defines group
x	X coordinate (string, s prefixed)
y	Y coordinate (string, s prefixed)
deg	Rotation angle in degrees (s prefixed)


id,x,y,deg

002_0,s0.0,s0.0,s15

002_1,s1.2,s0.3,s-5

⚠️ Errors
Missing required columns

Missing s prefix in values

Coordinates out of range

Tree overlap detected



---

### 中文

# 🎄 Santa 2025 · 圣诞树装箱可视化工具
https://www.kaggle.com/competitions/santa-2025


---

## 📖 项目简介

本项目是一个用于 **Santa 2025 Tree Packing** 任务的本地评分与可视化工具。

程序可读取参赛者提交的 CSV 文件，对其进行格式校验、碰撞检测与自动评分，并通过 Tkinter 图形界面直观展示指定树数量（N）的装箱结果，同时支持查看每棵树对应的 CSV 原始行数据。

---

## ✨ 功能特性

- CSV 格式校验（字段、前缀、范围）
- 圣诞树几何建模与旋转
- 基于 STRtree 的高效碰撞检测
- 按组（N）自动评分
- Tkinter 图形界面可视化
- 鼠标悬停显示 CSV 原始数据

---

## 🧮 评分规则

### 分组方式

- 使用 `id` 字段的前缀作为分组标识  
- 示例：  
  - `002_0`  
  - `002_1`  
- 上述数据属于同一组：`group = 002`，即 `N = 2`

### 碰撞规则

- ❌ 不允许树之间 **重叠（overlap）**
- ✅ 允许边界 **接触（touches）**

### 分数计算

对于每一组：

score = side² / N

其中：

- `side`：该组所有树的最小外接正方形边长
- `N`：该组中树的数量

### 总分

total_score = Σ score(group)



---

## 🖥️ 图形界面说明

- 加载 CSV 后自动计算总分与分组分数
- 通过滑条或输入框选择 `N (1 ~ 200)`
- 绘制对应分组的装箱结果
- 显示最小外接正方形
- 鼠标悬停：
  - 高亮当前树
  - 显示该树对应的 CSV 原始行数据

---

## 📦 环境要求

- Python 3.9 或更高版本
- 依赖库：
  - `pandas`
  - `shapely`
  - `matplotlib`
  - `tkinter`

---

## 📥 安装依赖

pip install pandas shapely matplotlib

---
🚀 使用方法
启动程序

操作流程
点击 Load CSV 按钮选择提交文件

程序自动校验 CSV 并计算分数

输入或拖动选择树数量 N

点击 Render N 渲染对应分组

🧾 CSV 文件格式
必需字段
字段名	说明
id	树的唯一标识，前缀表示分组
x	x 坐标，字符串，必须以 s 开头
y	y 坐标，字符串，必须以 s 开头
deg	旋转角度（度），字符串，必须以 s 开头

示例

id,x,y,deg

002_0,s0.0,s0.0,s15

002_1,s1.2,s0.3,s-5

⚠️ 错误说明
CSV 缺少必需字段

坐标或角度未使用 s 前缀

x 或 y 超出允许范围

检测到树之间发生重叠



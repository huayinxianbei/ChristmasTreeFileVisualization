Santa 2025 - 圣诞树装箱可视化工具 (Tree Packing Visualizer)
一个针对 Santa 2025 圣诞树装箱任务的可视化与评分计算工具，提供交互式 GUI 界面、高精度几何计算、碰撞检测、多语言支持等功能，帮助验证装箱方案并直观展示布局效果。
🎯 项目概述 (Project Overview)
该工具核心解决圣诞树装箱任务的两大核心需求：
评分计算：自动验证 CSV 格式、检测树重叠、计算分组分数 / 总分数、装箱边长
可视化展示：直观渲染指定数量（N）的圣诞树装箱布局，支持悬停查看详情、彩色区分不同树、展示 bounding square
适配中文 / 英文双语界面，采用现代化彩色 UI 设计，操作简单且交互友好
✨ 核心功能 (Core Features)
1. CSV 导入与严格验证
校验必填列：id / x / y / deg，缺失列直接报错
验证数值格式：x/y/deg 必须以 s 前缀开头（如 s12.34）
数值范围限制：x/y 必须在 [-100, 100] 区间内
错误提示：清晰的中文 / 英文错误信息，定位问题数据
2. 高精度评分计算
碰撞检测：使用 Shapely STRtree 索引优化，检测树之间是否重叠（仅允许接触，不允许重叠）
分数计算：按分组（N 值）计算装箱分数（(边长²) / N），并汇总总分数
高精度运算：使用 Decimal 类型（精度 25 位）避免浮点误差，缩放因子 1e18 保证几何计算准确性
3. 交互式可视化
彩色渲染：不同圣诞树使用差异化配色，带阴影 / 描边增强视觉效果
布局展示：绘制圣诞树几何形状、顶部星星标记、装箱 bounding square
悬停交互：鼠标悬停树体可查看原始 CSV 行数据（ID / 坐标 / 角度），侧边面板实时展示详情
视图控制：集成 Matplotlib 导航工具栏，支持缩放 / 平移 / 保存图片
4. 分组分数管理
表格展示：按分组（N 值）展示分数、装箱边长，支持排序 / 滚动
过滤功能：快速筛选指定分组，支持清空过滤条件
快捷操作：双击表格行可直接渲染对应 N 值的装箱布局
5. 多语言与 UI 优化
双语切换：一键切换中文 / 英文界面，所有文案自动适配
现代化 UI：彩色卡片式布局、响应式设计、hover 样式增强
固定布局：悬停详情面板固定高度，避免界面抖动
🛠️ 技术栈 (Tech Stack)
模块	技术 / 库	用途
界面框架	Tkinter + ttk	构建跨平台 GUI，自定义样式
数据处理	Pandas	CSV 解析、分组、数据验证
几何计算	Shapely	多边形 / 旋转 / 平移 / 碰撞检测 / STRtree 索引
可视化	Matplotlib	嵌入 Tkinter 渲染圣诞树布局
高精度计算	Python Decimal	避免浮点误差，保证评分准确性
🚀 快速开始 (Quick Start)
1. 环境安装
bash
运行
# 安装依赖包
pip install pandas shapely matplotlib tkinter
# 注意：tkinter 通常随 Python 自带，若缺失可通过系统包管理器安装（如 apt install python3-tk）
2. 运行工具
bash
运行
python tree_packing_visualizer.py
3. 基础操作流程
点击 📁 选择 CSV / 📁 Load CSV 导入装箱方案 CSV 文件
工具自动验证格式并计算所有分组分数，总分数展示在顶部
右侧面板：
选择 N 值（1~200）：通过滑块 / 输入框调整
点击 ✨ 绘制当前 N / ✨ Render N 渲染对应布局
分组表格：过滤 / 双击行快速渲染 / 刷新列表
可视化区域：鼠标悬停树体查看原始 CSV 数据，使用工具栏缩放 / 平移视图
📋 CSV 输入格式要求 (CSV Input Format)
必须列
列名	说明	示例
id	树 ID，格式为 {N:03d}_{序号}（如 002_0 表示 N=2 组的第 0 棵树）	005_3
x	X 坐标，必须以 s 开头	s15.678
y	Y 坐标，必须以 s 开头	s-8.912
deg	旋转角度，必须以 s 开头	s45.0
格式约束
x/y 取值范围：[-100, 100]
deg 无范围限制（支持任意旋转角度）
编码：UTF-8
分隔符：逗号（,）
🖥️ 界面说明 (UI Overview)
区域	功能描述
顶部横幅	工具标题，固定展示
左侧可视化区	圣诞树布局渲染、bounding square、Matplotlib 工具栏
右侧控制面板	- 导入按钮：加载 CSV 文件
- 语言切换：中文 / 英文
- N 选择：滑块 + 输入框
- 悬停详情：展示鼠标指向树的原始 CSV 数据
- 分组表格：展示所有分组分数，支持过滤 / 双击渲染
- 刷新按钮：重新加载分组数据
⚠️ 注意事项 (Notes)
重叠检测：若分组内存在树重叠（非接触），工具会直接报错，需修正 CSV 数据
Shapely 兼容性：适配 Shapely STRtree 多版本返回值（索引 / 几何对象）
高精度计算：所有几何计算基于 1e18 缩放因子，避免浮点精度丢失
性能优化：使用 STRtree 空间索引，大幅提升多树碰撞检测效率
🎨 界面预览 (UI Preview)
（可添加截图，示例描述）
左侧：彩色圣诞树布局 + bounding square + 悬停提示
右侧：中文界面控制面板 + 分组分数表格
悬停效果：树体高亮 + 侧边面板展示原始 CSV 数据
📄 许可证 (License)
该项目为开源工具，可自由修改 / 分发，适用于 Santa 2025 圣诞树装箱任务验证场景。
我要搞个多语言切换 加个英语切换怎么搞 最后交的是markdown格式的readme
Santa 2025 - 圣诞树装箱可视化工具 (Tree Packing Visualizer)
A visual and scoring calculation tool for the Santa 2025 Christmas tree packing task, providing an interactive GUI, high-precision geometric calculations, collision detection, multi-language support, and more to help validate packing schemes and intuitively display layout effects.
🎯 项目概述 (Project Overview)
该工具（This tool）核心解决圣诞树装箱任务的两大核心需求：
评分计算 (Scoring Calculation)：自动验证 CSV 格式、检测树重叠、计算分组分数 / 总分数、装箱边长（Automatically validate CSV format, detect tree overlaps, calculate group/total scores and packing side lengths）
可视化展示 (Visualization)：直观渲染指定数量（N）的圣诞树装箱布局，支持悬停查看详情、彩色区分不同树、展示 bounding square（Intuitively render packing layouts for a specified number (N) of Christmas trees, support hover for details, color-coded trees, and display bounding square）
适配中文 / 英文双语界面，采用现代化彩色 UI 设计，操作简单且交互友好（Supports Chinese/English bilingual interface with modern colorful UI design, simple operation and user-friendly interaction）
✨ 核心功能 (Core Features)
1. 多语言无缝切换 (Seamless Multi-Language Switching)
一键切换：界面内置中文 / 英文双语切换按钮，所有功能文案、提示信息、表格标题自动适配（One-click switch between Chinese/English, all UI texts, prompts, and table headers adapt automatically）
本地化体验：保留专业术语一致性（如 score / 分数、side / 边长），兼顾易用性与专业性（Localized experience with consistent professional terminology, balancing usability and professionalism）
2. CSV 导入与严格验证 (CSV Import & Strict Validation)
校验必填列：id / x / y / deg，缺失列直接报错（Validate required columns, error for missing columns）
验证数值格式：x/y/deg 必须以 s 前缀开头（如 s12.34）（Validate value format with s prefix requirement）
数值范围限制：x/y 必须在 [-100, 100] 区间内（Value range limit for x/y...
我是说你这个markdown需要能切换 我要保证看英语的也能看懂
Santa 2025 - 圣诞树装箱可视化工具 (Tree Packing Visualizer)
A visualization and scoring calculation tool for the Santa 2025 Christmas Tree Packing task, providing an interactive GUI, high-precision geometric calculations, collision detection, multi-language support, and more to validate packing schemes and intuitively display layout effects.
🎯 项目概述 (Project Overview)
中文
该工具核心解决圣诞树装箱任务的两大核心需求：
评分计算：自动验证 CSV 格式、检测树重叠、计算分组分数 / 总分数、装箱边长
可视化展示：直观渲染指定数量（N）的圣诞树装箱布局，支持悬停查看详情、彩色区分不同树、展示 bounding square
适配中文 / 英文双语界面，采用现代化彩色 UI 设计，操作简单且交互友好
English
This tool addresses two core needs of the Christmas tree packing task:
Scoring Calculation: Automatically validate CSV format, detect tree overlaps, calculate group/total scores, and packing side lengths
Visualization: Intuitively render packing layouts for a specified number (N) of Christmas trees, support hover for details, color-code different trees, and display bounding square
Supports Chinese/English bilingual interface with modern colorful UI design, simple operation and user-friendly interaction
✨ 核心功能 (Core Features)
1. CSV 导入与严格验证 (CSV Import & Strict Validation)
中文	English
校验必填列：id / x / y / deg，缺失列直接报错	Validate required columns (id/x/y/deg), throw error for missing columns
验证数值格式：x/y/deg 必须以 s 前缀开头（如 s12.34）	Validate value format: x/y/deg must start with s prefix (e.g., s12.34)
数值范围限制：x/y 必须在 [-100, 100] 区间内	Value range limit: x/y must be within [-100, 100]
错误提示：清晰的中文 / 英文错误信息，定位问题数据	Error prompts: Clear Chinese/English error messages to locate problematic data
2. 高精度评分计算 (High-Precision Scoring Calculation)
中文	English
碰撞检测：使用 Shapely STRtree 索引优化，检测树之间是否重叠（仅允许接触，不允许重叠）	Collision detection: Optimized with Shapely STRtree index to detect tree overlaps (only touching is allowed, overlapping is prohibited)
分数计算：按分组（N 值）计算装箱分数（(边长²) / N），并汇总总分数	Score calculation: Calculate packing score by group (N value) as (side_length²) / N, and sum total score
高精度运算：使用 Decimal 类型（精度 25 位）避免浮点误差，缩放因子 1e18 保证几何计算准确性	High-precision calculation: Use Decimal type (25-digit precision) to avoid floating-point errors, scale factor 1e18 ensures geometric calculation accuracy
3. 交互式可视化 (Interactive Visualization)
中文	English
彩色渲染：不同圣诞树使用差异化配色，带阴影 / 描边增强视觉效果	Color rendering: Different Christmas trees use distinct colors with shadow/stroke to enhance visual effect
布局展示：绘制圣诞树几何形状、顶部星星标记、装箱 bounding square	Layout display: Draw tree geometry, top star markers, and packing bounding square
悬停交互：鼠标悬停树体可查看原始 CSV 行数据（ID / 坐标 / 角度），侧边面板实时展示详情	Hover interaction: Hover over trees to view raw CSV row data (ID/coordinates/angle), side panel displays details in real-time
视图控制：集成 Matplotlib 导航工具栏，支持缩放 / 平移 / 保存图片	View control: Integrated Matplotlib navigation toolbar supports zoom/pan/save images
4. 分组分数管理 (Group Score Management)
中文	English
表格展示：按分组（N 值）展示分数、装箱边长，支持排序 / 滚动	Table display: Show scores and packing side lengths by group (N value), support sorting/scrolling
过滤功能：快速筛选指定分组，支持清空过滤条件	Filter function: Quickly filter specific groups, support clearing filter conditions
快捷操作：双击表格行可直接渲染对应 N 值的装箱布局	Quick operation: Double-click table rows to directly render packing layout for corresponding N value
5. 多语言与 UI 优化 (Multi-Language & UI Optimization)
中文	English
双语切换：一键切换中文 / 英文界面，所有文案自动适配	Bilingual switch: One-click switch between Chinese/English interface, all texts adapt automatically
现代化 UI：彩色卡片式布局、响应式设计、hover 样式增强	Modern UI: Colorful card layout, responsive design, enhanced hover styles
固定布局：悬停详情面板固定高度，避免界面抖动	Fixed layout: Hover detail panel with fixed height to avoid interface jitter
🛠️ 技术栈 (Tech Stack)
模块 (Module)	技术 / 库 (Technology/Library)	用途 (Purpose)
界面框架 (UI Framework)	Tkinter + ttk	构建跨平台 GUI，自定义样式 (Build cross-platform GUI with custom styles)
数据处理 (Data Processing)	Pandas	CSV 解析、分组、数据验证 (CSV parsing, grouping, data validation)
几何计算 (Geometric Calculation)	Shapely	多边形 / 旋转 / 平移 / 碰撞检测 / STRtree 索引 (Polygon/rotation/translation/collision detection/STRtree index)
可视化 (Visualization)	Matplotlib	嵌入 Tkinter 渲染圣诞树布局 (Embed in Tkinter to render tree layouts)
高精度计算 (High-Precision Calculation)	Python Decimal	避免浮点误差，保证评分准确性 (Avoid floating-point errors, ensure scoring accuracy)
🚀 快速开始 (Quick Start)
1. 环境安装 (Environment Installation)
bash
运行
# 安装依赖包 (Install dependencies)
pip install pandas shapely matplotlib
# 注意：tkinter 通常随 Python 自带，若缺失可通过系统包管理器安装 (Note: tkinter is usually included with Python; install via system package manager if missing)
# For Ubuntu/Debian: apt install python3-tk
# For Windows: Already included with Python installer
# For macOS: brew install python-tk
2. 运行工具 (Run the Tool)
bash
运行
python tree_packing_visualizer.py
3. 基础操作流程 (Basic Operation Flow)
中文
点击 📁 选择 CSV 导入装箱方案 CSV 文件
工具自动验证格式并计算所有分组分数，总分数展示在顶部
右侧面板：
选择 N 值（1~200）：通过滑块 / 输入框调整
点击 ✨ 绘制当前 N 渲染对应布局
分组表格：过滤 / 双击行快速渲染 / 刷新列表
可视化区域：鼠标悬停树体查看原始 CSV 数据，使用工具栏缩放 / 平移视图
English
Click 📁 Load CSV to import the packing scheme CSV file
The tool automatically validates the format and calculates all group scores, with total score displayed at the top
Right panel:
Select N value (1~200): Adjust via slider/input box
Click ✨ Render N to render the corresponding layout
Group table: Filter/double-click rows for quick rendering/refresh list
Visualization area: Hover over trees to view raw CSV data, use toolbar to zoom/pan view
📋 CSV 输入格式要求 (CSV Input Format Requirements)
必须列 (Required Columns)
列名 (Column)	说明 (Description)	示例 (Example)	
id	树 ID，格式为 {N:03d}_{序号}（如 002_0 表示 N=2 组的第 0 棵树）	Tree ID in format {N:03d}_{index} (e.g., 002_0 = 0th tree in N=2 group)	005_3
x	X 坐标，必须以 s 开头 (X coordinate, must start with s)	s15.678	
y	Y 坐标，必须以 s 开头 (Y coordinate, must start with s)	s-8.912	
deg	旋转角度，必须以 s 开头 (Rotation angle, must start with s)	s45.0	
格式约束 (Format Constraints)
中文	English
x/y 取值范围：[-100, 100]	x/y value range: [-100, 100]
deg 无范围限制（支持任意旋转角度）	deg has no range limit (supports any rotation angle)
编码：UTF-8	Encoding: UTF-8
分隔符：逗号（,）	Delimiter: Comma (,)
🖥️ 界面说明 (UI Overview)
区域 (Area)	功能描述 (Function Description)
顶部横幅 (Top Banner)	工具标题，固定展示 (Tool title, fixed display)
左侧可视化区 (Left Visualization Area)	圣诞树布局渲染、bounding square、Matplotlib 工具栏 (Tree layout rendering, bounding square, Matplotlib toolbar)
右侧控制面板 (Right Control Panel)	- 导入按钮：加载 CSV 文件 (Import button: Load CSV file)
- 语言切换：中文 / 英文 (Language switch: Chinese/English)
- N 选择：滑块 + 输入框 (N selection: Slider + input box)
- 悬停详情：展示鼠标指向树的原始 CSV 数据 (Hover details: Show raw CSV data of hovered tree)
- 分组表格：展示所有分组分数，支持过滤 / 双击渲染 (Group table: Show all group scores, support filter/double-click rendering)
- 刷新按钮：重新加载分组数据 (Refresh button: Reload group data)
⚠️ 注意事项 (Notes)
中文
重叠检测：若分组内存在树重叠（非接触），工具会直接报错，需修正 CSV 数据
Shapely 兼容性：适配 Shapely STRtree 多版本返回值（索引 / 几何对象）
高精度计算：所有几何计算基于 1e18 缩放因子，避免浮点精度丢失
性能优化：使用 STRtree 空间索引，大幅提升多树碰撞检测效率
English
Overlap Detection: If there are overlapping trees (not just touching) in a group, the tool will throw an error - please correct the CSV data
Shapely Compatibility: Adapt to multiple versions of Shapely STRtree return values (index/geometry objects)
High-Precision Calculation: All geometric calculations use 1e18 scale factor to avoid floating-point precision loss
Performance Optimization: Use STRtree spatial index to significantly improve collision detection efficiency for multiple trees
📄 许可证 (License)
中文
该项目为开源工具，可自由修改 / 分发，适用于 Santa 2025 圣诞树装箱任务验证场景。
English
This project is an open-source tool, free to modify/distribute, suitable for the Santa 2025 Christmas tree packing task validation scenario.
📞 反馈与建议 (Feedback & Suggestions)
中文：如有问题或优化建议，欢迎提交 Issue 或 PR
English：If you have any questions or optimization suggestions, please submit an Issue or PR

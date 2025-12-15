import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from decimal import Decimal, getcontext

import pandas as pd
from shapely import affinity
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.strtree import STRtree

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.patheffects as pe
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.patches import Polygon as MplPolygon


# ---------------- Metric implementation ----------------
getcontext().prec = 25
scale_factor = Decimal("1e18")


class ParticipantVisibleError(Exception):
    pass


class ChristmasTree:
    """Represents a single, rotatable Christmas tree of a fixed size."""

    def __init__(self, center_x="0", center_y="0", angle="0"):
        self.center_x = Decimal(center_x)
        self.center_y = Decimal(center_y)
        self.angle = Decimal(angle)

        trunk_w = Decimal("0.15")
        trunk_h = Decimal("0.2")
        base_w = Decimal("0.7")
        mid_w = Decimal("0.4")
        top_w = Decimal("0.25")
        tip_y = Decimal("0.8")
        tier_1_y = Decimal("0.5")
        tier_2_y = Decimal("0.25")
        base_y = Decimal("0.0")
        trunk_bottom_y = -trunk_h

        initial_polygon = Polygon(
            [
                (Decimal("0.0") * scale_factor, tip_y * scale_factor),
                (top_w / Decimal("2") * scale_factor, tier_1_y * scale_factor),
                (top_w / Decimal("4") * scale_factor, tier_1_y * scale_factor),
                (mid_w / Decimal("2") * scale_factor, tier_2_y * scale_factor),
                (mid_w / Decimal("4") * scale_factor, tier_2_y * scale_factor),
                (base_w / Decimal("2") * scale_factor, base_y * scale_factor),
                (trunk_w / Decimal("2") * scale_factor, base_y * scale_factor),
                (trunk_w / Decimal("2") * scale_factor, trunk_bottom_y * scale_factor),
                (-(trunk_w / Decimal("2")) * scale_factor, trunk_bottom_y * scale_factor),
                (-(trunk_w / Decimal("2")) * scale_factor, base_y * scale_factor),
                (-(base_w / Decimal("2")) * scale_factor, base_y * scale_factor),
                (-(mid_w / Decimal("4")) * scale_factor, tier_2_y * scale_factor),
                (-(mid_w / Decimal("2")) * scale_factor, tier_2_y * scale_factor),
                (-(top_w / Decimal("4")) * scale_factor, tier_1_y * scale_factor),
                (-(top_w / Decimal("2")) * scale_factor, tier_1_y * scale_factor),
            ]
        )

        rotated = affinity.rotate(initial_polygon, float(self.angle), origin=(0, 0))
        self.polygon = affinity.translate(
            rotated,
            xoff=float(self.center_x * scale_factor),
            yoff=float(self.center_y * scale_factor),
        )


def _strip_s_prefix_and_validate(df: pd.DataFrame) -> pd.DataFrame:
    required = ["id", "x", "y", "deg"]
    for c in required:
        if c not in df.columns:
            raise ParticipantVisibleError(f"CSV 缺少列：{c}")

    df = df.copy().astype(str)

    for c in ["x", "y", "deg"]:
        if not df[c].str.startswith("s").all():
            bad = df.loc[~df[c].str.startswith("s"), c].head(5).tolist()
            raise ParticipantVisibleError(f"列 {c} 存在未带 's' 前缀的值，例如：{bad}")
        df[c] = df[c].str[1:]  # remove 's'

    # enforce limits
    limit = 100
    x = df["x"].astype(float)
    y = df["y"].astype(float)
    if (x < -limit).any() or (x > limit).any() or (y < -limit).any() or (y > limit).any():
        raise ParticipantVisibleError("x 或 y 超出 [-100, 100] 限制。")

    # group id prefix
    df["tree_count_group"] = df["id"].str.split("_").str[0]
    return df


def _strtree_indices(tree: STRtree, query_geom, geom_list):
    """
    Shapely STRtree query return compatibility helper:
    - Some versions return indices
    - Some versions return geometries
    """
    res = tree.query(query_geom)
    if len(res) == 0:
        return []
    first = res[0]
    if isinstance(first, (int,)):
        return list(res)

    id_map = {id(g): i for i, g in enumerate(geom_list)}
    out = []
    for g in res:
        j = id_map.get(id(g))
        if j is not None:
            out.append(j)
    return out


def compute_scores(submission_raw: pd.DataFrame):
    """
    Returns:
      total_score: float
      group_scores: dict[group -> float]
      group_side_length: dict[group -> float]  (unscaled side length)
    """
    submission = _strip_s_prefix_and_validate(submission_raw)

    total_score = Decimal("0.0")
    group_scores = {}
    group_side = {}

    for group, df_group in submission.groupby("tree_count_group"):
        num_trees = len(df_group)

        placed_trees = [ChristmasTree(r["x"], r["y"], r["deg"]) for _, r in df_group.iterrows()]
        all_polygons = [t.polygon for t in placed_trees]
        r_tree = STRtree(all_polygons)

        # collision check
        for i, poly in enumerate(all_polygons):
            indices = _strtree_indices(r_tree, poly, all_polygons)
            for j in indices:
                if j == i:
                    continue
                if poly.intersects(all_polygons[j]) and not poly.touches(all_polygons[j]):
                    raise ParticipantVisibleError(f"组 {group} 存在树重叠（overlap）。")

        bounds = unary_union(all_polygons).bounds
        side_length_scaled = max(bounds[2] - bounds[0], bounds[3] - bounds[1])
        group_score = (Decimal(side_length_scaled) ** 2) / (scale_factor ** 2) / Decimal(num_trees)

        group_scores[group] = float(group_score)
        group_side[group] = float(Decimal(side_length_scaled) / scale_factor)
        total_score += group_score

    return float(total_score), group_scores, group_side


# ---------------- GUI ----------------
class TreePackingGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # ---------- colorful palette ----------
        self.C = {
            "bg": "#FFF4FB",
            "card": "#FFFFFF",
            "shadow": "#FFD6EA",
            "accent": "#FF3D9A",      # pink
            "accent2": "#4D96FF",     # blue
            "accent3": "#2EC4B6",     # teal
            "warn": "#FFB703",
            "text": "#1F1F2E",
            "muted": "#6B6B7A",
            "plot_bg": "#FFF9FE",
            "hl": "#FF006E",
        }
        self.TREE_COLORS = [
            "#FF3D9A", "#4D96FF", "#2EC4B6", "#FFB703",
            "#9B5DE5", "#F15BB5", "#00BBF9", "#00F5D4"
        ]

        self.lang = "zh"
        self.T = self._build_i18n()

        self.title(self.T["title"])
        self.geometry("1240x800")
        self.minsize(1100, 720)
        self.configure(bg=self.C["bg"])

        self.csv_path = None
        self.df_raw = None
        self.total_score = None
        self.group_scores = None
        self.group_side = None

        # state
        self._syncing_n = False
        self._hover_items = []
        self._last_hover_item = None

        self._build_style()
        self._build_ui()

    # ---------- i18n ----------
    def _build_i18n(self):
        return {
            "zh": {
                "title": "Santa 2025 - 圣诞树装箱可视化（彩色版）",
                "banner": "🎄 Santa 2025  ·  Tree Packing Visualizer",
                "load_csv": "📁 选择 CSV",
                "render": "✨ 绘制当前 N",
                "refresh": "🔄 刷新列表",
                "file_none": "还没有加载 CSV",
                "controls": "控制面板",
                "groups": "组分数一览",
                "n_label": "圣诞树数量 N (1~200)",
                "lang": "语言",
                "total": "所有组分数总和 (Total score)：",
                "current": "当前组分数：",
                "hint": "提示：id 前缀例如 002_0 / 002_1 表示 N=2 的组（group='002'）",
                "ok": "成功",
                "loaded": "CSV 已加载并计算分数完成。",
                "warn_load": "请先加载 CSV。",
                "input_err": "输入错误",
                "load_fail": "加载失败",
                "render_fail": "制图/计算失败",
                "not_found": "CSV 里找不到 group='{group}'（也就是 N={n}）的数据。",
                "group": "group",
                "col_n": "N",
                "score": "score",
                "side": "边长",
                "filter": "🔎 过滤 group：",
                "clear": "清空",
                "showing": "显示 {shown}/{total} 个组",
                "hover_title": "悬停信息（CSV 原始行）",
                "hover_ph": "把鼠标移到树上查看 CSV 行数据（右侧可滚动）",
            },
            "en": {
                "title": "Santa 2025 - Tree Packing Visualizer (Colorful)",
                "banner": "🎄 Santa 2025  ·  Tree Packing Visualizer",
                "load_csv": "📁 Load CSV",
                "render": "✨ Render N",
                "refresh": "🔄 Refresh",
                "file_none": "No CSV loaded",
                "controls": "Controls",
                "groups": "Group Scores",
                "n_label": "Tree count N (1~200)",
                "lang": "Language",
                "total": "Total score (sum of all groups): ",
                "current": "Current group score: ",
                "hint": "Hint: id prefix like 002_0 / 002_1 means N=2 group (group='002')",
                "ok": "Success",
                "loaded": "CSV loaded and scores computed.",
                "warn_load": "Please load a CSV first.",
                "input_err": "Input error",
                "load_fail": "Load failed",
                "render_fail": "Render/compute failed",
                "not_found": "Group '{group}' (N={n}) not found in CSV.",
                "group": "group",
                "col_n": "N",
                "score": "score",
                "side": "side",
                "filter": "🔎 Filter group: ",
                "clear": "Clear",
                "showing": "Showing {shown}/{total} groups",
                "hover_title": "Hover (raw CSV row)",
                "hover_ph": "Hover a tree to see CSV row data (scroll on the right)",
            },
        }[self.lang]

    def _tr(self, key, **kwargs):
        s = self.T.get(key, key)
        if kwargs:
            try:
                return s.format(**kwargs)
            except Exception:
                return s
        return s

    # ---------- fixed hover panel helpers ----------
    def _set_hover_text(self, s: str):
        if not hasattr(self, "hover_text"):
            return
        self.hover_text.config(state="normal")
        self.hover_text.delete("1.0", "end")
        self.hover_text.insert("1.0", s)
        self.hover_text.config(state="disabled")

    # ---------- modern colorful style ----------
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        self.option_add("*Font", ("Segoe UI", 10))

        style.configure("TFrame", background=self.C["bg"])
        style.configure("Card.TFrame", background=self.C["card"], padding=12)
        style.configure("Title.TLabel", background=self.C["card"], foreground=self.C["text"], font=("Segoe UI", 12, "bold"))
        style.configure("Muted.TLabel", background=self.C["card"], foreground=self.C["muted"])

        style.configure(
            "Treeview",
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground=self.C["text"],
            rowheight=26,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background="#FFE3F1",
            foreground=self.C["text"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.map("Treeview", background=[("selected", "#BDE0FE")], foreground=[("selected", self.C["text"])])
        style.configure("TScale", background=self.C["card"])

    # ---------- UI ----------
    def _build_ui(self):
        banner = tk.Frame(self, bg=self.C["accent2"], height=52)
        banner.pack(fill=tk.X, side=tk.TOP)
        tk.Label(
            banner, text=self._tr("banner"), bg=self.C["accent2"], fg="white",
            font=("Segoe UI", 13, "bold")
        ).pack(side=tk.LEFT, padx=14, pady=10)

        outer = ttk.Frame(self, padding=12)
        outer.pack(fill=tk.BOTH, expand=True)

        paned = ttk.Panedwindow(outer, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left (plot)
        left = ttk.Frame(paned, style="Card.TFrame")
        paned.add(left, weight=4)

        header = ttk.Frame(left, style="Card.TFrame")
        header.pack(fill=tk.X, pady=(0, 8))

        self.file_label = ttk.Label(header, text=self._tr("file_none"), foreground=self.C["muted"], background=self.C["card"])
        self.file_label.pack(side=tk.LEFT)

        self.lbl_total = ttk.Label(header, text=self._tr("total") + "-", style="Title.TLabel")
        self.lbl_total.pack(side=tk.RIGHT)

        fig = Figure(figsize=(7.2, 6.0), dpi=100, facecolor=self.C["plot_bg"])
        self.ax = fig.add_subplot(111)
        self.ax.set_title("Packing Visualization", fontsize=12, fontweight="bold")
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.set_facecolor(self.C["plot_bg"])
        self.ax.grid(True, alpha=0.35)

        self.canvas = FigureCanvasTkAgg(fig, master=left)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, left, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(fill=tk.X, pady=(6, 0))

        status = ttk.Frame(left, style="Card.TFrame")
        status.pack(fill=tk.X, pady=(8, 0))

        self.lbl_current = ttk.Label(status, text=self._tr("current") + "-", background=self.C["card"], foreground=self.C["text"])
        self.lbl_current.pack(side=tk.LEFT)

        self.lbl_hint = ttk.Label(status, text=self._tr("hint"), style="Muted.TLabel")
        self.lbl_hint.pack(side=tk.RIGHT)

        # tooltip on plot (does NOT affect layout)
        self._anno = self.ax.annotate(
            "",
            xy=(0, 0),
            xytext=(14, 14),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=self.C["accent"], alpha=0.96),
            arrowprops=dict(arrowstyle="->", color=self.C["accent"]),
        )
        self._anno.set_visible(False)
        self.canvas.mpl_connect("motion_notify_event", self._on_motion)

        # Right (controls)
        right = ttk.Frame(paned, style="Card.TFrame", width=390)
        paned.add(right, weight=1)

        ttk.Label(right, text=self._tr("controls"), style="Title.TLabel").pack(anchor="w")

        btn_row = tk.Frame(right, bg=self.C["card"])
        btn_row.pack(fill=tk.X, pady=(10, 6))

        self.btn_load = tk.Button(
            btn_row, text=self._tr("load_csv"),
            bg=self.C["accent2"], fg="white", activebackground="#377DFF",
            relief="flat", padx=12, pady=10, font=("Segoe UI", 10, "bold"),
            command=self.on_load_csv
        )
        self.btn_load.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Language toggle
        lang_row = tk.Frame(right, bg=self.C["card"])
        lang_row.pack(fill=tk.X, pady=(8, 0))

        tk.Label(lang_row, text=self._tr("lang") + ":", bg=self.C["card"], fg=self.C["text"],
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        self.lang_var = tk.StringVar(value=self.lang)
        tk.Radiobutton(
            lang_row, text="中文", value="zh", variable=self.lang_var,
            bg=self.C["card"], fg=self.C["text"], selectcolor=self.C["shadow"],
            command=self._apply_lang
        ).pack(side=tk.LEFT, padx=(10, 0))
        tk.Radiobutton(
            lang_row, text="EN", value="en", variable=self.lang_var,
            bg=self.C["card"], fg=self.C["text"], selectcolor=self.C["shadow"],
            command=self._apply_lang
        ).pack(side=tk.LEFT, padx=(10, 0))

        # N slider + entry
        n_wrap = tk.Frame(right, bg=self.C["card"])
        n_wrap.pack(fill=tk.X, pady=(10, 0))

        tk.Label(n_wrap, text=self._tr("n_label"), bg=self.C["card"], fg=self.C["text"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")

        n_row = tk.Frame(n_wrap, bg=self.C["card"])
        n_row.pack(fill=tk.X, pady=(6, 0))

        self.n_var = tk.StringVar(value="2")
        self.n_scale = ttk.Scale(n_row, from_=1, to=200, orient=tk.HORIZONTAL, command=self._on_scale_move)
        self.n_scale.set(2)
        self.n_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.entry_n = tk.Entry(n_row, textvariable=self.n_var, width=6, justify="center",
                                relief="flat", bg="#FFFFFF", fg=self.C["text"])
        self.entry_n.pack(side=tk.LEFT, padx=(10, 0), ipady=6)
        self.n_var.trace_add("write", self._on_entry_change)

        self.btn_render = tk.Button(
            right, text=self._tr("render"),
            bg=self.C["accent"], fg="white", activebackground="#FF2D8C",
            relief="flat", padx=12, pady=10, font=("Segoe UI", 10, "bold"),
            command=self.on_render
        )
        self.btn_render.pack(fill=tk.X, pady=(10, 10))

        # ---- Hover panel (FIXED HEIGHT, NO RESIZE / NO MOUSE JUMP) ----
        self.lbl_hover_title = tk.Label(
            right, text=self._tr("hover_title"),
            bg=self.C["card"], fg=self.C["text"],
            font=("Segoe UI", 10, "bold")
        )
        self.lbl_hover_title.pack(anchor="w", pady=(0, 0))

        hover_box = tk.Frame(right, bg=self.C["card"], height=180)
        hover_box.pack(fill=tk.X, pady=(6, 10))
        hover_box.pack_propagate(False)  # IMPORTANT: prevent resizing caused by content

        sb2 = tk.Scrollbar(hover_box)
        sb2.pack(side=tk.RIGHT, fill=tk.Y)

        self.hover_text = tk.Text(
            hover_box,
            wrap="word",
            yscrollcommand=sb2.set,
            bg="#FFFFFF",
            fg=self.C["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.C["shadow"],
        )
        self.hover_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb2.config(command=self.hover_text.yview)
        self._set_hover_text(self._tr("hover_ph"))

        ttk.Separator(right, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        ttk.Label(right, text=self._tr("groups"), style="Title.TLabel").pack(anchor="w")

        # Filter row
        filt_row = tk.Frame(right, bg=self.C["card"])
        filt_row.pack(fill=tk.X, pady=(10, 6))

        tk.Label(filt_row, text=self._tr("filter"), bg=self.C["card"], fg=self.C["text"],
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        self.filter_var = tk.StringVar(value="")
        self.filter_entry = tk.Entry(filt_row, textvariable=self.filter_var, relief="flat", bg="#FFFFFF", fg=self.C["text"])
        self.filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 8), ipady=6)
        self.filter_entry.bind("<KeyRelease>", lambda e: self.refresh_group_table())

        self.btn_clear = tk.Button(
            filt_row, text=self._tr("clear"),
            bg=self.C["warn"], fg="white", activebackground="#FF9F1C",
            relief="flat", padx=10, pady=6, font=("Segoe UI", 9, "bold"),
            command=self._clear_filter
        )
        self.btn_clear.pack(side=tk.RIGHT)

        self.lbl_showing = tk.Label(
            right, text=self._tr("showing", shown=0, total=0),
            bg=self.C["card"], fg=self.C["muted"], font=("Segoe UI", 9)
        )
        self.lbl_showing.pack(anchor="w", pady=(0, 6))

        # Treeview + scrollbar
        table_wrap = ttk.Frame(right, style="Card.TFrame")
        table_wrap.pack(fill=tk.BOTH, expand=True)

        cols = ("group", "n", "score", "side")
        self.treeview = ttk.Treeview(table_wrap, columns=cols, show="headings", height=18)

        self.treeview.heading("group", text=self._tr("group"))
        self.treeview.heading("n", text=self._tr("col_n"))
        self.treeview.heading("score", text=self._tr("score"))
        self.treeview.heading("side", text=self._tr("side"))

        self.treeview.column("group", width=70, anchor="center")
        self.treeview.column("n", width=55, anchor="center")
        self.treeview.column("score", width=140, anchor="e")
        self.treeview.column("side", width=80, anchor="e")

        sb = ttk.Scrollbar(table_wrap, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=sb.set)

        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.treeview.bind("<Double-1>", self._on_table_double_click)

        self.btn_refresh = tk.Button(
            right, text=self._tr("refresh"),
            bg=self.C["accent3"], fg="white", activebackground="#24B7AA",
            relief="flat", padx=12, pady=10, font=("Segoe UI", 10, "bold"),
            command=self.refresh_group_table
        )
        self.btn_refresh.pack(fill=tk.X, pady=(10, 0))

    # ---------- Lang apply ----------
    def _apply_lang(self):
        self.lang = self.lang_var.get().strip() if self.lang_var.get() else "zh"
        self.T = self._build_i18n()

        self.title(self._tr("title"))
        self.btn_load.config(text=self._tr("load_csv"))
        self.btn_render.config(text=self._tr("render"))
        self.btn_refresh.config(text=self._tr("refresh"))
        self.btn_clear.config(text=self._tr("clear"))

        self.file_label.config(text=self._tr("file_none") if not self.csv_path else os.path.basename(self.csv_path))
        self.lbl_hint.config(text=self._tr("hint"))

        self.treeview.heading("group", text=self._tr("group"))
        self.treeview.heading("n", text=self._tr("col_n"))
        self.treeview.heading("score", text=self._tr("score"))
        self.treeview.heading("side", text=self._tr("side"))

        if hasattr(self, "lbl_hover_title"):
            self.lbl_hover_title.config(text=self._tr("hover_title"))
        self._set_hover_text(self._tr("hover_ph"))

        if self.total_score is None:
            self.lbl_total.config(text=self._tr("total") + "-")
        else:
            self.lbl_total.config(text=self._tr("total") + f"{self.total_score:.12f}")

        self.refresh_group_table()

    # ---------- Filter ----------
    def _clear_filter(self):
        self.filter_var.set("")
        self.refresh_group_table()

    # ---------- Slider / Entry sync ----------
    def _on_scale_move(self, val):
        if self._syncing_n:
            return
        try:
            n = int(round(float(val)))
            self._syncing_n = True
            self.n_var.set(str(n))
        finally:
            self._syncing_n = False

    def _on_entry_change(self, *_):
        if self._syncing_n:
            return
        s = self.n_var.get().strip()
        if not s.isdigit():
            return
        n = int(s)
        n = max(1, min(200, n))
        try:
            self._syncing_n = True
            self.n_scale.set(n)
        finally:
            self._syncing_n = False

    # ---------- Actions ----------
    def on_load_csv(self):
        path = filedialog.askopenfilename(
            title=self._tr("load_csv"),
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            df = pd.read_csv(path)
            total, group_scores, group_side = compute_scores(df)

            self.csv_path = path
            self.df_raw = df
            self.total_score = total
            self.group_scores = group_scores
            self.group_side = group_side

            self.file_label.config(text=os.path.basename(path))
            self.lbl_total.config(text=self._tr("total") + f"{self.total_score:.12f}")

            self.refresh_group_table()
            messagebox.showinfo(self._tr("ok"), self._tr("loaded"))
        except Exception as e:
            messagebox.showerror(self._tr("load_fail"), str(e))

    def refresh_group_table(self):
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        if not self.group_scores:
            self.lbl_showing.config(text=self._tr("showing", shown=0, total=0))
            return

        flt = (self.filter_var.get() or "").strip().lower()
        all_groups = list(self.group_scores.keys())
        total = len(all_groups)

        def group_key(g):
            try:
                return int(g)
            except Exception:
                return 10**9

        groups_sorted = sorted(all_groups, key=group_key)
        if flt:
            groups_sorted = [g for g in groups_sorted if flt in str(g).lower()]

        shown = len(groups_sorted)
        self.lbl_showing.config(text=self._tr("showing", shown=shown, total=total))

        for idx, g in enumerate(groups_sorted):
            n = int(g) if g.isdigit() else "-"
            sc = self.group_scores[g]
            side = self.group_side.get(g, None)
            side_txt = f"{side:.6f}" if side is not None else "-"

            tag = "odd" if idx % 2 else "even"
            self.treeview.insert("", tk.END, values=(g, n, f"{sc:.12f}", side_txt), tags=(tag,))

        self.treeview.tag_configure("even", background="#FFF1FA")
        self.treeview.tag_configure("odd", background="#EAF4FF")

    def _on_table_double_click(self, _evt):
        sel = self.treeview.selection()
        if not sel:
            return
        vals = self.treeview.item(sel[0], "values")
        if not vals:
            return
        g = str(vals[0])
        if g.isdigit():
            n = int(g)
            self.n_scale.set(n)
            self.n_var.set(str(n))
            self.on_render()

    def on_render(self):
        if self.df_raw is None:
            messagebox.showwarning(self._tr("input_err"), self._tr("warn_load"))
            return

        try:
            n = int(self.n_var.get().strip())
            if not (1 <= n <= 200):
                raise ValueError("N must be 1~200" if self.lang == "en" else "N 必须在 1~200。")
        except Exception as e:
            messagebox.showerror(self._tr("input_err"), str(e))
            return

        group = f"{n:03d}"

        try:
            submission = _strip_s_prefix_and_validate(self.df_raw)
            df_group = submission[submission["tree_count_group"] == group].copy()
            if df_group.empty:
                raise ParticipantVisibleError(self._tr("not_found", group=group, n=n))

            # raw CSV row map (keeps 's' prefix + any extra columns)
            raw_tmp = self.df_raw.copy().astype(str)
            raw_tmp["tree_count_group"] = raw_tmp["id"].astype(str).str.split("_").str[0]
            df_group_raw = raw_tmp[raw_tmp["tree_count_group"] == group].copy()
            raw_map = {str(r["id"]): r.to_dict() for _, r in df_group_raw.iterrows()}

            trees = [ChristmasTree(r["x"], r["y"], r["deg"]) for _, r in df_group.iterrows()]
            polys_scaled = [t.polygon for t in trees]

            bounds = unary_union(polys_scaled).bounds
            minx, miny, maxx, maxy = bounds
            width = maxx - minx
            height = maxy - miny
            side_scaled = max(width, height)

            group_score = self.group_scores.get(group)
            if group_score is None:
                group_score = float(
                    (Decimal(side_scaled) ** 2) / (scale_factor ** 2) / Decimal(len(df_group))
                )

            # Redraw
            self.ax.clear()
            self.ax.set_title(f"N={n} (group {group}) Packing", fontsize=12, fontweight="bold")
            self.ax.set_aspect("equal", adjustable="box")
            self.ax.set_facecolor(self.C["plot_bg"])
            self.ax.grid(True, alpha=0.35)

            # reset hover
            self._hover_items = []
            self._last_hover_item = None
            self._anno.set_visible(False)
            self._set_hover_text(self._tr("hover_ph"))

            # draw trees
            for i, ((_, r), poly) in enumerate(zip(df_group.iterrows(), polys_scaled), start=1):
                x, y = poly.exterior.xy
                x = [v / float(scale_factor) for v in x]
                y = [v / float(scale_factor) for v in y]

                color = self.TREE_COLORS[(i - 1) % len(self.TREE_COLORS)]
                patch = MplPolygon(list(zip(x, y)), closed=True)
                patch.set_facecolor(color)
                patch.set_edgecolor("#FFFFFF")
                patch.set_alpha(0.48)
                patch.set_linewidth(1.6)
                patch.set_zorder(3)
                patch.set_path_effects([
                    pe.SimplePatchShadow(offset=(2, -2), alpha=0.25),
                    pe.Normal()
                ])
                self.ax.add_patch(patch)

                # star at top tip
                tip_k = max(range(len(y)), key=lambda k: y[k])
                self.ax.scatter(
                    [x[tip_k]], [y[tip_k]],
                    marker="*", s=130,
                    color="#FFD166",
                    edgecolors="#1F1F2E",
                    linewidths=0.8,
                    zorder=6
                )

                rid = str(r["id"])
                meta = {
                    "idx": i,
                    "id": rid,
                    "row_clean": r.to_dict(),
                    "row_raw": raw_map.get(rid, None),
                }
                orig = {"alpha": 0.48, "lw": 1.6, "ec": "#FFFFFF", "z": 3}
                self._hover_items.append({"patch": patch, "meta": meta, "orig": orig})

            # Bounding square
            side = side_scaled
            sq = Polygon(
                [(minx, miny), (minx + side, miny), (minx + side, miny + side), (minx, miny + side)]
            )
            sx, sy = sq.exterior.xy
            sx = [v / float(scale_factor) for v in sx]
            sy = [v / float(scale_factor) for v in sy]
            self.ax.plot(sx, sy, linewidth=2.6, color=self.C["accent2"], zorder=2)

            # View limits with padding
            pad = float(Decimal(side) / scale_factor) * 0.08 + 0.05
            minx_f = float(Decimal(minx) / scale_factor) - pad
            miny_f = float(Decimal(miny) / scale_factor) - pad
            side_f = float(Decimal(side) / scale_factor) + 2 * pad
            self.ax.set_xlim(minx_f, minx_f + side_f)
            self.ax.set_ylim(miny_f, miny_f + side_f)

            self.canvas.draw()

            self.lbl_current.config(text=self._tr("current") + f"{group_score:.12f}   (N={n})")
            self.lbl_total.config(text=self._tr("total") + f"{self.total_score:.12f}")

        except Exception as e:
            messagebox.showerror(self._tr("render_fail"), str(e))

    # ---------- Hover ----------
    def _on_motion(self, event):
        if event.inaxes != self.ax or not self._hover_items:
            self._hide_hover()
            return

        hovered = None
        for item in self._hover_items:
            patch = item["patch"]
            contains, _ = patch.contains(event)
            if contains:
                hovered = item
                break

        if hovered is None:
            self._hide_hover()
            return

        if self._last_hover_item is not None and self._last_hover_item is not hovered:
            self._restore_item_style(self._last_hover_item)

        patch = hovered["patch"]
        patch.set_alpha(0.78)
        patch.set_linewidth(3.0)
        patch.set_edgecolor(self.C["hl"])
        patch.set_zorder(10)

        meta = hovered["meta"]
        self._anno.xy = (event.xdata, event.ydata)

        row = meta["row_raw"] if meta.get("row_raw") else meta.get("row_clean", {})
        keys_first = ["id", "x", "y", "deg"]
        keys = [k for k in keys_first if k in row] + [k for k in row.keys() if k not in keys_first and k != "tree_count_group"]

        header = f"Tree #{meta['idx']} (CSV row)" if self.lang == "en" else f"第 {meta['idx']} 棵（CSV 行数据）"
        full_text = "\n".join([header] + [f"{k}: {row.get(k, '')}" for k in keys])
        self._set_hover_text(full_text)

        # compact tooltip
        tip = (
            f"#{meta['idx']}  id: {row.get('id','')}\n"
            f"x: {row.get('x','')}\n"
            f"y: {row.get('y','')}\n"
            f"deg: {row.get('deg','')}"
        )
        self._anno.set_text(tip)
        self._anno.set_visible(True)

        self._last_hover_item = hovered
        self.canvas.draw_idle()

    def _restore_item_style(self, item):
        try:
            patch = item["patch"]
            orig = item["orig"]
            patch.set_alpha(orig["alpha"])
            patch.set_linewidth(orig["lw"])
            patch.set_edgecolor(orig["ec"])
            patch.set_zorder(orig.get("z", 3))
        except Exception:
            pass

    def _hide_hover(self):
        if self._anno.get_visible():
            self._anno.set_visible(False)
        if self._last_hover_item is not None:
            self._restore_item_style(self._last_hover_item)
            self._last_hover_item = None
        self._set_hover_text(self._tr("hover_ph"))
        self.canvas.draw_idle()


def main():
    app = TreePackingGUI()
    app.mainloop()


if __name__ == "__main__":
    main()

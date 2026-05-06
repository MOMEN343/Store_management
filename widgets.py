"""
مكونات UI مشتركة – RTL Arabic
"""
import tkinter as tk
from tkinter import ttk
import theme as T


# ═══════════════════════════════════════════════════════════════════════════════
#  Labels
# ═══════════════════════════════════════════════════════════════════════════════
def lbl(parent, text, *, font=None, fg=None, bg=None, anchor="e", **kw):
    return tk.Label(
        parent, text=text,
        font=font or T.FONT_BODY,
        fg=fg or T.TEXT_PRIMARY,
        bg=bg or T.BG_CARD,
        anchor=anchor,
        justify="right",
        **kw
    )

def lbl_h1(parent, text, **kw):
    return lbl(parent, text, font=T.FONT_H1, **kw)

def lbl_h2(parent, text, **kw):
    return lbl(parent, text, font=T.FONT_H2, **kw)

def lbl_h3(parent, text, **kw):
    return lbl(parent, text, font=T.FONT_H3, **kw)

def lbl_muted(parent, text, **kw):
    return lbl(parent, text, fg=T.TEXT_SECOND, **kw)

def lbl_accent(parent, text, **kw):
    return lbl(parent, text, fg=T.ACCENT, **kw)


# ═══════════════════════════════════════════════════════════════════════════════
#  زر مخصص مع Hover effect
# ═══════════════════════════════════════════════════════════════════════════════
class ModernButton(tk.Button):
    def __init__(self, parent, text, style="primary", command=None, icon=None, **kw):
        styles = {
            "primary"  : T.BTN_PRIMARY,
            "danger"   : T.BTN_DANGER,
            "secondary": T.BTN_SECONDARY,
            "warning"  : T.BTN_WARNING,
            "info"     : T.BTN_INFO,
        }
        s = styles.get(style, T.BTN_PRIMARY)
        full_text = f"{text}  {icon}" if icon else text
        super().__init__(
            parent,
            text=full_text,
            bg=s["bg"], fg=s["fg"],
            activebackground=s["abg"],
            activeforeground=s["fg"],
            font=T.FONT_BTN,
            relief="flat", bd=0,
            padx=16, pady=8,
            cursor="hand2",
            command=command,
            **kw
        )
        self._bg = s["bg"]
        self._abg = s["abg"]
        self.bind("<Enter>", lambda e: self.config(bg=self._abg))
        self.bind("<Leave>", lambda e: self.config(bg=self._bg))


# ═══════════════════════════════════════════════════════════════════════════════
#  حقل إدخال مخصص
# ═══════════════════════════════════════════════════════════════════════════════
class ModernEntry(tk.Entry):
    def __init__(self, parent, placeholder="", **kw):
        super().__init__(
            parent,
            bg=T.BG_INPUT, fg=T.TEXT_PRIMARY,
            insertbackground=T.ACCENT,
            relief="flat", bd=0,
            font=T.FONT_INPUT,
            justify="right",
            highlightthickness=2,
            highlightbackground=T.BORDER,
            highlightcolor=T.BORDER_FOCUS,
            **kw
        )
        self._placeholder = placeholder
        self._has_placeholder = False
        if placeholder:
            self._show_placeholder()
            self.bind("<FocusIn>",  self._on_focus_in)
            self.bind("<FocusOut>", self._on_focus_out)

    def _show_placeholder(self):
        self.insert(0, self._placeholder)
        self.config(fg=T.TEXT_MUTED)
        self._has_placeholder = True

    def _on_focus_in(self, _):
        if self._has_placeholder:
            self.delete(0, "end")
            self.config(fg=T.TEXT_PRIMARY)
            self._has_placeholder = False

    def _on_focus_out(self, _):
        if not self.get():
            self._show_placeholder()

    def get_value(self):
        if self._has_placeholder:
            return ""
        return self.get()


# ═══════════════════════════════════════════════════════════════════════════════
#  Combobox
# ═══════════════════════════════════════════════════════════════════════════════
class ModernCombo(ttk.Combobox):
    def __init__(self, parent, values=None, **kw):
        super().__init__(parent, values=values or [], **kw)
        self.configure(font=T.FONT_INPUT, justify="right")


# ═══════════════════════════════════════════════════════════════════════════════
#  بطاقة
# ═══════════════════════════════════════════════════════════════════════════════
class Card(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(
            parent, bg=T.BG_CARD,
            highlightthickness=1, highlightbackground=T.BORDER,
            **kw
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  بطاقة إحصاء KPI
# ═══════════════════════════════════════════════════════════════════════════════
class KpiCard(tk.Frame):
    def __init__(self, parent, title, value, icon="", color=None, **kw):
        super().__init__(parent, bg=T.BG_CARD,
                         highlightthickness=1, highlightbackground=color or T.BORDER, **kw)
        color = color or T.ACCENT
        top = tk.Frame(self, bg=T.BG_CARD)
        top.pack(fill="x", pady=(T.PAD, 4), padx=T.PAD)
        tk.Label(top, text=icon, font=(T.FONT_AR, 22), bg=T.BG_CARD, fg=color).pack(side="right")

        self._val_lbl = tk.Label(self, text=str(value), font=T.FONT_KPI_VAL, bg=T.BG_CARD, fg=color)
        self._val_lbl.pack(pady=(0, 2))
        tk.Label(self, text=title, font=T.FONT_KPI_LBL, bg=T.BG_CARD, fg=T.TEXT_SECOND).pack(pady=(0, T.PAD))

    def update_value(self, v):
        self._val_lbl.config(text=str(v))


# ═══════════════════════════════════════════════════════════════════════════════
#  جدول بيانات Treeview
# ═══════════════════════════════════════════════════════════════════════════════
def make_table(parent, columns):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
                    background=T.TBL_ROW_ODD,
                    foreground=T.TEXT_PRIMARY,
                    rowheight=36,
                    fieldbackground=T.TBL_ROW_ODD,
                    bordercolor=T.TBL_BORDER,
                    borderwidth=0,
                    font=T.FONT_BODY)
    style.configure("Custom.Treeview.Heading",
                    background=T.TBL_HEAD_BG,
                    foreground=T.TBL_HEAD_FG,
                    font=T.FONT_H3,
                    relief="flat",
                    borderwidth=0)
    style.map("Custom.Treeview",
              background=[("selected", T.TBL_SEL_BG)],
              foreground=[("selected", T.TBL_SEL_FG)])
    style.map("Custom.Treeview.Heading",
              background=[("active", T.BG_HOVER)])

    frame = tk.Frame(parent, bg=T.BG_DARK)
    col_ids = [c["id"] for c in columns]
    tree = ttk.Treeview(frame, columns=col_ids, show="headings",
                        style="Custom.Treeview")
    for col in columns:
        tree.heading(col["id"], text=col["text"])
        tree.column(col["id"],
                    width=col.get("width", 100),
                    anchor=col.get("anchor", "center"),
                    minwidth=50)

    vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    tree.tag_configure("odd",     background=T.TBL_ROW_ODD)
    tree.tag_configure("even",    background=T.TBL_ROW_EVEN)
    tree.tag_configure("danger",  background="#2A0A0F", foreground=T.DANGER)
    tree.tag_configure("warning", background="#2A1F0A", foreground=T.WARNING)
    tree.tag_configure("success", background="#0A2A15", foreground=T.SUCCESS)

    return frame, tree


def refresh_table(tree, rows, formatters=None):
    for item in tree.get_children():
        tree.delete(item)
    for i, row in enumerate(rows):
        tag = "odd" if i % 2 == 0 else "even"
        values = formatters(row) if formatters else list(row)
        tree.insert("", "end", values=values, tags=(tag,))


# ═══════════════════════════════════════════════════════════════════════════════
#  نافذة حوار
# ═══════════════════════════════════════════════════════════════════════════════
class Dialog(tk.Toplevel):
    def __init__(self, parent, title, width=520, height=440):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=T.BG_DARK)
        self.resizable(False, False)
        self.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width()  - width)  // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{px}+{py}")
        self.grab_set()

    def add_title(self, text):
        tk.Label(self, text=text, font=T.FONT_H2,
                 bg=T.BG_DARK, fg=T.ACCENT, anchor="center",
                 justify="center").pack(pady=(T.PAD_LARGE, T.PAD), fill="x")

    def add_separator(self):
        tk.Frame(self, bg=T.BORDER, height=1).pack(fill="x", padx=T.PAD)


# ═══════════════════════════════════════════════════════════════════════════════
#  شريط بحث
# ═══════════════════════════════════════════════════════════════════════════════
class SearchBar(tk.Frame):
    def __init__(self, parent, on_search, placeholder="...بحث", **kw):
        super().__init__(parent, bg=T.BG_CARD, **kw)
        self._cb = on_search
        ModernButton(self, "بحث", style="secondary",
                     command=self._trigger).pack(side="left", padx=4)
        self._entry = ModernEntry(self, placeholder=placeholder, width=30)
        self._entry.pack(side="right", fill="x", expand=True, ipady=6, padx=(4, 8))
        self._entry.bind("<KeyRelease>", lambda e: self._trigger())
        tk.Label(self, text=T.ICON["search"], bg=T.BG_CARD,
                 fg=T.TEXT_SECOND, font=T.FONT_BODY).pack(side="right", padx=(8, 0))

    def _trigger(self):
        self._cb(self._entry.get_value())

    def get(self):
        return self._entry.get_value()


# ═══════════════════════════════════════════════════════════════════════════════
#  شريط تاريخ (من – إلى)
# ═══════════════════════════════════════════════════════════════════════════════
class DateRangeBar(tk.Frame):
    def __init__(self, parent, on_filter, **kw):
        super().__init__(parent, bg=T.BG_CARD, **kw)
        self._cb = on_filter

        ModernButton(self, "الكل", style="secondary", command=self._clear).pack(side="left", padx=4)
        ModernButton(self, "تصفية", style="info", command=self._trigger).pack(side="left", padx=4)

        self._to = ModernEntry(self, width=12)
        self._to.pack(side="left", padx=4, ipady=5)
        lbl(self, "إلى:", bg=T.BG_CARD).pack(side="left", padx=4)

        self._from = ModernEntry(self, width=12)
        self._from.pack(side="left", padx=4, ipady=5)
        lbl(self, "📅  من:", bg=T.BG_CARD).pack(side="left", padx=(4, 8))

    def _trigger(self):
        self._cb(self._from.get() or None, self._to.get() or None)

    def _clear(self):
        self._from.delete(0, "end")
        self._to.delete(0, "end")
        self._cb(None, None)

    def get(self):
        return self._from.get() or None, self._to.get() or None


# ═══════════════════════════════════════════════════════════════════════════════
#  رسائل
# ═══════════════════════════════════════════════════════════════════════════════
def confirm(parent, msg="هل أنت متأكد؟"):
    from tkinter import messagebox
    return messagebox.askyesno("تأكيد", msg, parent=parent)

def alert_error(parent, msg):
    from tkinter import messagebox
    messagebox.showerror("خطأ", msg, parent=parent)

def alert_info(parent, msg):
    from tkinter import messagebox
    messagebox.showinfo("تم", msg, parent=parent)

def alert_warning(parent, msg):
    from tkinter import messagebox
    messagebox.showwarning("تنبيه", msg, parent=parent)


# ═══════════════════════════════════════════════════════════════════════════════
#  تنسيقات
# ═══════════════════════════════════════════════════════════════════════════════
def fmt_money(val):
    try:
        return f"₪ {float(val):,.2f}"
    except Exception:
        return str(val)

def fmt_qty(val):
    try:
        return f"{int(val):,}"
    except Exception:
        return str(val)

def fmt_date(val):
    if not val:
        return ""
    try:
        from datetime import datetime
        return datetime.strptime(val, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return val


# ═══════════════════════════════════════════════════════════════════════════════
#  Form helpers – RTL row (label right, entry left)
# ═══════════════════════════════════════════════════════════════════════════════
def form_row(parent, label_text, widget, row_num):
    """صف واحد في النموذج: العنوان على اليمين والحقل على اليسار"""
    tk.Label(parent, text=label_text, font=T.FONT_LABEL,
             bg=T.BG_DARK, fg=T.TEXT_SECOND, anchor="e",
             width=16).grid(row=row_num, column=1, sticky="e", pady=7, padx=(4, 8))
    widget.grid(row=row_num, column=0, sticky="ew", pady=7, padx=(8, 4), ipady=7)

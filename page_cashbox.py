"""
صفحة الصندوق – CustomTkinter
"""
import customtkinter as ctk
from datetime import date
import os
import database as db
from date_picker import show_date_picker


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_DIR = os.path.join(BASE_DIR, "icons")

FONT_HDR = "Thmanyah Sans"
FONT_REG = "Cairo"
FONT = FONT_REG


def get_icon(name, size=(24, 24)):
    try:
        from PIL import Image
        return ctk.CTkImage(
            light_image=Image.open(os.path.join(ICON_DIR, f"{name}_light.png")),
            dark_image=Image.open(os.path.join(ICON_DIR, f"{name}_dark.png")),
            size=size
        )
    except:
        return None


def get_white_icon(name, size=(24, 24)):
    try:
        from PIL import Image
        img = Image.open(os.path.join(ICON_DIR, f"{name}_dark.png")).convert("RGBA")
        _, _, _, a = img.split()
        white_img = Image.new("RGBA", img.size, (255, 255, 255, 255))
        white_img.putalpha(a)
        return ctk.CTkImage(light_image=white_img, dark_image=white_img, size=size)
    except:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
#  CashboxPage
# ═══════════════════════════════════════════════════════════════════════════════
class CashboxPage(ctk.CTkFrame):
    def __init__(self, parent, colors):
        super().__init__(parent, fg_color=colors["bg"], corner_radius=0)
        self.C = colors
        self._from_date = self._to_date = None
        self._current_tab = "sales"

        self._cal_icon   = get_icon("calendar", (18, 18))
        self._w_cal_icon = get_white_icon("calendar", (18, 18))
        self._cash_icon  = get_icon("cashbox", (28, 28))
        self._exp_icon   = get_icon("expenses", (20, 20))
        self._del_icon   = get_icon("delete", (16, 16))
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────
    def _build(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 10))

        ctk.CTkLabel(
            hdr, text="  الصندوق العام", font=(FONT_HDR, 24, "bold"),
            image=self._cash_icon, compound="right",
            text_color=self.C["accent"]
        ).pack(side="right")

        # ── NEW: سحب / إيداع button ──
        ctk.CTkButton(
            hdr, text="  سحب / إيداع", font=(FONT, 14, "bold"),
            image=self._exp_icon, compound="right",
            fg_color=self.C["warning"], text_color="#1F2937",
            hover_color="#D97706", corner_radius=10, height=44,
            command=self._open_transfer
        ).pack(side="left")

        # Date label
        day = ctk.CTkFrame(self, fg_color="transparent")
        day.pack(fill="x", padx=24, pady=(0, 8))
        ctk.CTkLabel(
            day, text=date.today().strftime("%d / %m / %Y"),
            font=(FONT, 14, "bold"), text_color=self.C["text2"]
        ).pack(side="right")

        # Filter bar
        flt = ctk.CTkFrame(self, fg_color=self.C["card"], corner_radius=12,
                           border_width=1, border_color=self.C["border"])
        flt.pack(fill="x", padx=24, pady=(0, 10))
        inner = ctk.CTkFrame(flt, fg_color="transparent")
        inner.pack(pady=10)

        ctk.CTkLabel(inner, text=":تصفية حسب التاريخ", font=(FONT, 13, "bold"),
                     text_color=self.C["accent"]).pack(side="right", padx=(0, 10))

        ctk.CTkButton(inner, text="", width=28, height=36, fg_color="transparent",
                      image=self._cal_icon, hover_color=self.C["hover"], corner_radius=8,
                      command=lambda: self._pick_date_main(self._from_e)
                      ).pack(side="right", padx=0)
        self._from_e = ctk.CTkEntry(inner, width=135, height=36, font=(FONT, 13),
                                    fg_color=self.C["input"], border_color=self.C["border"],
                                    text_color=self.C["text"], justify="center",
                                    placeholder_text="...من تاريخ", corner_radius=12)
        self._from_e.pack(side="right", padx=0)

        ctk.CTkButton(inner, text="", width=28, height=36, fg_color="transparent",
                      image=self._cal_icon, hover_color=self.C["hover"], corner_radius=8,
                      command=lambda: self._pick_date_main(self._to_e)
                      ).pack(side="right", padx=(0, 30))
        self._to_e = ctk.CTkEntry(inner, width=135, height=36, font=(FONT, 13),
                                  fg_color=self.C["input"], border_color=self.C["border"],
                                  text_color=self.C["text"], justify="center",
                                  placeholder_text="...إلى تاريخ", corner_radius=12)
        self._to_e.pack(side="right", padx=0)

        ctk.CTkButton(inner, text="تصفية", width=70, height=36, font=(FONT, 13, "bold"),
                      fg_color=self.C["accent"], text_color=self.C["btn_text"],
                      hover_color="#00897B", corner_radius=8,
                      command=self._apply).pack(side="right", padx=(0, 40))
        ctk.CTkButton(inner, text="الكل", width=70, height=36, font=(FONT, 13),
                      fg_color=self.C["hover"], text_color=self.C["text"],
                      border_width=1, border_color=self.C["border"], corner_radius=8,
                      command=self._clear).pack(side="right", padx=(0, 5))

        ctk.CTkButton(flt, text="صندوق اليوم", width=125, height=36, font=(FONT, 13, "bold"),
                      image=self._w_cal_icon, compound="right",
                      fg_color=self.C["blue"], text_color=self.C["btn_text"],
                      hover_color="#1E40AF", corner_radius=8,
                      command=self._today).place(relx=0.03, rely=0.5, anchor="w")

        # KPI cards
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=24, pady=(10, 20))
        self._frm_sales, self._lbl_sales = self._big_card(cards, "المبيعات",        "💰", self.C["success"])
        self._frm_exp,   self._lbl_exp   = self._big_card(cards, "المصروفات",       "💸", self.C["danger"])
        self._frm_debts, self._lbl_debts = self._big_card(cards, "مدفوعات الديون", "💳", self.C.get("info", self.C["blue"]))
        self._frm_trans, self._lbl_trans = self._big_card(cards, "سحب / إيداع",     "🔄", self.C["warning"])
        self._frm_net,   self._lbl_net   = self._big_card(cards, "الرصيد المتبقي",   "💵", self.C["accent"])

        # Tabs
        tab_bar = ctk.CTkFrame(self, fg_color=self.C["card"], corner_radius=12)
        tab_bar.pack(fill="x", padx=24, pady=(0, 10))
        self._tabs = {}
        t_inner = ctk.CTkFrame(tab_bar, fg_color="transparent")
        t_inner.pack(padx=8, pady=8)
        for k, label in [
            ("sales",    "💰  المبيعات"),
            ("exp",      "💸  المصروفات"),
            ("debts",    "💳  مدفوعات الديون"),
            ("transfer", "🔄  سحب / إيداع"),
        ]:
            b = ctk.CTkButton(
                t_inner, text=label, font=(FONT, 14, "bold"),
                fg_color="transparent", text_color=self.C["text2"],
                hover_color=self.C["hover"], corner_radius=8, height=40,
                command=lambda key=k: self._switch_tab(key)
            )
            b.pack(side="right", padx=6)
            self._tabs[k] = b

        self._scroll = ctk.CTkScrollableFrame(self, fg_color=self.C["bg"], corner_radius=0)
        self._scroll.pack(fill="both", expand=True, padx=24, pady=(0, 12))

    # ── Helpers ───────────────────────────────────────────────────────────
    def _big_card(self, parent, title, icon, color):
        c_map = {
            self.C["success"]: self.C["success_f"],
            self.C["danger"]:  self.C["danger_bg"],
            self.C["accent"]:  self.C["accent_f"],
            self.C["blue"]:    self.C["blue_f"],
        }
        bg   = c_map.get(color, self.C["card"])
        card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=22)
        card.pack(side="right", padx=8, expand=True, fill="both", ipady=12)
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=15, pady=(10, 2))
        ctk.CTkLabel(top, text=icon, font=(FONT, 22)).pack(side="right")
        ctk.CTkLabel(top, text=title, font=(FONT, 13, "bold"),
                     text_color=self.C["text"]).pack(side="right", padx=8)
        v_lbl = ctk.CTkLabel(card, text="—", font=(FONT, 26, "bold"),
                              text_color=color, anchor="e")
        v_lbl.pack(fill="x", padx=15, pady=2)
        ctk.CTkLabel(card, text="ملخص الحسابات الجاري", font=(FONT, 10),
                     text_color=self.C["text2"], anchor="e").pack(fill="x", padx=15, pady=(0, 8))
        return card, v_lbl

    def _switch_tab(self, key):
        self._current_tab = key
        for k, b in self._tabs.items():
            b.configure(
                fg_color=self.C["sidebar"]  if k == key else "transparent",
                text_color=self.C["accent"] if k == key else self.C["text2"],
            )
        self._draw_tab_content()

    def refresh(self):
        f, t = self._from_date, self._to_date
        s    = db.get_cashbox_summary(f, t)
        self._lbl_sales.configure( text=f"\u200E ₪ {s['sales']:,.2f}")
        self._lbl_exp.configure(   text=f"\u200E ₪ {s['expenses']:,.2f}")
        self._lbl_debts.configure( text=f"\u200E ₪ {s['debt_paid']:,.2f}")
        
        t = s["transfers"]
        t_color = self.C["danger"] if t > 0 else (self.C["success"] if t < 0 else self.C["text2"])
        self._lbl_trans.configure(text=f"\u200E ₪ {abs(t):,.2f}", text_color=t_color)

        n     = s["net"]
        color = self.C["success"] if n >= 0 else self.C["danger"]
        self._lbl_net.configure(text=f"\u200E ₪ {n:,.2f}", text_color=color)
        self._frm_net.configure(border_color=color)
        self._switch_tab(self._current_tab)

    def _fmt(self, d):
        if not d:
            return "—"
        try:
            from datetime import datetime
            return f"\u200E{datetime.strptime(d, '%Y-%m-%d').strftime('%d/%m/%Y')}"
        except:
            return f"\u200E{d}"

    def _draw_tab_content(self):
        for w in self._scroll.winfo_children():
            w.destroy()
        f, t = self._from_date, self._to_date

        header = ctk.CTkFrame(self._scroll, fg_color=self.C["sidebar"], corner_radius=8)
        header.pack(fill="x", pady=(0, 4))

        if self._current_tab == "sales":
            cols    = ["التاريخ", "الإجمالي", "بيان العملية / الملاحظات"]
            widths  = [120, 150, 400]
            data    = db.get_sales(from_date=f, to_date=t)
            vals_fn = lambda r: [
                self._fmt(r["sale_date"]),
                f"\u200E ₪ {r['total']:,.2f}",
                r["notes"] or "---",
            ]

        elif self._current_tab == "exp":
            cols    = ["التاريخ", "المبلغ", "الوصف"]
            widths  = [120, 150, 400]
            # Fetch only business expenses
            data    = db.get_expenses(from_date=f, to_date=t, include_transfers=False)
            vals_fn = lambda r: [
                self._fmt(r["expense_date"]),
                f"\u200E ₪ {r['amount']:,.2f}",
                r["description"] or "---",
            ]

        elif self._current_tab == "debts":
            cols   = ["التاريخ", "المدين", "المبلغ", "الملاحظات"]
            widths = [120, 150, 150, 300]
            from database import get_conn
            conn = get_conn()
            q = ("SELECT dp.pay_date, dp.amount, dp.notes, d.debtor_name "
                 "FROM debt_payments dp JOIN debts d ON dp.debt_id=d.id WHERE 1=1")
            p = []
            if f: q += " AND dp.pay_date>=?"; p.append(f)
            if t: q += " AND dp.pay_date<=?"; p.append(t)
            q += " ORDER BY dp.pay_date DESC LIMIT 100"
            data = conn.execute(q, p).fetchall()
            conn.close()
            vals_fn = lambda r: [
                self._fmt(r["pay_date"]), r["debtor_name"],
                f"\u200E ₪ {r['amount']:,.2f}", r["notes"] or "---",
            ]

        else:  # "transfer"
            cols    = ["التاريخ", "النوع", "المبلغ", "البيان / التصنيف", ""]
            widths  = [120, 100, 140, 320, 60]
            # Fetch EVERYTHING to filter for transfers specifically
            all_data = db.get_expenses(from_date=f, to_date=t, include_transfers=True)
            data     = [r for r in all_data if r["category"] == "INTERNAL_TRANSFER"]
            vals_fn = lambda r: [
                self._fmt(r["expense_date"]),
                "🔴 سحب" if r["amount"] > 0 else "🟢 إيداع",
                f"\u200E ₪ {abs(r['amount']):,.2f}",
                r["description"] or "---",
            ]

        # Draw column headers
        for i, col in enumerate(cols):
            w = widths[i] if i < len(widths) else 150
            # Pack empty headers (like delete column) to the left
            side = "left" if (col == "" and i == len(cols)-1) else "right"
            ctk.CTkLabel(header, text=col, font=(FONT, 14, "bold"),
                         text_color=self.C["accent"], width=w, anchor="e"
                         ).pack(side=side, padx=10, pady=10)

        if not data:
            ctk.CTkLabel(self._scroll, text="لا توجد بيانات في هذه الفترة",
                         font=(FONT, 16), text_color=self.C["text2"]).pack(pady=40)
            return

        for i, r in enumerate(list(data)[:100]):
            bg  = self.C["card"] if i % 2 == 0 else self.C["sidebar"]
            row = ctk.CTkFrame(self._scroll, fg_color=bg, corner_radius=6)
            row.pack(fill="x", pady=2)
            
            vals = vals_fn(r)
            for j, v in enumerate(vals):
                w = widths[j] if j < len(widths) else 150
                ctk.CTkLabel(row, text=v, font=(FONT, 12), text_color=self.C["text"],
                             width=w, anchor="e", justify="right"
                             ).pack(side="right", padx=10, pady=8)
            
            # Add delete button if it's the transfer tab
            if self._current_tab == "transfer":
                ctk.CTkButton(
                    row, text="", width=32, height=32, image=self._del_icon,
                    fg_color="transparent", hover_color=self.C.get("danger_bg", "#FEE2E2"),
                    corner_radius=8,
                    command=lambda rid=r["id"]: self._delete_transfer(rid)
                ).pack(side="left", padx=15, pady=4)

    # ── Actions ───────────────────────────────────────────────────────────
    def _open_transfer(self):
        _CashTransferDialog(self, self.C, on_save=self.refresh)
    
    def _delete_transfer(self, rid):
        from tkinter import messagebox
        if messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من حذف هذه العملية؟", parent=self):
            db.delete_expense(rid)
            self.refresh()

    def _pick_date_main(self, entry):
        show_date_picker(self, entry, self.C)

    def _today(self):
        t = date.today().isoformat()
        self._from_date = self._to_date = t
        self._from_e.delete(0, "end"); self._from_e.insert(0, t)
        self._to_e.delete(0, "end");   self._to_e.insert(0, t)
        self.refresh()

    def _apply(self):
        self._from_date = self._from_e.get().strip() or None
        self._to_date   = self._to_e.get().strip()   or None
        self.refresh()

    def _clear(self):
        self._from_e.delete(0, "end"); self._to_e.delete(0, "end")
        self._from_date = self._to_date = None
        self.refresh()


# ═══════════════════════════════════════════════════════════════════════════════
#  Cash Transfer Dialog
# ═══════════════════════════════════════════════════════════════════════════════
class _CashTransferDialog(ctk.CTkToplevel):
    """نافذة سحب أو إيداع من/إلى الصندوق العام"""

    CATEGORIES = [
        "شراء بضاعة / توريد",
        "مصروف تشغيلي",
        "تحويل بنكي",
        "سحب شخصي",
        "إيداع / إضافة رصيد",
        "أخرى",
    ]

    def __init__(self, parent, colors, on_save=None):
        super().__init__(parent)
        self.C        = colors
        self._on_save = on_save
        self._kind    = "withdraw"  # "withdraw" | "deposit"

        self.title("سحب / إيداع من الصندوق")
        self.geometry("520x680")
        self.resizable(False, False)
        self.configure(fg_color=self.C["bg"])
        self.grab_set()

        try:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            self.geometry(f"520x680+{(sw-520)//2}+{(sh-680)//2}")
        except:
            pass

        self._build()

    def _build(self):
        # ── Coloured header strip ──
        hdr = ctk.CTkFrame(self, fg_color=self.C["warning"], corner_radius=0, height=85)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(
            hdr, text="🔄  سحب / إيداع من الصندوق",
            font=(FONT_HDR, 22, "bold"), text_color="#1F2937"
        ).pack(expand=True, pady=10)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=30, pady=20)

        # ── Kind toggle ──
        ctk.CTkLabel(body, text="نوع العملية", font=(FONT, 13, "bold"),
                     text_color=self.C["text"], anchor="e").pack(fill="x", pady=(0, 6))

        toggle_row = ctk.CTkFrame(body, fg_color=self.C["sidebar"], corner_radius=12)
        toggle_row.pack(fill="x", pady=(0, 18))

        self._btn_withdraw = ctk.CTkButton(
            toggle_row, text="🔴  سحب من الصندوق",
            font=(FONT, 13, "bold"), corner_radius=10, height=42,
            fg_color=self.C["danger"], text_color="#FFFFFF",
            hover_color="#DC2626",
            command=lambda: self._set_kind("withdraw")
        )
        self._btn_withdraw.pack(side="right", expand=True, fill="x", padx=(6, 3), pady=6)

        self._btn_deposit = ctk.CTkButton(
            toggle_row, text="🟢  إيداع في الصندوق",
            font=(FONT, 13, "bold"), corner_radius=10, height=42,
            fg_color=self.C["hover"], text_color=self.C["text2"],
            hover_color=self.C["hover"],
            command=lambda: self._set_kind("deposit")
        )
        self._btn_deposit.pack(side="right", expand=True, fill="x", padx=(3, 6), pady=6)

        # ── Amount ──
        self._amount_e = self._field(body, "المبلغ (₪) *", "0.00")

        # ── Category ──
        ctk.CTkLabel(body, text="التصنيف / السبب *", font=(FONT, 13, "bold"),
                     text_color=self.C["text"], anchor="e").pack(fill="x", pady=(0, 4))
        self._cat_var = ctk.StringVar(value=self.CATEGORIES[0])
        ctk.CTkComboBox(
            body, values=self.CATEGORIES, variable=self._cat_var,
            font=(FONT, 13), dropdown_font=(FONT, 13),
            height=42, justify="right",
            fg_color=self.C["input"], border_color=self.C["border"],
            button_color=self.C["accent"], button_hover_color="#00897B",
            text_color=self.C["text"], corner_radius=10,
        ).pack(fill="x", pady=(0, 14))

        # ── Notes ──
        self._notes_e = self._field(body, "ملاحظات إضافية", "اختياري")

        # ── Date ──
        ctk.CTkLabel(body, text="التاريخ", font=(FONT, 13, "bold"),
                     text_color=self.C["text"], anchor="e").pack(fill="x", pady=(0, 4))
        
        date_input_row = ctk.CTkFrame(body, fg_color="transparent")
        date_input_row.pack(fill="x", pady=(0, 20))
        
        # Calendar button moved to the LEFT (side="left") as requested
        cal_btn = ctk.CTkButton(
            date_input_row, text="", width=42, height=42, image=get_icon("calendar", (20, 20)),
            fg_color=self.C["sidebar"], hover_color=self.C["hover"], corner_radius=10,
            command=lambda: show_date_picker(self, self._date_e, self.C)
        )
        cal_btn.pack(side="left", padx=(0, 5))

        self._date_e = ctk.CTkEntry(
            date_input_row, font=(FONT, 13), height=42, justify="center",
            fg_color=self.C["input"], border_color=self.C["border"],
            text_color=self.C["text"], corner_radius=10,
        )
        self._date_e.insert(0, date.today().isoformat())
        self._date_e.pack(side="right", fill="x", expand=True)

        # ── Action buttons ──
        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x")
        ctk.CTkButton(
            btn_row, text="✔  تأكيد وحفظ",
            font=(FONT, 15, "bold"), height=48, corner_radius=12,
            fg_color=self.C["accent"], text_color="#FFFFFF", hover_color="#00897B",
            command=self._save
        ).pack(side="right", fill="x", expand=True, padx=(4, 0))
        ctk.CTkButton(
            btn_row, text="إلغاء",
            font=(FONT, 14), height=48, corner_radius=12,
            fg_color="#F1F5F9", text_color="#64748B", hover_color="#E2E8F0",
            command=self.destroy
        ).pack(side="right", fill="x", expand=True, padx=(0, 4))

    def _field(self, parent, label, placeholder):
        ctk.CTkLabel(parent, text=label, font=(FONT, 13, "bold"),
                     text_color=self.C["text"], anchor="e").pack(fill="x", pady=(0, 4))
        e = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            font=(FONT, 14), height=42, justify="right",
            fg_color=self.C["input"], border_color=self.C["border"],
            text_color=self.C["text"], corner_radius=10,
        )
        e.pack(fill="x", pady=(0, 14))
        return e

    def _set_kind(self, kind):
        self._kind = kind
        if kind == "withdraw":
            self._btn_withdraw.configure(fg_color=self.C["danger"],  text_color="#FFFFFF")
            self._btn_deposit.configure( fg_color=self.C["hover"],   text_color=self.C["text2"])
        else:
            self._btn_deposit.configure( fg_color=self.C["success"], text_color="#FFFFFF")
            self._btn_withdraw.configure(fg_color=self.C["hover"],   text_color=self.C["text2"])

    def _save(self):
        from tkinter import messagebox
        amt_str = self._amount_e.get().strip()
        cat_str = self._cat_var.get().strip()
        notes   = self._notes_e.get().strip()
        d       = self._date_e.get().strip() or date.today().isoformat()

        if not amt_str:
            messagebox.showwarning("تنبيه", "الرجاء إدخال المبلغ", parent=self)
            return
        if not cat_str:
            messagebox.showwarning("تنبيه", "الرجاء اختيار التصنيف", parent=self)
            return
        try:
            amt = float(amt_str)
            if amt <= 0:
                raise ValueError
        except:
            messagebox.showerror("خطأ", "المبلغ غير صحيح – أدخل رقماً أكبر من الصفر", parent=self)
            return

        description = f"[{cat_str}] {notes}" if notes else cat_str
        # سحب = مبلغ موجب (يُخصم من الصندوق)
        # إيداع = مبلغ سالب (يُضاف للصندوق عبر تقليل المصروفات)
        final_amt = amt if self._kind == "withdraw" else -amt
        db.add_expense(description=description, amount=final_amt,
                       category="INTERNAL_TRANSFER", expense_date=d)

        if self._on_save:
            self._on_save()
        self.destroy()

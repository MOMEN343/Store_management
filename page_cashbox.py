"""
صفحة الصندوق – CustomTkinter
"""
import customtkinter as ctk
from datetime import date
import database as db

FONT_HDR = "Thmanyah Sans"
FONT_REG = "Cairo"
FONT = FONT_REG


class CashboxPage(ctk.CTkFrame):
    def __init__(self, parent, colors):
        super().__init__(parent, fg_color=colors["bg"], corner_radius=0)
        self.C = colors
        self._from_date = self._to_date = None
        self._current_tab = "sales"
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 10))
        ctk.CTkLabel(hdr, text="💰  الصندوق العام", font=(FONT_HDR, 24, "bold"),
                     text_color=self.C["accent"]).pack(side="right")
        
        day = ctk.CTkFrame(self, fg_color="transparent")
        day.pack(fill="x", padx=24, pady=(0, 8))
        ctk.CTkButton(day, text="📅 اليوم", font=(FONT, 14, "bold"), fg_color=self.C["blue"],
                      text_color=self.C["btn_text"], corner_radius=8, height=36,
                      command=self._today).pack(side="left")
        ctk.CTkLabel(day, text=date.today().strftime("%d / %m / %Y"),
                     font=(FONT, 14, "bold"), text_color=self.C["text2"]).pack(side="right")

        flt = ctk.CTkFrame(self, fg_color=self.C["card"], corner_radius=12)
        flt.pack(fill="x", padx=24, pady=(0, 10))
        inner = ctk.CTkFrame(flt, fg_color="transparent")
        inner.pack(padx=12, pady=10)
        ctk.CTkButton(inner, text="الكل", width=70, height=36, font=(FONT, 13),
                      fg_color=self.C["hover"], text_color=self.C["text"],
                      corner_radius=8, command=self._clear).pack(side="left", padx=4)
        ctk.CTkButton(inner, text="تصفية", width=70, height=36, font=(FONT, 13),
                      fg_color=self.C["blue"], text_color=self.C["btn_text"],
                      corner_radius=8, command=self._apply).pack(side="left", padx=4)
        self._to_e = ctk.CTkEntry(inner, width=130, height=36, font=(FONT, 13),
                                   fg_color=self.C["input"], border_color=self.C["border"],
                                   text_color=self.C["text"], justify="center", corner_radius=8)
        self._to_e.pack(side="left", padx=4)
        self._from_e = ctk.CTkEntry(inner, width=130, height=36, font=(FONT, 13),
                                     fg_color=self.C["input"], border_color=self.C["border"],
                                     text_color=self.C["text"], justify="center", corner_radius=8)
        self._from_e.pack(side="left", padx=4)
        ctk.CTkLabel(inner, text="📅  من — إلى", font=(FONT, 13), text_color=self.C["text2"]).pack(side="left")

        # Big cards
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=24, pady=(10, 20))
        
        self._frm_sales, self._lbl_sales = self._big_card(cards, "المبيعات", "💰", self.C["success"])
        self._frm_exp, self._lbl_exp   = self._big_card(cards, "المصروفات", "💸", self.C["danger"])
        self._frm_debts, self._lbl_debts = self._big_card(cards, "مدفوعات الديون", "💳", self.C["info"] if "info" in self.C else self.C["blue"])
        self._frm_net, self._lbl_net   = self._big_card(cards, "صافي الصندوق", "💵", self.C["accent"])

        # Tabs
        tab_bar = ctk.CTkFrame(self, fg_color=self.C["card"], corner_radius=12)
        tab_bar.pack(fill="x", padx=24, pady=(0, 10))
        
        self._tabs = {}
        t_inner = ctk.CTkFrame(tab_bar, fg_color="transparent")
        t_inner.pack(padx=8, pady=8)
        
        for k, l in [("sales", "💰  المبيعات"), ("exp", "💸  المصروفات"), ("debts", "💳  مدفوعات الديون")]:
            b = ctk.CTkButton(t_inner, text=l, font=(FONT, 14, "bold"),
                              fg_color="transparent", text_color=self.C["text2"],
                              hover_color=self.C["hover"], corner_radius=8, height=40,
                              command=lambda key=k: self._switch_tab(key))
            b.pack(side="right", padx=6)
            self._tabs[k] = b

        self._scroll = ctk.CTkScrollableFrame(self, fg_color=self.C["bg"], corner_radius=0)
        self._scroll.pack(fill="both", expand=True, padx=24, pady=(0, 12))

    def _big_card(self, parent, title, icon, color):
        c_map = {
            self.C["success"]: self.C["success_f"],
            self.C["danger"]:  self.C["danger_bg"],
            self.C["accent"]:  self.C["accent_f"],
            self.C["blue"]:    self.C["blue_f"]
        }
        bg = c_map.get(color, self.C["card"])
        
        card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=22, border_width=0)
        card.pack(side="right", padx=8, expand=True, fill="both", ipady=12)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=15, pady=(10, 2))
        ctk.CTkLabel(top, text=icon, font=(FONT, 22)).pack(side="right")
        ctk.CTkLabel(top, text=title, font=(FONT, 13, "bold"), text_color=self.C["text"]).pack(side="right", padx=8)

        v_lbl = ctk.CTkLabel(card, text="—", font=(FONT, 26, "bold"), text_color=color, anchor="e")
        v_lbl.pack(fill="x", padx=15, pady=2)

        ctk.CTkLabel(card, text="ملخص الحسابات الجاري", font=(FONT, 10), text_color=self.C["text2"], anchor="e").pack(fill="x", padx=15, pady=(0, 8))
        return card, v_lbl

    def _switch_tab(self, key):
        self._current_tab = key
        for k, b in self._tabs.items():
            b.configure(fg_color=self.C["sidebar"] if k == key else "transparent",
                        text_color=self.C["accent"] if k == key else self.C["text2"])
        self._draw_tab_content()

    def refresh(self):
        f, t = self._from_date, self._to_date
        s = db.get_cashbox_summary(f, t)
        self._lbl_sales.configure(text=f"\u200E ₪ {s['sales']:,.2f}")
        self._lbl_exp.configure(text=f"\u200E ₪ {s['expenses']:,.2f}")
        self._lbl_debts.configure(text=f"\u200E ₪ {s['debt_paid']:,.2f}")
        n = s["net"]
        color = self.C["success"] if n >= 0 else self.C["danger"]
        self._lbl_net.configure(text=f"\u200E ₪ {n:,.2f}", text_color=color)
        self._frm_net.configure(border_color=color)
        
        self._switch_tab(self._current_tab)

    def _fmt(self, d):
        if not d: return "—"
        try:
            from datetime import datetime
            return f"\u200E{datetime.strptime(d, '%Y-%m-%d').strftime('%d/%m/%Y')}"
        except: return f"\u200E{d}"

    def _draw_tab_content(self):
        for w in self._scroll.winfo_children(): w.destroy()
        f, t = self._from_date, self._to_date
        
        header = ctk.CTkFrame(self._scroll, fg_color=self.C["sidebar"], corner_radius=8)
        header.pack(fill="x", pady=(0, 4))
        
        if self._current_tab == "sales":
            cols = ["التاريخ", "الإجمالي", "بيان العملية / الملاحظات"]
            data = db.get_sales(from_date=f, to_date=t)
            vals_fn = lambda r: [
                self._fmt(r["sale_date"]),
                f"\u200E ₪ {r['total']:,.2f}", 
                r["notes"] if r["notes"] else "---"
            ]
        
        elif self._current_tab == "exp":
            cols = ["التاريخ", "المبلغ", "الوصف"]
            data = db.get_expenses(from_date=f, to_date=t)
            vals_fn = lambda r: [self._fmt(r["expense_date"]), f"\u200E ₪ {r['amount']:,.2f}", r["description"] if r["description"] else "---"]
            
        else: # debts
            cols = ["التاريخ", "المدين", "المبلغ", "الملاحظات"]
            from database import get_conn
            c = get_conn()
            q = "SELECT dp.pay_date, dp.amount, dp.notes, d.debtor_name FROM debt_payments dp JOIN debts d ON dp.debt_id=d.id WHERE 1=1"
            p = []
            if f: q+=" AND dp.pay_date>=?"; p.append(f)
            if t: q+=" AND dp.pay_date<=?"; p.append(t)
            q+=" ORDER BY dp.pay_date DESC LIMIT 100"
            data = c.execute(q, p).fetchall()
            c.close()
            vals_fn = lambda r: [self._fmt(r["pay_date"]), r["debtor_name"], f"\u200E ₪ {r['amount']:,.2f}", r["notes"] if r["notes"] else "---"]

        # Define widths for columns
        widths = [120, 150, 400] if self._current_tab in ["sales", "exp"] else [120, 150, 150, 300]
        
        for i, col in enumerate(cols):
            w = widths[i] if i < len(widths) else 150
            lbl = ctk.CTkLabel(header, text=col, font=(FONT, 14, "bold"), text_color=self.C["accent"], width=w, anchor="e")
            lbl.pack(side="right", padx=10, pady=10)

        if not data:
            ctk.CTkLabel(self._scroll, text="لا توجد بيانات", font=(FONT, 16), text_color=self.C["text2"]).pack(pady=40)
            return

        for i, r in enumerate(data[:100]): # Limit 100
            bg = self.C["card"] if i % 2 == 0 else self.C["sidebar"]
            row = ctk.CTkFrame(self._scroll, fg_color=bg, corner_radius=6)
            row.pack(fill="x", pady=2)
            row_vals = vals_fn(r)
            for j, v in enumerate(row_vals):
                w = widths[j] if j < len(widths) else 150
                # Last column (Notes) gets anchor="e" and more space if needed
                anch = "e"
                lbl = ctk.CTkLabel(row, text=v, font=(FONT, 12), text_color=self.C["text"], width=w, anchor=anch, justify="right")
                lbl.pack(side="right", padx=10, pady=8)

    def _today(self):
        t = date.today().isoformat(); self._from_date = t; self._to_date = t; self.refresh()
    def _apply(self):
        self._from_date = self._from_e.get().strip() or None; self._to_date = self._to_e.get().strip() or None; self.refresh()
    def _clear(self):
        self._from_e.delete(0,"end"); self._to_e.delete(0,"end"); self._from_date = self._to_date = None; self.refresh()

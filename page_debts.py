"""
صفحة الديون والمطالبات – CustomTkinter (النسخة الجمالية المطورة)
"""
import customtkinter as ctk
from datetime import date, datetime
import os
import database as db

FONT_HDR = "Thmanyah Sans"
FONT_REG = "Cairo"
FONT = FONT_REG
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_DIR = os.path.join(BASE_DIR, "icons")

def get_icon(name, size=(24, 24)):
    try:
        from PIL import Image
        return ctk.CTkImage(
            light_image=Image.open(os.path.join(ICON_DIR, f"{name}_light.png")),
            dark_image=Image.open(os.path.join(ICON_DIR, f"{name}_dark.png")),
            size=size
        )
    except: return None

def get_white_icon(name, size=(24, 24)):
    try:
        from PIL import Image
        img = Image.open(os.path.join(ICON_DIR, f"{name}_dark.png")).convert("RGBA")
        _, _, _, a = img.split()
        white_img = Image.new("RGBA", img.size, (255, 255, 255, 255))
        white_img.putalpha(a)
        return ctk.CTkImage(light_image=white_img, dark_image=white_img, size=size)
    except: return None

class DebtsPage(ctk.CTkFrame):
    def __init__(self, parent, colors):
        super().__init__(parent, fg_color=colors["bg"], corner_radius=0)
        self.C = colors
        self._status = "الكل"
        self._plus_icon = get_icon("add", (20, 20))
        self._pay_icon  = get_icon("supply", (20, 20)) # Using supply icon for payment
        self._debt_icon = get_icon("debts", (28, 28))
        self._cal_icon  = get_white_icon("calendar", (18, 18))
        self._del_icon  = get_icon("delete", (16, 16))
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 10))
        ctk.CTkLabel(hdr, text="  الديون والمطالبات", font=(FONT_HDR, 24, "bold"), image=self._debt_icon, compound="right", text_color=self.C["accent"]).pack(side="right")
        
        btn_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        btn_frame.pack(side="left")
        ctk.CTkButton(btn_frame, text="تسجيل دين جديد", font=(FONT, 15, "bold"), image=self._plus_icon, compound="right", fg_color=self.C["accent"], text_color=self.C["btn_text"], hover_color="#00897B", corner_radius=10, height=44, command=self._open_add).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="تسجيل دفعة سداد", font=(FONT, 15, "bold"), image=self._pay_icon, compound="right", fg_color=self.C["blue"], text_color=self.C["btn_text"], hover_color="#1E40AF", corner_radius=10, height=44, command=self._open_pay).pack(side="left", padx=5)

        flt = ctk.CTkFrame(self, fg_color=self.C["card"], corner_radius=12, border_width=1, border_color=self.C["border"])
        flt.pack(fill="x", padx=24, pady=(0, 10))
        inner = ctk.CTkFrame(flt, fg_color="transparent")
        inner.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(inner, text=":تصفية حسب الحالة", font=(FONT, 13, "bold"), text_color=self.C["accent"]).pack(side="right", padx=10)
        self._status_var = ctk.StringVar(value="الكل")
        for s in ["الكل", "مفتوح", "جزئي", "مسدد"]:
            ctk.CTkRadioButton(inner, text=s, variable=self._status_var, value=s, font=(FONT, 13), text_color=self.C["text"], fg_color=self.C["accent"], hover_color=self.C["accent"], command=self.refresh).pack(side="right", padx=15)

        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=24, pady=(0, 10))
        self._kpi_count = self._make_kpi(kpi_frame, "عدد الديون", "0", get_icon("receipt", (26, 26)), self.C["accent"])
        self._kpi_total = self._make_kpi(kpi_frame, "إجمالي الديون", "₪ 0", get_icon("debts", (26, 26)), self.C["danger"])
        self._kpi_paid  = self._make_kpi(kpi_frame, "إجمالي المسدد", "₪ 0", get_icon("supply", (26, 26)), self.C["success"])
        self._kpi_rem   = self._make_kpi(kpi_frame, "المبلغ المتبقي", "₪ 0", get_icon("products", (26, 26)), self.C["warning"])

        self._scroll = ctk.CTkScrollableFrame(self, fg_color=self.C["bg"], corner_radius=0)
        self._scroll.pack(fill="both", expand=True, padx=24, pady=(0, 12))

    def _make_kpi(self, parent, title, value, icon_img, color):
        c_map = { self.C["accent"]: self.C["accent_f"], self.C["danger"]: self.C["danger_bg"], self.C["success"]: self.C["success_f"], self.C["warning"]: self.C["warning_f"] }
        bg = c_map.get(color, self.C["card"])
        card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=22)
        card.pack(side="right", padx=6, expand=True, fill="both", ipady=12)
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=15, pady=(10, 2))
        ctk.CTkLabel(top, text="", image=icon_img).pack(side="right")
        ctk.CTkLabel(top, text=title, font=(FONT, 13, "bold"), text_color=self.C["text"]).pack(side="right", padx=8)
        v_lbl = ctk.CTkLabel(card, text=value, font=(FONT, 22, "bold"), text_color=color, anchor="e")
        v_lbl.pack(fill="x", padx=15, pady=2)
        return v_lbl

    def _setup_grid(self, frame):
        frame.grid_columnconfigure(0, weight=0, minsize=80)  # Sel & Del
        frame.grid_columnconfigure(1, weight=1)              # Debtor Name
        frame.grid_columnconfigure(2, weight=0, minsize=110) # Amount
        frame.grid_columnconfigure(3, weight=0, minsize=110) # Paid
        frame.grid_columnconfigure(4, weight=0, minsize=110) # Remaining
        frame.grid_columnconfigure(5, weight=0, minsize=100) # Status
        frame.grid_columnconfigure(6, weight=0, minsize=120) # Date

    def refresh(self):
        s = self._status_var.get()
        self._all = db.get_debts(status=None if s == "الكل" else s)
        for w in self._scroll.winfo_children(): w.destroy()

        header = ctk.CTkFrame(self._scroll, fg_color=self.C["sidebar"], corner_radius=10)
        header.pack(fill="x", pady=(0, 5))
        self._setup_grid(header)
        cols = [("تاريخ الدين", 6), ("الحالة", 5), ("المتبقي", 4), ("المسدد", 3), ("المبلغ", 2), ("اسم المدين", 1), ("", 0)]
        for text, col in cols:
            ctk.CTkLabel(header, text=text, font=(FONT, 13, "bold"), text_color=self.C["accent"], anchor="e").grid(row=0, column=col, padx=(0, 15), pady=10, sticky="nsew")

        if not self._all:
            ctk.CTkLabel(self._scroll, text="لا توجد ديون مسجلة حالياً", font=(FONT, 16), text_color=self.C["text2"]).pack(pady=60)
            self._kpi_count.configure(text="0"); self._kpi_total.configure(text="₪ 0"); self._kpi_paid.configure(text="₪ 0"); self._kpi_rem.configure(text="₪ 0"); return

        tot = 0.0; pd = 0.0; self._sel_var = ctk.StringVar(value="")
        for i, r in enumerate(self._all):
            rem = r["amount"] - r["paid"]; tot += r["amount"]; pd += r["paid"]
            bg = self.C["card"] if i % 2 == 0 else self.C["sidebar"]
            row = ctk.CTkFrame(self._scroll, fg_color=bg, corner_radius=8)
            row.pack(fill="x", pady=2)
            self._setup_grid(row)
            
            # Date (Col 6)
            fmt_date = r["debt_date"]
            try: fmt_date = f"\u200E{datetime.strptime(r['debt_date'], '%Y-%m-%d').strftime('%d/%m/%Y')}"
            except: pass
            ctk.CTkLabel(row, text=fmt_date, font=(FONT, 13), text_color=self.C["text"], anchor="e").grid(row=0, column=6, padx=(0, 15), pady=12, sticky="nsew")

            # Status (Col 5)
            c_tag = self.C["danger"] if r["status"] == "مفتوح" else (self.C["warning"] if r["status"] == "جزئي" else self.C["success"])
            ctk.CTkLabel(row, text=r["status"], font=(FONT, 13, "bold"), text_color=c_tag, anchor="e").grid(row=0, column=5, padx=(0, 15), pady=12, sticky="nsew")

            # Rem, Paid, Amount (4, 3, 2)
            ctk.CTkLabel(row, text=f"\u200E ₪ {rem:,.2f}", font=(FONT, 13, "bold"), text_color=self.C["danger"] if rem>0 else self.C["text"], anchor="e").grid(row=0, column=4, padx=(0, 15), pady=12, sticky="nsew")
            ctk.CTkLabel(row, text=f"\u200E ₪ {r['paid']:,.2f}", font=(FONT, 13), text_color=self.C["success"], anchor="e").grid(row=0, column=3, padx=(0, 15), pady=12, sticky="nsew")
            ctk.CTkLabel(row, text=f"\u200E ₪ {r['amount']:,.2f}", font=(FONT, 13, "bold"), text_color=self.C["text"], anchor="e").grid(row=0, column=2, padx=(0, 15), pady=12, sticky="nsew")

            # Debtor Name (Col 1)
            ctk.CTkLabel(row, text=r["debtor_name"], font=(FONT, 14, "bold"), text_color=self.C["text"], anchor="e", justify="right").grid(row=0, column=1, padx=(0, 15), pady=12, sticky="nsew")

            # Actions (Col 0)
            act_f = ctk.CTkFrame(row, fg_color="transparent")
            act_f.grid(row=0, column=0, padx=10, sticky="w")
            ctk.CTkRadioButton(act_f, text="", variable=self._sel_var, value=str(r["id"]), width=20, fg_color=self.C["accent"]).pack(side="left")
            ctk.CTkButton(act_f, text="", width=28, height=28, fg_color="transparent", image=self._del_icon, hover_color=self.C["danger_bg"], corner_radius=6, command=lambda rid=r["id"]: self._del(rid)).pack(side="left", padx=5)

        self._kpi_count.configure(text=str(len(self._all)))
        self._kpi_total.configure(text=f"₪ {tot:,.2f}")
        self._kpi_paid.configure(text=f"₪ {pd:,.2f}")
        self._kpi_rem.configure(text=f"₪ {(tot-pd):,.2f}")

    def _open_add(self): _DebtDialog(self, self.C, on_save=self.refresh)
    def _open_pay(self):
        sel = self._sel_var.get()
        if not sel: return
        debt = next((r for r in self._all if r["id"] == int(sel)), None)
        if debt: _PayDialog(self, self.C, debt, on_save=self.refresh)
    def _del(self, did):
        from tkinter import messagebox
        if messagebox.askyesno("تأكيد الحذف", "هل تريد حذف هذا الدين نهائياً؟"): db.delete_debt(did); self.refresh()

class _DebtDialog(ctk.CTkToplevel):
    def __init__(self, parent, colors, on_save=None):
        super().__init__(parent)
        self.C = colors; self._on_save = on_save
        self.title("تسجيل دين جديد"); self.geometry("480x650")
        self.resizable(False, False); self.configure(fg_color=self.C["bg"]); self.grab_set()
        self.update_idletasks()
        try:
            sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
            px = (sw - 480) // 2; py = (sh - 650) // 2
            self.geometry(f"480x650+{px}+{py}")
        except: pass
        self._build()

    def _build(self):
        hdr_f = ctk.CTkFrame(self, fg_color=self.C["accent"], corner_radius=0, height=80)
        hdr_f.pack(fill="x"); hdr_f.pack_propagate(False)
        ctk.CTkLabel(hdr_f, text="تسجيل دين جديد", font=(FONT_HDR, 22, "bold"), text_color="#FFFFFF", image=get_icon("debts", (32, 32)), compound="right", anchor="center").pack(expand=True, fill="both")
        
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=40, pady=20)
        
        def add_field(label, ph="", has_cal=False):
            ctk.CTkLabel(body, text=label, font=(FONT, 14, "bold"), text_color=self.C["text"], anchor="e").pack(fill="x", pady=(5, 2))
            f = ctk.CTkFrame(body, fg_color="transparent")
            f.pack(fill="x", pady=(0, 12))
            e = ctk.CTkEntry(f, placeholder_text=ph, font=(FONT, 15), height=42, fg_color=self.C["input"], border_color=self.C["border"], text_color=self.C["text"], corner_radius=10, justify="right")
            e.pack(side="right", fill="x", expand=True)
            if has_cal:
                ctk.CTkButton(f, text="", width=35, height=42, fg_color="transparent", image=get_icon("calendar", (20, 20)), corner_radius=10, hover_color=self.C["sidebar"], command=lambda: _DebtDialog.show_calendar(self, e, self.C)).pack(side="right", padx=(5, 0))
            return e
            
        self._name   = add_field("اسم المدين *", "أدخل اسم الشخص المستحق عليه الدين")
        self._amount = add_field("مبلغ الدين (₪) *", "0.00")
        self._desc   = add_field("التفاصيل / ملاحظات", "مثلاً: بضاعة متبقية...")
        self._d_date = add_field("تاريخ الدين", "YYYY-MM-DD", has_cal=True)
        self._d_date.insert(0, date.today().isoformat())
        self._due    = add_field("موعد السداد المتوقع", "اختياري YYYY-MM-DD", has_cal=True)

        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x", pady=(20, 10))
        self._save_btn = ctk.CTkButton(btn_row, text="💾 حفظ الدين", font=(FONT, 16, "bold"), fg_color=self.C["accent"], text_color="#FFFFFF", hover_color="#00897B", corner_radius=12, height=46, command=self._save)
        self._save_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkButton(btn_row, text="إلغاء", font=(FONT, 15), fg_color="#F1F5F9", text_color="#475569", hover_color="#E2E8F0", corner_radius=12, height=46, command=self.destroy).pack(side="right", fill="x", expand=True, padx=(0, 5))

    def _save(self):
        from tkinter import messagebox
        name = self._name.get().strip(); amt_s = self._amount.get().strip()
        if not name or not amt_s: messagebox.showwarning("تنبيه", "يرجى ملء الحقول المطلوبة (*)"); return
        try: amt = float(amt_s)
        except: messagebox.showerror("خطأ", "المبلغ غير صحيح"); return
        if amt <= 0: messagebox.showwarning("تنبيه", "يجب أن يكون المبلغ أكبر من صفر"); return
        d = self._d_date.get().strip() or date.today().isoformat()
        db.add_debt(name, amt, self._desc.get().strip(), d, self._due.get().strip())
        if self._on_save: self._on_save()
        self.destroy()

    @staticmethod
    def show_calendar(parent, entry, C):
        import calendar
        top = ctk.CTkToplevel(parent); top.title("اختر التاريخ")
        top.geometry("380x420"); top.resizable(False, False); top.configure(fg_color=C["bg"]); top.attributes("-topmost", True); top.grab_set()
        sw = parent.winfo_screenwidth(); sh = parent.winfo_screenheight()
        top.geometry(f"+{(sw-380)//2}+{(sh-420)//2}")
        card = ctk.CTkFrame(top, fg_color=C["card"], corner_radius=20, border_width=1, border_color=C["border"])
        card.pack(fill="both", expand=True, padx=10, pady=10)
        today = date.today(); curr_yr = [today.year]; curr_mo = [today.month]; view_mode = ["days"]
        ar_months = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
        hdr = ctk.CTkFrame(card, fg_color="transparent", height=50); hdr.pack(fill="x", padx=10, pady=5); hdr.pack_propagate(False)
        def shift(m):
            if view_mode[0] == "days":
                curr_mo[0] += m
                if curr_mo[0] > 12: curr_mo[0] = 1; curr_yr[0] += 1
                if curr_mo[0] < 1: curr_mo[0] = 12; curr_yr[0] -= 1
            else: curr_yr[0] += m
            render()
        ctk.CTkButton(hdr, text="<", width=35, height=35, fg_color=C["hover"], text_color=C["text"], corner_radius=18, command=lambda: shift(1)).pack(side="left")
        mo_btn = ctk.CTkButton(hdr, text="", font=(FONT_REG, 17, "bold"), text_color=C["text"], fg_color="transparent", hover_color=C["hover"], height=40, command=lambda: toggle_view())
        mo_btn.pack(side="left", expand=True)
        ctk.CTkButton(hdr, text=">", width=35, height=35, fg_color=C["hover"], text_color=C["text"], corner_radius=18, command=lambda: shift(-1)).pack(side="right")
        main_fr = ctk.CTkFrame(card, fg_color="transparent"); main_fr.pack(fill="both", expand=True, padx=15, pady=5)
        for i in range(7): main_fr.grid_columnconfigure(i, weight=1)
        def pick(d): entry.delete(0, "end"); entry.insert(0, f"{curr_yr[0]}-{curr_mo[0]:02d}-{d:02d}"); top.destroy()
        def render():
            for w in main_fr.winfo_children(): w.destroy()
            if view_mode[0] == "days":
                mo_btn.configure(text=f"{ar_months[curr_mo[0]-1]} {curr_yr[0]}")
                for c, d in enumerate(["أحد","إثن","ثلا","أرب","خم","جم","سب"]): ctk.CTkLabel(main_fr, text=d, font=(FONT_REG, 11, "bold"), text_color=C["muted"]).grid(row=0, column=6-c, pady=(5, 10))
                cal = calendar.Calendar(firstweekday=6)
                for r, week in enumerate(cal.monthdayscalendar(curr_yr[0], curr_mo[0])):
                    for c, day in enumerate(week):
                        if day != 0:
                            is_today = (curr_yr[0] == today.year and curr_mo[0] == today.month and day == today.day)
                            f = ctk.CTkFrame(main_fr, width=46, height=46, corner_radius=23, fg_color=C["accent"] if is_today else "transparent")
                            f.grid(row=r+1, column=6-c, padx=2, pady=2); f.pack_propagate(False)
                            lbl = ctk.CTkLabel(f, text=str(day), font=(FONT_REG, 13, "bold"), text_color="#FFFFFF" if is_today else C["text"]); lbl.pack(expand=True, fill="both")
                            for obj in [f, lbl]: obj.bind("<Button-1>", lambda e, d=day: pick(d))
            else:
                mo_btn.configure(text=f"{curr_yr[0]}")
                for i in range(12):
                    r = i // 3; c = i % 3; is_curr = (curr_yr[0] == today.year and (i+1) == today.month)
                    ctk.CTkButton(main_fr, text=ar_months[i], width=100, height=55, font=(FONT_REG, 14, "bold"), fg_color=C["accent"] if is_curr else "transparent", text_color="#FFFFFF" if is_curr else C["text"], hover_color=C["hover"], corner_radius=15, command=lambda m=(i+1): pick_month(m)).grid(row=r, column=2-c, padx=5, pady=5)
        def toggle_view(): view_mode[0] = "months" if view_mode[0] == "days" else "days"; render()
        def pick_month(m): curr_mo[0] = m; view_mode[0] = "days"; render()
        render()

class _PayDialog(ctk.CTkToplevel):
    def __init__(self, parent, colors, debt, on_save=None):
        super().__init__(parent)
        self.C = colors; self._debt = debt; self._on_save = on_save
        self.title("تسجيل دفعة سداد"); self.geometry("520x680")
        self.resizable(False, False); self.configure(fg_color=self.C["bg"]); self.grab_set()
        self.update_idletasks()
        try:
            sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
            px = (sw - 520) // 2; py = (sh - 680) // 2
            self.geometry(f"520x680+{px}+{py}")
        except: pass
        self._build()

    def _build(self):
        hdr_f = ctk.CTkFrame(self, fg_color=self.C["blue"], corner_radius=0, height=80)
        hdr_f.pack(fill="x"); hdr_f.pack_propagate(False)
        ctk.CTkLabel(hdr_f, text="تسجيل دفعة سداد", font=(FONT_HDR, 22, "bold"), text_color="#FFFFFF", image=get_icon("supply", (32, 32)), compound="right", anchor="center").pack(expand=True, fill="both")
        
        body = ctk.CTkFrame(self, fg_color="transparent"); body.pack(fill="both", expand=True, padx=40, pady=20)
        rem = self._debt["amount"] - self._debt["paid"]
        
        info = ctk.CTkFrame(body, fg_color=self.C["card"], corner_radius=15, border_width=1, border_color=self.C["border"])
        info.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(info, text=f"المدين: {self._debt['debtor_name']}", font=(FONT_HDR, 18, "bold"), text_color=self.C["accent"]).pack(pady=(10, 2))
        inf_r = ctk.CTkFrame(info, fg_color="transparent"); inf_r.pack(fill="x", pady=(2, 12), padx=15)
        
        # Total
        f1 = ctk.CTkFrame(inf_r, fg_color=self.C["blue_f"], corner_radius=8)
        f1.pack(side="right", padx=5)
        ctk.CTkLabel(f1, text=f"إجمالي: ₪ {self._debt['amount']:,.2f}", font=(FONT, 13, "bold"), text_color=self.C["blue"]).pack(padx=10, pady=4)
        
        # Paid
        f2 = ctk.CTkFrame(inf_r, fg_color=self.C["success_f"], corner_radius=8)
        f2.pack(side="right", padx=5)
        ctk.CTkLabel(f2, text=f"مسدد: ₪ {self._debt['paid']:,.2f}", font=(FONT, 13, "bold"), text_color=self.C["success"]).pack(padx=10, pady=4)
        
        # Remaining
        f3 = ctk.CTkFrame(inf_r, fg_color=self.C["danger_bg"] if rem > 0 else self.C["success_f"], corner_radius=8)
        f3.pack(side="right", padx=5)
        ctk.CTkLabel(f3, text=f"المتبقي: ₪ {rem:,.2f}", font=(FONT, 13, "bold"), text_color=self.C["danger"] if rem > 0 else self.C["success"]).pack(padx=10, pady=4)

        ctk.CTkLabel(body, text=":مبلغ الدفعة الجديدة *", font=(FONT, 14, "bold"), text_color=self.C["text"], anchor="e").pack(fill="x")
        self._pay_amt = ctk.CTkEntry(body, placeholder_text="0.00", font=(FONT, 16, "bold"), height=45, fg_color=self.C["input"], border_color=self.C["border"], text_color=self.C["accent"], corner_radius=10, justify="center")
        self._pay_amt.pack(fill="x", pady=(2, 12))
        self._pay_amt.insert(0, str(rem))

        ctk.CTkLabel(body, text=":تاريخ الدفع", font=(FONT, 14, "bold"), text_color=self.C["text"], anchor="e").pack(fill="x")
        f_dat = ctk.CTkFrame(body, fg_color="transparent"); f_dat.pack(fill="x", pady=(2, 12))
        self._pay_dat = ctk.CTkEntry(f_dat, font=(FONT, 15), height=45, fg_color=self.C["input"], border_color=self.C["border"], text_color=self.C["text"], corner_radius=10, justify="right")
        self._pay_dat.pack(side="right", fill="x", expand=True)
        self._pay_dat.insert(0, date.today().isoformat())
        ctk.CTkButton(f_dat, text="", width=35, height=45, fg_color="transparent", image=get_icon("calendar", (20, 20)), corner_radius=10, hover_color=self.C["sidebar"], command=lambda: _DebtDialog.show_calendar(self, self._pay_dat, self.C)).pack(side="right", padx=(5, 0))

        ctk.CTkLabel(body, text=":ملاحظات", font=(FONT, 14, "bold"), text_color=self.C["text"], anchor="e").pack(fill="x")
        self._pay_not = ctk.CTkEntry(body, placeholder_text="مثلاً: سداد نقدي، شيك...", font=(FONT, 14), height=45, fg_color=self.C["input"], border_color=self.C["border"], text_color=self.C["text"], corner_radius=10, justify="right")
        self._pay_not.pack(fill="x", pady=(2, 20))

        btn_row = ctk.CTkFrame(body, fg_color="transparent"); btn_row.pack(fill="x")
        self._save_btn = ctk.CTkButton(btn_row, text="💳 تسجيل الدفعة", font=(FONT, 16, "bold"), fg_color=self.C["blue"], text_color="#FFFFFF", hover_color="#1E40AF", corner_radius=12, height=48, command=self._save)
        self._save_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkButton(btn_row, text="إلغاء", font=(FONT, 15), fg_color="#F1F5F9", text_color="#475569", hover_color="#E2E8F0", corner_radius=12, height=48, command=self.destroy).pack(side="right", fill="x", expand=True, padx=(0, 5))

    def _save(self):
        from tkinter import messagebox
        try: amt = float(self._pay_amt.get() or 0)
        except: messagebox.showerror("خطأ", "المبلغ غير صحيح"); return
        if amt <= 0: messagebox.showwarning("تنبيه", "يجب أن يكون المبلغ أكبر من صفر"); return
        rem = self._debt["amount"] - self._debt["paid"]
        if amt > rem + 0.01: messagebox.showwarning("تنبيه", "المبلغ المدفوع أكبر من المتبقي!"); return
        d = self._pay_dat.get().strip() or date.today().isoformat()
        db.pay_debt(self._debt["id"], amt, d, self._pay_not.get().strip())
        if self._on_save: self._on_save()
        self.destroy()

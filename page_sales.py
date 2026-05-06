"""
صفحة المبيعات – CustomTkinter (نسخة الترابط الجمالي - مطابقة التوريد 100%)
"""
import customtkinter as ctk
from datetime import date
import os
import database as db
from date_picker import show_date_picker


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

class SalesPage(ctk.CTkFrame):
    def __init__(self, parent, colors):
        super().__init__(parent, fg_color=colors["bg"], corner_radius=0)
        self.C = colors
        self._from_date = self._to_date = None
        self._plus_icon  = get_icon("add", (20, 20))
        self._cal_icon   = get_icon("calendar", (18, 18))
        self._w_cal_icon = get_white_icon("calendar", (18, 18))
        self._sales_icon = get_icon("sales", (28, 28))
        self._del_icon   = get_icon("delete", (16, 16))

        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 10))
        ctk.CTkLabel(hdr, text="  سجل المبيعات", font=(FONT_HDR, 24, "bold"), image=self._sales_icon, compound="right", text_color=self.C["accent"]).pack(side="right")
        ctk.CTkButton(hdr, text="تسجيل بيع جديد", font=(FONT, 15, "bold"), image=self._plus_icon, compound="right", fg_color=self.C["accent"], text_color=self.C["btn_text"], hover_color="#00897B", corner_radius=10, height=44, command=self._open_add).pack(side="left")
        
        flt = ctk.CTkFrame(self, fg_color=self.C["card"], corner_radius=12, border_width=1, border_color=self.C["border"])
        flt.pack(fill="x", padx=24, pady=(0, 10))
        
        # Center all filter elements as one group
        inner = ctk.CTkFrame(flt, fg_color="transparent")
        inner.pack(pady=10)
        
        # Group everything in order from right to left
        # Pack elements sequentially from Right to Left to ensure perfect order
        # 1. Label (Far Right)
        ctk.CTkLabel(inner, text=":تاريخ المبيعات", font=(FONT, 13, "bold"), text_color=self.C["accent"]).pack(side="right", padx=(0, 10))
        
        # 2. From Group (Icon docked to Entry)
        ctk.CTkButton(inner, text="", width=28, height=36, fg_color="transparent", image=self._cal_icon, hover_color=self.C["hover"], corner_radius=8, command=lambda: self._pick_date_main(self._from_e)).pack(side="right", padx=0)
        self._from_e = ctk.CTkEntry(inner, width=135, height=36, font=(FONT, 13), fg_color=self.C["input"], border_color=self.C["border"], text_color=self.C["text"], justify="center", placeholder_text="...من تاريخ", corner_radius=12)

        self._from_e.pack(side="right", padx=0)
        
        # 3. To Group (30px gap from 'From' group, then Icon docked to Entry)
        ctk.CTkButton(inner, text="", width=28, height=36, fg_color="transparent", image=self._cal_icon, hover_color=self.C["hover"], corner_radius=8, command=lambda: self._pick_date_main(self._to_e)).pack(side="right", padx=(0, 30))
        self._to_e = ctk.CTkEntry(inner, width=135, height=36, font=(FONT, 13), fg_color=self.C["input"], border_color=self.C["border"], text_color=self.C["text"], justify="center", placeholder_text="...إلى تاريخ", corner_radius=12)

        self._to_e.pack(side="right", padx=0)
        
        # 4. Action Buttons (40px gap from the date entries)
        ctk.CTkButton(inner, text="تصفية", width=70, height=36, font=(FONT, 13, "bold"), fg_color=self.C["accent"], text_color=self.C["btn_text"], hover_color="#00897B", corner_radius=8, command=self._apply_filter).pack(side="right", padx=(0, 40))
        ctk.CTkButton(inner, text="الكل", width=70, height=36, font=(FONT, 13), fg_color=self.C["hover"], text_color=self.C["text"], border_width=1, border_color=self.C["border"], corner_radius=8, command=self._clear_filter).pack(side="right", padx=(0, 5))

        
        # 5. Today Button (Using PLACE to anchor it at the Far Left of the 'flt' frame)
        ctk.CTkButton(flt, text="مبيعات اليوم", width=115, height=36, font=(FONT, 13, "bold"), image=self._w_cal_icon, compound="right", fg_color=self.C["blue"], text_color=self.C["btn_text"], hover_color="#1E40AF", corner_radius=8, command=self._today).place(relx=0.03, rely=0.5, anchor="w")





        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=24, pady=(0, 10))
        self._kpi_count = self._make_kpi(kpi_frame, "عدد العمليات", "0", get_icon("receipt", (28, 28)), self.C["accent"])
        self._kpi_rev   = self._make_kpi(kpi_frame, "إجمالي مبيعات الفترة", "₪ 0", get_icon("sales", (28, 28)), self.C["success"])
        
        # Scrollable area starts directly after KPIs
        self._scroll = ctk.CTkScrollableFrame(self, fg_color=self.C["bg"], corner_radius=0)
        self._scroll.pack(fill="both", expand=True, padx=24, pady=(0, 12))

    def _setup_grid(self, frame):
        # Column configuration matches for both header and rows inside the scroll
        frame.grid_columnconfigure(3, weight=0, minsize=140) # Date
        frame.grid_columnconfigure(2, weight=0, minsize=140) # Amount
        frame.grid_columnconfigure(1, weight=1)              # Notes
        frame.grid_columnconfigure(0, weight=0, minsize=60)  # Delete

    def _make_kpi(self, parent, title, value, icon_img, color):
        c_map = { self.C["accent"]: self.C["accent_f"], self.C["success"]: self.C["success_f"], self.C["blue"]: self.C["blue_f"] }
        bg = c_map.get(color, self.C["card"])
        card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=22)
        card.pack(side="right", padx=10, expand=True, fill="both", ipady=12)
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=15, pady=(10, 2))
        ctk.CTkLabel(top, text="", image=icon_img).pack(side="right")
        ctk.CTkLabel(top, text=title, font=(FONT, 13, "bold"), text_color=self.C["text"]).pack(side="right", padx=8)
        v_lbl = ctk.CTkLabel(card, text=value, font=(FONT, 26, "bold"), text_color=color, anchor="e")
        v_lbl.pack(fill="x", padx=15, pady=2)
        return v_lbl

    def refresh(self):
        rows = db.get_sales(from_date=self._from_date, to_date=self._to_date)
        for w in self._scroll.winfo_children(): w.destroy()
        
        # Create Header INSIDE the scroll frame to match Supply Page feel
        header = ctk.CTkFrame(self._scroll, fg_color=self.C["sidebar"], corner_radius=10)
        header.pack(fill="x", pady=(0, 5))
        self._setup_grid(header)
        
        # Consistent column headers with proper alignment
        cols = [
            ("تاريخ البيع", 3, "center"), 
            ("المبلغ الإجمالي", 2, "center"), 
            ("الملاحظات / بيان العملية", 1, "e"), 
            ("", 0, "center")
        ]
        for text, col, anchor in cols:
            ctk.CTkLabel(header, text=text, font=(FONT, 13, "bold"), text_color=self.C["accent"], 
                         anchor=anchor).grid(row=0, column=col, padx=15, pady=10, sticky="nsew")


        if not rows:
            ctk.CTkLabel(self._scroll, text="لا توجد مبيعات مسجلة في هذه الفترة", font=(FONT, 16), text_color=self.C["text2"]).pack(pady=60)
            self._kpi_count.configure(text="0"); self._kpi_rev.configure(text="₪ 0"); return

        total_cash = 0.0
        for i, r in enumerate(rows):
            total_cash += r["total"]
            bg = self.C["card"] if i % 2 == 0 else self.C["sidebar"]
            row = ctk.CTkFrame(self._scroll, fg_color=bg, corner_radius=8)
            row.pack(fill="x", pady=2)
            self._setup_grid(row)
            
            # Date (Col 3) - Centered
            fmt_date = r["sale_date"]
            try:
                from datetime import datetime
                fmt_date = f"\u200E{datetime.strptime(r['sale_date'], '%Y-%m-%d').strftime('%d/%m/%Y')}"
            except: pass
            ctk.CTkLabel(row, text=fmt_date, font=(FONT, 14), text_color=self.C["text"], anchor="center").grid(row=0, column=3, padx=15, pady=12, sticky="nsew")

            # Amount (Col 2) - Centered
            ctk.CTkLabel(row, text=f"\u200E ₪ {r['total']:,.2f}", font=(FONT, 14, "bold"), text_color=self.C["text"], anchor="center").grid(row=0, column=2, padx=15, pady=12, sticky="nsew")
            
            # Notes (Col 1) - Right Aligned
            lbl_notes = ctk.CTkLabel(row, text=r["notes"] or "—", font=(FONT, 14), text_color=self.C["text"], anchor="e", justify="right", wraplength=480)
            lbl_notes.grid(row=0, column=1, padx=15, pady=12, sticky="nsew")
            
            # Delete (Col 0) - Centered (default for grid)
            ctk.CTkButton(row, text="", width=32, height=32, fg_color="transparent", image=self._del_icon, hover_color=self.C["danger_bg"], corner_radius=8, command=lambda rid=r["id"]: self._del(rid)).grid(row=0, column=0, padx=15, pady=12)



        self._kpi_count.configure(text=str(len(rows)))
        self._kpi_rev.configure(text=f"₪ {total_cash:,.2f}")

    def _today(self):
        t = date.today().isoformat()
        self._from_date = self._to_date = t
        self._from_e.delete(0, "end"); self._from_e.insert(0, t)
        self._to_e.delete(0, "end"); self._to_e.insert(0, t)
        self.refresh()

    def _apply_filter(self):
        self._from_date = self._from_e.get().strip() or None
        self._to_date = self._to_e.get().strip() or None; self.refresh()

    def _clear_filter(self):
        self._from_e.delete(0, "end"); self._to_e.delete(0, "end")
        self._from_date = self._to_date = None; self.refresh()

    def _pick_date_main(self, entry):
        show_date_picker(self, entry, self.C)


    def _open_add(self):
        _SaleDialog(self, self.C, on_save=self.refresh)

    def _del(self, sid):
        from tkinter import messagebox
        if messagebox.askyesno("تأكيد الحذف", "هل تريد حذف هذه العملية من السجل؟"):
            db.delete_sale(sid); self.refresh()

class _SaleDialog(ctk.CTkToplevel):
    def __init__(self, parent, colors, on_save=None):
        super().__init__(parent)
        self.C = colors; self._on_save = on_save
        self.title("تسجيل مبيعات جديدة"); self.geometry("480x500")
        self.resizable(False, False); self.configure(fg_color=self.C["bg"]); self.grab_set()
        self.update_idletasks()
        try:
            sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
            px = (sw - 480) // 2; py = (sh - 500) // 2
            self.geometry(f"480x500+{px}+{py}")
        except: pass
        self._build()

    def _build(self):
        hdr_f = ctk.CTkFrame(self, fg_color=self.C["accent"], corner_radius=0, height=80)
        hdr_f.pack(fill="x")
        hdr_f.pack_propagate(False)
        ctk.CTkLabel(hdr_f, text="تسجيل مبيعات جديدة", font=(FONT_HDR, 22, "bold"), text_color=self.C["btn_text"], image=get_icon("sales", (32, 32)), compound="right", anchor="center").pack(expand=True, fill="both")
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=40, pady=25)
        def add_field(label, ph="", has_cal=False):
            lbl_fr = ctk.CTkFrame(body, fg_color="transparent")
            lbl_fr.pack(fill="x", pady=(5, 2))
            ctk.CTkLabel(lbl_fr, text=label, font=(FONT, 14, "bold"), text_color=self.C["text"], anchor="e").pack(side="right")
            f = ctk.CTkFrame(body, fg_color="transparent")
            f.pack(fill="x", pady=(0, 15))
            e = ctk.CTkEntry(f, placeholder_text=ph, font=(FONT, 15), height=45, fg_color=self.C["input"], border_color=self.C["border"], text_color=self.C["text"], corner_radius=10, justify="right")
            e.pack(side="right", fill="x", expand=True)
            if has_cal:
                btn = ctk.CTkButton(f, text="", width=35, height=45, fg_color="transparent", image=get_icon("calendar", (20, 20)), corner_radius=10, hover_color=self.C["sidebar"], command=lambda: show_date_picker(self, e, self.C))

                btn.pack(side="right", padx=(5, 0))
            return e
        self._amount = add_field("قيمة المبيعات الكلية (₪) *", "0.00")
        self._date_e = add_field("تاريخ العملية", "YYYY-MM-DD", has_cal=True)
        self._date_e.insert(0, date.today().isoformat())
        self._notes  = add_field("بيان المبيعات / ملاحظات", "مثلاً: مبيعات متنوعة...")
        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x", pady=(20, 0))
        self._save_btn = ctk.CTkButton(btn_row, text="💾 حفظ المبيعات", font=(FONT, 16, "bold"), fg_color=self.C["accent"], text_color=self.C["btn_text"], hover_color="#00897B", corner_radius=12, height=46, command=self._save)
        self._save_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkButton(btn_row, text="إلغاء", font=(FONT, 15), fg_color="#F1F5F9", text_color="#475569", hover_color="#E2E8F0", corner_radius=12, height=46, command=self.destroy).pack(side="right", fill="x", expand=True, padx=(0, 5))

    @staticmethod
    def show_calendar(parent, entry, C):
        import calendar
        top = ctk.CTkToplevel(parent); top.title("اختر التاريخ")
        top.geometry("380x420"); top.resizable(False, False)
        top.configure(fg_color=C["bg"]); top.attributes("-topmost", True); top.grab_set()
        sw = parent.winfo_screenwidth(); sh = parent.winfo_screenheight()
        top.geometry(f"+{(sw-380)//2}+{(sh-420)//2}")
        card = ctk.CTkFrame(top, fg_color=C["card"], corner_radius=20, border_width=1, border_color=C["border"])
        card.pack(fill="both", expand=True, padx=10, pady=10)
        today = date.today(); curr_yr = [today.year]; curr_mo = [today.month]; view_mode = ["days"]
        ar_months = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
        hdr = ctk.CTkFrame(card, fg_color="transparent", height=50)
        hdr.pack(fill="x", padx=10, pady=5)
        hdr.pack_propagate(False)
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
        main_fr = ctk.CTkFrame(card, fg_color="transparent")
        main_fr.pack(fill="both", expand=True, padx=15, pady=5)
        for i in range(7): main_fr.grid_columnconfigure(i, weight=1)
        def pick(d):
            entry.delete(0, "end"); entry.insert(0, f"{curr_yr[0]}-{curr_mo[0]:02d}-{d:02d}")
            top.destroy()
        def render():
            for w in main_fr.winfo_children(): w.destroy()
            if view_mode[0] == "days":
                mo_btn.configure(text=f"{ar_months[curr_mo[0]-1]} {curr_yr[0]}")
                days = ["أحد","إثن","ثلا","أرب","خم","جم","سب"]
                for c, d in enumerate(days):
                    ctk.CTkLabel(main_fr, text=d, font=(FONT_REG, 11, "bold"), text_color=C["muted"]).grid(row=0, column=6-c, pady=(5, 10))
                cal = calendar.Calendar(firstweekday=6)
                for r, week in enumerate(cal.monthdayscalendar(curr_yr[0], curr_mo[0])):
                    for c, day in enumerate(week):
                        if day != 0:
                            is_today = (curr_yr[0] == today.year and curr_mo[0] == today.month and day == today.day)
                            f = ctk.CTkFrame(main_fr, width=46, height=46, corner_radius=23, fg_color=C["accent"] if is_today else "transparent")
                            f.grid(row=r+1, column=6-c, padx=2, pady=2); f.pack_propagate(False)
                            lbl = ctk.CTkLabel(f, text=str(day), font=(FONT_REG, 13, "bold"), text_color="#FFFFFF" if is_today else C["text"])
                            lbl.pack(expand=True, fill="both")
                            def on_ent(e, frame=f, sel=is_today):
                                if not sel: frame.configure(fg_color=C["hover"])
                            def on_lev(e, frame=f, sel=is_today):
                                if not sel: frame.configure(fg_color="transparent")
                            for obj in [f, lbl]:
                                obj.bind("<Button-1>", lambda e, d=day: pick(d))
                                obj.bind("<Enter>", on_ent); obj.bind("<Leave>", on_lev)
            else:
                mo_btn.configure(text=f"{curr_yr[0]}")
                for i in range(12):
                    r = i // 3; c = i % 3
                    is_curr = (curr_yr[0] == today.year and (i+1) == today.month)
                    btn = ctk.CTkButton(main_fr, text=ar_months[i], width=100, height=55, font=(FONT_REG, 14, "bold"), fg_color=C["accent"] if is_curr else "transparent", text_color="#FFFFFF" if is_curr else C["text"], hover_color=C["hover"], corner_radius=15, command=lambda m=(i+1): pick_month(m))
                    btn.grid(row=r, column=2-c, padx=5, pady=5)
        def toggle_view(): view_mode[0] = "months" if view_mode[0] == "days" else "days"; render()
        def pick_month(m): curr_mo[0] = m; view_mode[0] = "days"; render()
        render()

    def _save(self):
        try:
            amt_str = self._amount.get().strip()
            if not amt_str:
                from tkinter import messagebox
                messagebox.showwarning("تنبيه", "يرجى إدخال مبلغ المبيعات")
                return
                
            try:
                amt = float(amt_str)
            except ValueError:
                from tkinter import messagebox
                messagebox.showerror("خطأ", "يرجى إدخال مبلغ صحيح (أرقام فقط)")
                return

            if amt <= 0:
                from tkinter import messagebox
                messagebox.showwarning("تنبيه", "يجب أن يكون المبلغ أكبر من صفر")
                return

            db.add_sale(
                product_id=None, 
                quantity=1, 
                unit_price=amt, 
                discount=0, 
                notes=self._notes.get().strip(), 
                sale_date=self._date_e.get().strip()
            )
            
            if self._on_save: 
                self._on_save()
            self.destroy()
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("خطأ", f"حدث خطأ أثناء حفظ المبيعات:\n{str(e)}")

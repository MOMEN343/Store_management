"""
صفحة التوريد – CustomTkinter
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
        # Use dark image (usually dark pixels on transparent bg) to extract alpha channel
        img = Image.open(os.path.join(ICON_DIR, f"{name}_dark.png")).convert("RGBA")
        _, _, _, a = img.split()
        white_img = Image.new("RGBA", img.size, (255, 255, 255, 255))
        white_img.putalpha(a)
        return ctk.CTkImage(light_image=white_img, dark_image=white_img, size=size)
    except: return None


class SupplyPage(ctk.CTkFrame):
    def __init__(self, parent, colors):
        super().__init__(parent, fg_color=colors["bg"], corner_radius=0)
        self.C = colors
        self._from_date = self._to_date = None
        
        # Icons
        self._supply_icon = get_icon("supply", (28, 28))
        self._plus_icon   = get_icon("add", (20, 20))
        self._cal_icon    = get_icon("calendar", (20, 20))
        self._del_icon    = get_icon("delete", (16, 16))
        
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 10))
        ctk.CTkLabel(hdr, text="  إدارة التوريد", font=(FONT_HDR, 24, "bold"),
                     image=self._supply_icon, compound="right",
                     text_color=self.C["accent"]).pack(side="right")
        ctk.CTkButton(hdr, text="توريد جديد", font=(FONT, 15, "bold"),
                      image=self._plus_icon, compound="right",
                      fg_color=self.C["accent"], text_color=self.C["btn_text"], hover_color="#0D9488",
                      corner_radius=10, height=44, command=self._open_add).pack(side="left")

        # Modern Filter Bar
        flt = ctk.CTkFrame(self, fg_color=self.C["card"], corner_radius=12, border_width=1, border_color=self.C["border"])
        flt.pack(fill="x", padx=24, pady=(0, 10))
        inner = ctk.CTkFrame(flt, fg_color="transparent")
        inner.pack(pady=10)

        # 1. Label (Far Right)
        ctk.CTkLabel(inner, text=":تاريخ التوريد", font=(FONT, 13, "bold"), text_color=self.C["accent"]).pack(side="right", padx=(0, 10))

        # 2. From Group (Icon docked to Entry)
        ctk.CTkButton(inner, text="", width=28, height=36, fg_color="transparent", image=self._cal_icon, hover_color=self.C["hover"], corner_radius=8, command=lambda: self._pick_date(self._from_e)).pack(side="right", padx=0)
        self._from_e = ctk.CTkEntry(inner, width=135, height=36, font=(FONT, 13), fg_color=self.C["input"], border_color=self.C["border"], text_color=self.C["text"], justify="center", placeholder_text="...من تاريخ", corner_radius=12)

        self._from_e.pack(side="right", padx=0)

        # 3. To Group (30px gap from 'From' group, then Icon docked to Entry)
        ctk.CTkButton(inner, text="", width=28, height=36, fg_color="transparent", image=self._cal_icon, hover_color=self.C["hover"], corner_radius=8, command=lambda: self._pick_date(self._to_e)).pack(side="right", padx=(0, 30))
        self._to_e = ctk.CTkEntry(inner, width=135, height=36, font=(FONT, 13), fg_color=self.C["input"], border_color=self.C["border"], text_color=self.C["text"], justify="center", placeholder_text="...إلى تاريخ", corner_radius=12)

        self._to_e.pack(side="right", padx=0)

        # 4. Action Buttons (40px gap from the date entries)
        ctk.CTkButton(inner, text="تصفية", width=70, height=36, font=(FONT, 13, "bold"), fg_color=self.C["accent"], text_color=self.C["btn_text"], hover_color="#00897B", corner_radius=8, command=self._apply_filter).pack(side="right", padx=(0, 40))
        ctk.CTkButton(inner, text="الكل", width=70, height=36, font=(FONT, 13), fg_color=self.C["hover"], text_color=self.C["text"], border_width=1, border_color=self.C["border"], corner_radius=8, command=self._clear_filter).pack(side="right", padx=(0, 5))


        # 5. Today Button (Using PLACE to anchor it at the Far Left of the 'flt' frame)
        ctk.CTkButton(flt, text="توريد اليوم", width=115, height=36, font=(FONT, 13, "bold"), image=get_white_icon("calendar", (18, 18)), compound="right", fg_color=self.C["blue"], text_color=self.C["btn_text"], hover_color="#1E40AF", corner_radius=8, command=self._today).place(relx=0.03, rely=0.5, anchor="w")






        # KPI row
        kpi = ctk.CTkFrame(self, fg_color="transparent")
        kpi.pack(fill="x", padx=24, pady=(0, 8))
        self._kpi_count = self._make_kpi(kpi, "عدد العمليات", "0", get_icon("receipt", (28, 28)), self.C["accent"])
        self._kpi_qty   = self._make_kpi(kpi, "إجمالي الكميات", "0", get_icon("supply", (28, 28)), self.C["blue"])
        self._kpi_cost  = self._make_kpi(kpi, "إجمالي التكلفة", "₪ 0", get_icon("expenses", (28, 28)), self.C["warning"])

        # Table
        self._scroll = ctk.CTkScrollableFrame(self, fg_color=self.C["bg"], corner_radius=0)
        self._scroll.pack(fill="both", expand=True, padx=24, pady=(0, 12))

    def _make_kpi(self, parent, title, value, icon_img, color):
        # Map main color to its faded background version from theme
        c_map = {
            self.C["accent"]:  self.C["accent_f"],
            self.C["blue"]:    self.C["blue_f"],
            self.C["success"]: self.C["success_f"],
            self.C["danger"]:  self.C["danger_bg"], # used danger_bg as it exists
            self.C["warning"]: self.C["warning_f"],
        }
        bg = c_map.get(color, self.C["card"])
        
        card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=22, border_width=0)
        card.pack(side="right", padx=8, expand=True, fill="both", ipady=12)

        # Top row: Icon + Title
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=15, pady=(10, 2))
        ctk.CTkLabel(top, text="", image=icon_img).pack(side="right")
        ctk.CTkLabel(top, text=title, font=(FONT, 13, "bold"), text_color=self.C["text"]).pack(side="right", padx=8)

        # Main Value
        v_lbl = ctk.CTkLabel(card, text=value, font=(FONT, 26, "bold"), text_color=color, anchor="e")
        v_lbl.pack(fill="x", padx=15, pady=2)

        # Footer
        ctk.CTkLabel(card, text="إحصائيات النظام المحدثة", font=(FONT, 10), text_color=self.C["text2"], anchor="e").pack(fill="x", padx=15, pady=(0, 8))
        return v_lbl

    def _fmt(self, d):
        if not d: return ""
        try:
            from datetime import datetime
            return f"\u200E{datetime.strptime(d, '%Y-%m-%d').strftime('%d/%m/%Y')}"
        except: return f"\u200E{d}"

    def _today(self):
        t = date.today().isoformat()
        self._from_date = self._to_date = t
        self._from_e.delete(0, "end"); self._from_e.insert(0, t)
        self._to_e.delete(0, "end"); self._to_e.insert(0, t)
        self.refresh()

    def refresh(self):
        rows = db.get_supplies(from_date=self._from_date, to_date=self._to_date)
        for w in self._scroll.winfo_children(): w.destroy()

        if not rows:
            ctk.CTkLabel(self._scroll, text="لا توجد عمليات توريد", font=(FONT, 17),
                         text_color=self.C["text2"]).pack(pady=50)
            self._kpi_count.configure(text="0"); self._kpi_qty.configure(text="0")
            self._kpi_cost.configure(text="₪ 0"); return

        # Header row
        header = ctk.CTkFrame(self._scroll, fg_color=self.C["sidebar"], corner_radius=8)
        header.pack(fill="x", pady=(0, 4))
        # الترتيب المنطقي: التاريخ -> الكود -> الصنف -> الكمية -> السعر -> التكلفة -> الربح -> ملاحظات
        cols = ["التاريخ", "الكود", "الصنف", "الكمية", "سعر الشراء", "إجمالي التكلفة", "الربح المتوقع", "ملاحظات"]
        for col in cols:
            ctk.CTkLabel(header, text=col, font=(FONT, 12, "bold"), text_color=self.C["accent"],
                         width=100).pack(side="right", padx=3, pady=8)

        tq = 0; tc = 0.0
        for i, r in enumerate(rows):
            tot_cost = r["quantity"] * r["cost_price"]
            tot_profit = r["quantity"] * ((r["sell_price"] or 0) - r["cost_price"])
            tq += r["quantity"]; tc += tot_cost
            bg = self.C["card"] if i % 2 == 0 else self.C["sidebar"]
            row = ctk.CTkFrame(self._scroll, fg_color=bg, corner_radius=6)
            row.pack(fill="x", pady=2)
            
            vals = [
                self._fmt(r["supply_date"]),
                r["product_code"],
                r["product_name"],
                f"\u200E{r['quantity']}",
                f"\u200E ₪ {r['cost_price']:,.2f}",
                f"\u200E ₪ {tot_cost:,.2f}",
                f"\u200E ₪ {tot_profit:,.2f}",
                r["notes"] or "—"
            ]
            for v in vals:
                ctk.CTkLabel(row, text=v, font=(FONT, 12), text_color=self.C["text"],
                             width=100).pack(side="right", padx=3, pady=8)
            ctk.CTkButton(row, text="", width=32, height=32, fg_color="transparent",
                          image=self._del_icon,
                          hover_color=self.C["danger_bg"], text_color=self.C["danger"], corner_radius=8,
                          command=lambda rid=r["id"]: self._del(rid)).pack(side="left", padx=6)

        self._kpi_count.configure(text=f"\u200E{len(rows)}")
        self._kpi_qty.configure(text=f"\u200E{tq:,}")
        self._kpi_cost.configure(text=f"\u200E ₪ {tc:,.2f}")

    def _apply_filter(self):
        f = self._from_e.get().strip()
        t = self._to_e.get().strip()
        
        def parse_date(ds):
            if not ds: return None
            if "/" in ds or "-" in ds:
                p = ds.replace("/", "-").split("-")
                if len(p) == 3:
                    if len(p[0]) == 4: return f"{p[0]}-{p[1].zfill(2)}-{p[2].zfill(2)}"
                    if len(p[2]) == 4: return f"{p[2]}-{p[1].zfill(2)}-{p[0].zfill(2)}"
            return ds
            
        self._from_date = parse_date(f)
        self._to_date = parse_date(t)
        self.refresh()

    def _pick_date(self, entry):
        show_date_picker(self, entry, self.C)

    def _clear_filter(self):
        self._from_e.delete(0, "end")
        self._to_e.delete(0, "end")
        self._from_date = self._to_date = None
        self.refresh()

    def _open_add(self):
        _SupplyDialog(self, self.C, on_save=self.refresh)

    def _del(self, sid):
        from tkinter import messagebox
        if messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من حذف هذه العملية؟"):
            db.delete_supply(sid); self.refresh()


class _SupplyDialog(ctk.CTkToplevel):
    def __init__(self, parent, colors, on_save=None):
        super().__init__(parent)
        self.C = colors
        self._on_save = on_save
        self._selected_product = None
        self._all_products = db.get_all_products()
        
        self.title("توريد جديد")
        self.geometry("850x690")
        self.resizable(False, False)
        self.configure(fg_color=self.C["bg"])
        self.grab_set()
        
        self.update_idletasks()
        try:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            px = (sw - 850) // 2
            py = (sh - 690) // 2
            self.geometry(f"850x690+{px}+{py}")
        except: pass
            
        self._build()

    def _build(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ━━━ Right Frame: Product Grid ━━━
        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent", width=450)
        right_frame.pack(side="right", fill="both", expand=True, padx=(15, 0))
        right_frame.pack_propagate(False)

        ctk.CTkLabel(right_frame, text="اختر الصنف", font=(FONT_HDR, 20, "bold"), text_color=self.C["accent"]).pack(anchor="e", pady=(0, 10))
        
        search_entry = ctk.CTkEntry(right_frame, placeholder_text="ابحث عن صنف...", font=(FONT_REG, 14), height=40, justify="right", fg_color=self.C["input"], border_color=self.C["border"])
        search_entry.pack(fill="x", pady=(0, 10))
        search_entry.bind("<KeyRelease>", lambda e: self._populate_products(search_entry.get()))

        self._prod_scroll = ctk.CTkScrollableFrame(right_frame, fg_color=self.C["card"], corner_radius=15)
        self._prod_scroll.pack(fill="both", expand=True)

        # ━━━ Left Frame: Form ━━━
        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent", width=350)
        left_frame.pack(side="left", fill="both", padx=(0, 15))
        left_frame.pack_propagate(False)

        ctk.CTkLabel(left_frame, text="تفاصيل التوريد", font=(FONT_HDR, 20, "bold"), text_color=self.C["accent"]).pack(anchor="e", pady=(0, 10))
        
        self._sel_frame = ctk.CTkFrame(left_frame, fg_color=self.C["card"], corner_radius=10, height=45)
        self._sel_frame.pack(fill="x", pady=(0, 15))
        self._sel_frame.pack_propagate(False)
        
        self._sel_title_fr = ctk.CTkFrame(self._sel_frame, fg_color="transparent", corner_radius=10, width=100)
        self._sel_title_fr.pack(side="right", fill="y", padx=2, pady=2)
        self._sel_title_fr.pack_propagate(False)
        self._sel_title_lbl = ctk.CTkLabel(self._sel_title_fr, text=":الصنف المختار", font=(FONT_REG, 12, "bold"), text_color=self.C["text2"])
        self._sel_title_lbl.pack(expand=True)

        self._sel_name_lbl = ctk.CTkLabel(self._sel_frame, text="لم يتم الاختيار بعد", font=(FONT_REG, 14, "bold"), text_color=self.C["danger"])
        self._sel_name_lbl.pack(side="right", expand=True, fill="both", padx=5)

        self._qty_var = ctk.StringVar()
        self._cost_var = ctk.StringVar()

        def premium_field(label, ph="", var=None, has_cal=False):
            lbl = ctk.CTkLabel(left_frame, text=label, font=(FONT_REG, 13, "bold"), text_color=self.C["text"], anchor="e")
            lbl.pack(fill="x", pady=(5, 2))
            
            f = ctk.CTkFrame(left_frame, fg_color="transparent")
            f.pack(fill="x")
            
            e = ctk.CTkEntry(f, placeholder_text=ph, textvariable=var, font=(FONT_REG, 14), height=40,
                              fg_color=self.C["input"], border_width=1, border_color=self.C["border"],
                              text_color=self.C["text"], corner_radius=10, justify="right")
            e.pack(side="right", fill="x", expand=True)
            
            if has_cal:
                btn = ctk.CTkButton(f, text="", width=35, height=40, fg_color="transparent", image=get_icon("calendar", (20, 20)),
                                    hover_color=self.C["sidebar"], command=lambda: self._pick_date(e))
                btn.pack(side="right", padx=(5, 0))
            return e

        self._qty = premium_field("الكمية المطلوبة *", "مثال: 50", self._qty_var)
        self._cost = premium_field("سعر الشراء (للوحدة)", "0.00", self._cost_var)
        
        # حسابات ديناميكية (Slim Design)
        calc_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        calc_frame.pack(fill="x", pady=(15, 5))
        
        def badge(parent, label, value, color, dark_color):
            f = ctk.CTkFrame(parent, fg_color=color, corner_radius=10, height=40)
            f.pack(fill="x", pady=3)
            f.pack_propagate(False)
            
            ctk.CTkLabel(f, text=label, font=(FONT_REG, 12, "bold"), text_color="#FFFFFF").pack(side="right", padx=15)
            
            val_f = ctk.CTkFrame(f, fg_color=dark_color, corner_radius=8, width=120)
            val_f.pack(side="left", padx=5, pady=4, fill="y")
            val_f.pack_propagate(False)
            
            lbl = ctk.CTkLabel(val_f, text=value, font=(FONT_REG, 13, "bold"), text_color="#FFFFFF")
            lbl.pack(expand=True)
            return lbl

        self._lbl_total_cost = badge(calc_frame, "إجمالي التكلفة", "0.00 ₪", "#E11D48", "#9F1239")
        self._lbl_total_sale = badge(calc_frame, "قيمة المبيعات", "0.00 ₪", "#2563EB", "#1E40AF")
        self._lbl_total_profit = badge(calc_frame, "صافي الربح", "0.00 ₪", "#16A34A", "#166534")

        self._qty_var.trace_add("write", self._calc)
        self._cost_var.trace_add("write", self._calc)

        self._date_e = premium_field("تاريخ العملية", "YYYY-MM-DD", has_cal=True)
        self._date_e.insert(0, date.today().isoformat())
        
        self._notes = premium_field("ملاحظات", "اختياري")

        btn_row = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_row.pack(fill="x", side="bottom", pady=(20, 0))
        
        ctk.CTkButton(btn_row, text="إتمام التوريد", font=(FONT_REG, 15, "bold"),
                      fg_color=self.C["accent"], text_color=self.C["btn_text"], hover_color="#00BFA0",
                      corner_radius=12, height=48, command=self._save).pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        ctk.CTkButton(btn_row, text="إلغاء", font=(FONT_REG, 14),
                      fg_color="#F1F5F9", text_color="#64748B", hover_color="#E2E8F0",
                      corner_radius=12, height=48, command=self.destroy).pack(side="right", fill="x", expand=True, padx=(0, 5))

        self._populate_products()

    def _populate_products(self, term=""):
        for w in self._prod_scroll.winfo_children():
            w.destroy()
        
        from page_products import _get_product_image
        term = term.lower().strip()
        self._cards = {} # Store cards to manage selection highlight
        
        for p in self._all_products:
            if term and term not in p["name"].lower() and term not in (p["code"] or "").lower():
                continue
            
            card = ctk.CTkFrame(self._prod_scroll, fg_color=self.C["bg"], corner_radius=10, cursor="hand2")
            card.pack(fill="x", pady=4, padx=4)
            self._cards[p["id"]] = card
            
            # Re-apply selection color if this was already selected
            if self._selected_product and self._selected_product["id"] == p["id"]:
                card.configure(fg_color=self.C["sidebar"])

            img = _get_product_image(p, size=(45, 45))
            img_lbl = ctk.CTkLabel(card, text="", image=img)
            img_lbl.pack(side="right", padx=10, pady=8)
            
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="right", fill="both", expand=True, padx=5, pady=8)
            
            name_lbl = ctk.CTkLabel(info, text=p["name"], font=(FONT_REG, 14, "bold"), text_color=self.C["text"], anchor="e")
            name_lbl.pack(fill="x")
            
            price_lbl = ctk.CTkLabel(info, text=f"تكلفة: \u200E{p['cost_price']} ₪  |  بيع: \u200E{p['sell_price']} ₪", font=(FONT_REG, 11), text_color=self.C["text2"], anchor="e")
            price_lbl.pack(fill="x", pady=(2, 0))
            
            for w in [card, img_lbl, info, name_lbl, price_lbl]:
                w.bind("<Button-1>", lambda e, prod=p: self._select_product(prod))

    def _select_product(self, p):
        self._selected_product = p
            
        self._sel_frame.configure(fg_color="#3B82F6") # Light Blue
        self._sel_title_fr.configure(fg_color="#1E40AF") # Dark Blue
        self._sel_title_lbl.configure(text_color="#FFFFFF")
        self._sel_name_lbl.configure(text=p['name'], text_color="#FFFFFF")
        
        self._cost_var.set(str(p["cost_price"]))
        self._calc()

    def _calc(self, *args):
        if not self._selected_product: return
        try:
            qty = float(self._qty_var.get() or 0)
            cost = float(self._cost_var.get() or 0)
            sell = float(self._selected_product["sell_price"] or 0)
            
            total_cost = qty * cost
            total_sale = qty * sell
            expected_profit = total_sale - total_cost
            
            self._lbl_total_cost.configure(text=f"{total_cost:,.2f} ₪")
            self._lbl_total_sale.configure(text=f"{total_sale:,.2f} ₪")
            self._lbl_total_profit.configure(text=f"{expected_profit:,.2f} ₪")
        except:
            self._lbl_total_cost.configure(text="0.00 ₪")
            self._lbl_total_sale.configure(text="0.00 ₪")
            self._lbl_total_profit.configure(text="0.00 ₪")

    def _pick_date(self, entry):
        import calendar
        from datetime import date
        
        top = ctk.CTkToplevel(self)
        top.title("اختر التاريخ")
        top.geometry("320x360")
        top.configure(fg_color=self.C["bg"])
        top.attributes("-topmost", True)
        top.grab_set()
        
        sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
        top.geometry(f"+{(sw-320)//2}+{(sh-360)//2}")
        
        today = date.today()
        curr_yr = [today.year]
        curr_mo = [today.month]
        view_mode = ["days"]
        
        ar_months = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", 
                     "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
        
        hdr = ctk.CTkFrame(top, fg_color="transparent")
        hdr.pack(fill="x", padx=10, pady=10)
        
        mo_btn = ctk.CTkButton(hdr, text="", font=(FONT_REG, 15, "bold"), text_color=self.C["text"],
                               fg_color=self.C["card"], border_width=1, border_color=self.C["border"],
                               hover_color=self.C["hover"], corner_radius=8, height=35, command=lambda: toggle_view())
        mo_btn.pack(side="right", expand=True)
        
        main_fr = ctk.CTkFrame(top, fg_color="transparent")
        main_fr.pack(fill="both", expand=True, padx=10, pady=5)
        
        def render():
            for w in main_fr.winfo_children(): w.destroy()
            
            if view_mode[0] == "days":
                mo_btn.configure(text=f"{ar_months[curr_mo[0]-1]} {curr_yr[0]}")
                for c, d in enumerate(["أحد","إثنين","ثلاثاء","أربعاء","خميس","جمعة","سبت"]):
                    ctk.CTkLabel(main_fr, text=d, font=(FONT_REG, 11, "bold"), text_color=self.C["text2"]).grid(row=0, column=6-c, padx=4, pady=5)
                
                cal = calendar.Calendar(firstweekday=6)
                for r, week in enumerate(cal.monthdayscalendar(curr_yr[0], curr_mo[0])):
                    for c, day in enumerate(week):
                        if day != 0:
                            is_today = (curr_yr[0] == today.year and curr_mo[0] == today.month and day == today.day)
                            bg = self.C["accent"] if is_today else self.C["card"]
                            tc = "#FFF" if is_today else self.C["text"]
                            btn = ctk.CTkButton(main_fr, text=str(day), width=35, height=35, font=(FONT_REG, 13, "bold"),
                                                fg_color=bg, text_color=tc, hover_color=self.C["hover"], corner_radius=8,
                                                command=lambda d=day: pick(d))
                            btn.grid(row=r+1, column=6-c, padx=3, pady=2)
            else:
                mo_btn.configure(text=f"{curr_yr[0]}")
                for i in range(12):
                    r = i // 3; c = i % 3
                    is_curr = (curr_yr[0] == today.year and (i+1) == today.month)
                    bg = self.C["accent"] if is_curr else self.C["card"]
                    tc = "#FFF" if is_curr else self.C["text"]
                    btn = ctk.CTkButton(main_fr, text=ar_months[i], width=85, height=45, font=(FONT_REG, 14, "bold"),
                                        fg_color=bg, text_color=tc, hover_color=self.C["hover"], corner_radius=8,
                                        command=lambda m=(i+1): pick_month(m))
                    btn.grid(row=r, column=2-c, padx=5, pady=5)
                        
        def toggle_view():
            view_mode[0] = "months" if view_mode[0] == "days" else "days"
            render()

        def pick_month(m):
            curr_mo[0] = m; view_mode[0] = "days"; render()

        def pick(d):
            entry.delete(0, "end")
            entry.insert(0, f"{curr_yr[0]}-{curr_mo[0]:02d}-{d:02d}")
            top.destroy()

        def shift(m):
            if view_mode[0] == "days":
                curr_mo[0] += m
                if curr_mo[0] > 12: curr_mo[0] = 1; curr_yr[0] += 1
                if curr_mo[0] < 1: curr_mo[0] = 12; curr_yr[0] -= 1
            else:
                curr_yr[0] += m
            render()
            
        ctk.CTkButton(hdr, text="<", width=30, fg_color=self.C["card"], text_color=self.C["text"], hover_color=self.C["hover"], command=lambda: shift(1)).pack(side="left")
        ctk.CTkButton(hdr, text=">", width=30, fg_color=self.C["card"], text_color=self.C["text"], hover_color=self.C["hover"], command=lambda: shift(-1)).pack(side="right")
        render()

    def _save(self):
        if not self._selected_product:
            from tkinter import messagebox
            messagebox.showerror("تنبيه", "الرجاء اختيار صنف من القائمة أولاً", parent=self)
            return
        try:
            qty = int(self._qty_var.get() or 0)
            if qty <= 0: return
        except: return
        
        try:
            cost = float(self._cost_var.get() or 0)
        except:
            cost = 0.0

        s_date = self._date_e.get().strip() or date.today().isoformat()
        db.add_supply(self._selected_product["id"], qty, cost, "", self._notes.get().strip(), s_date)
        if self._on_save: self._on_save()
        self.destroy()

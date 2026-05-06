"""
صفحة الجرد المبسط (الجرد السهل) – النسخة العصرية المطورة
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

class InventoryPage(ctk.CTkFrame):
    def __init__(self, parent, colors):
        super().__init__(parent, fg_color=colors["bg"], corner_radius=0)
        self.C = colors
        self._current_session = None
        self._rep_data = []
        self._summary = {}
        
        self._inv_icon  = get_icon("inventory", (28, 28))
        self._plus_icon = get_icon("add", (20, 20))
        self._save_icon = get_icon("save", (20, 20))
        self._save_icon_w = get_white_icon("save", (22, 22))
        
        self._build()

    def _build(self):
        # ═══ Top Header ═══
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=30, pady=(20, 15))
        
        title_f = ctk.CTkFrame(hdr, fg_color="transparent")
        title_f.pack(side="right")
        ctk.CTkLabel(title_f, text=" جرد نهاية الأسبوع", font=(FONT_HDR, 26, "bold"), text_color=self.C["accent"]).pack(side="right")
        ctk.CTkLabel(title_f, text="", image=self._inv_icon).pack(side="right", padx=10)

        ctk.CTkButton(hdr, text="جلسة جرد جديدة", font=(FONT, 14, "bold"), image=self._plus_icon, compound="right", fg_color=self.C["accent"], text_color="#FFFFFF", corner_radius=12, height=44, command=self._new_session).pack(side="left")

        # ═══ Session & Search ═══
        top_bar = ctk.CTkFrame(self, fg_color=self.C["card"], corner_radius=15, border_width=1, border_color=self.C["border"])
        top_bar.pack(fill="x", padx=30, pady=(0, 20))
        
        ctk.CTkLabel(top_bar, text=": اختر الجلسة", font=(FONT, 13, "bold"), text_color=self.C["text2"]).pack(side="right", padx=(20, 5), pady=15)
        self._sess_combo = ctk.CTkComboBox(top_bar, values=[], font=(FONT, 14), width=220, height=38, corner_radius=10, fg_color=self.C["input"], border_color=self.C["border"], button_color=self.C["accent"], command=lambda x: self._load_report())
        self._sess_combo.pack(side="right", padx=5)

        # Delete Session Button
        self._del_sess_btn = ctk.CTkButton(top_bar, text="", width=38, height=38, fg_color="transparent", image=get_icon("delete", (20, 20)), hover_color=self.C["danger_f"], command=self._delete_session)
        self._del_sess_btn.pack(side="right", padx=5)
        
        self._search_e = ctk.CTkEntry(top_bar, placeholder_text="🔍 ابحث عن صنف لجرده...", font=(FONT, 14), height=38, width=250, fg_color=self.C["input"], border_color=self.C["border"], corner_radius=10, justify="right")
        self._search_e.pack(side="left", padx=(20, 5))
        self._search_e.bind("<KeyRelease>", lambda e: self._filter_cards())

        # Save All Button
        ctk.CTkButton(top_bar, text="حفظ الكل", font=(FONT, 13, "bold"), image=self._save_icon_w, compound="right", width=110, height=38, fg_color=self.C["blue"], hover_color="#1E40AF", corner_radius=10, command=self._save_all).pack(side="left", padx=5)

        # ═══ Main Scrollable Area ═══
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=25)

        # ═══ Bottom Sticky Summary ═══
        self._bot_bar = ctk.CTkFrame(self, fg_color=self.C["sidebar"], height=80, corner_radius=0)
        self._bot_bar.pack(fill="x", side="bottom")
        self._bot_bar.pack_propagate(False)
        
        self._res_lbl = ctk.CTkLabel(self._bot_bar, text="يرجى اختيار جلسة جرد والبدء بإدخال الكميات المتبقية", font=(FONT, 16, "bold"), text_color=self.C["text2"])
        self._res_lbl.pack(expand=True)

        self._refresh_sessions()

    def _refresh_sessions(self):
        sessions = db.get_inventory_sessions()
        names = [f"{s['id']} | {s['name'] or 'جرد'} ({s['start_date']})" for s in sessions]
        self._sess_combo.configure(values=names)
        if names:
            self._sess_combo.set(names[0])
            self._load_report()
        else:
            self._sess_combo.set("")
            for w in self._scroll.winfo_children(): w.destroy()
            for w in self._bot_bar.winfo_children(): w.destroy()
            self._res_lbl = ctk.CTkLabel(self._bot_bar, text="لا توجد جلسات جرد حالياً. ابدأ جلسة جديدة", 
                                         font=(FONT, 16, "bold"), text_color=self.C["text2"])
            self._res_lbl.pack(expand=True)

    def _delete_session(self):
        val = self._sess_combo.get()
        if not val: return
        sid = int(val.split("|")[0].strip())
        from tkinter import messagebox
        if messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من حذف جلسة الجرد هذه بالكامل؟"):
            db.delete_inventory_session(sid)
            self._refresh_sessions()

    def _load_report(self):
        val = self._sess_combo.get()
        if not val: return
        sid = int(val.split("|")[0].strip())
        self._current_session = sid
        sess, rep, summ = db.get_inventory_report(sid)
        self._rep_data = rep
        self._summary = summ
        self._render_cards()
        self._update_summary()

    def _render_cards(self):
        for w in self._scroll.winfo_children(): w.destroy()
        self._entries = {} # {product_id: entry_widget}
        
        # Grid layout for cards
        grid = ctk.CTkFrame(self._scroll, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure((0, 1, 2), weight=1, pad=20)

        for i, r in enumerate(self._rep_data):
            card = ctk.CTkFrame(grid, fg_color=self.C["card"], corner_radius=20, border_width=1, border_color=self.C["border"])
            card.grid(row=i//3, column=2-(i%3), padx=10, pady=10, sticky="nsew")
            card._row_data = r
            
            # Header: Name
            head = ctk.CTkFrame(card, fg_color="transparent")
            head.pack(fill="x", padx=10, pady=(10, 0))
            
            ctk.CTkLabel(head, text=r["name"], font=(FONT, 15, "bold"), text_color=self.C["text"], anchor="e").pack(side="right", fill="x", expand=True)
            
            # Header: Code (Completely Separated for RTL)
            code_f = ctk.CTkFrame(card, fg_color="transparent")
            code_f.pack(fill="x", padx=15, pady=(0, 10))
            ctk.CTkLabel(code_f, text="كود", font=(FONT, 11), text_color=self.C["text2"]).pack(side="right")
            ctk.CTkLabel(code_f, text=" : ", font=(FONT, 11), text_color=self.C["text2"]).pack(side="right")
            ctk.CTkLabel(code_f, text=f"{r['code']}", font=(FONT, 11), text_color=self.C["text2"]).pack(side="right")
            
            # استخدام إطار داخلي لضمان ترتيب النصوص من اليمين لليسار بشكل سليم
            mid = ctk.CTkFrame(card, fg_color=self.C["accent_f"], corner_radius=10)
            mid.pack(fill="x", padx=15, pady=5)
            inner_mid = ctk.CTkFrame(mid, fg_color="transparent")
            inner_mid.pack(pady=8)
            
            # تقسيم النص لأربعة أجزاء لضمان الاتجاه الصحيح 100% (الكمية الموردة : 10 قطعة)
            ctk.CTkLabel(inner_mid, text="الكمية الموردة", font=(FONT, 13, "bold"), text_color=self.C["accent"]).pack(side="right")
            ctk.CTkLabel(inner_mid, text=" : ", font=(FONT, 13, "bold"), text_color=self.C["accent"]).pack(side="right")
            ctk.CTkLabel(inner_mid, text=f"{r['supplied']}", font=(FONT, 13, "bold"), text_color=self.C["accent"]).pack(side="right")
            ctk.CTkLabel(inner_mid, text=f" {r['unit']}", font=(FONT, 13, "bold"), text_color=self.C["accent"]).pack(side="right")
            
            # Input Area
            ctk.CTkLabel(card, text="كم الكمية الفعلية المتبقية؟", font=(FONT, 12), text_color=self.C["text2"]).pack(pady=(10, 0))
            
            inp_f = ctk.CTkFrame(card, fg_color="transparent")
            inp_f.pack(pady=5, padx=15)
            
            ent = ctk.CTkEntry(inp_f, width=100, height=45, font=(FONT, 18, "bold"), fg_color=self.C["input"], border_color=self.C["accent"], text_color=self.C["accent"], corner_radius=10, justify="center")
            ent.pack(side="right")
            self._entries[r["product_id"]] = ent
            # نضع الكمية الموردة كقيمة افتراضية إذا لم يتم الجرد بعد، لتسهيل العمل
            val_to_show = r["actual"] if r["actual"] is not None else r["supplied"]
            ent.insert(0, str(val_to_show))
            
            # Action: Save individual card
            btn = ctk.CTkButton(inp_f, text="حفظ", width=60, height=45, fg_color=self.C["accent"], hover_color="#00897B", corner_radius=10, font=(FONT, 13, "bold"), command=lambda e=ent, pid=r["product_id"]: self._save_item(pid, e))
            btn.pack(side="right", padx=(5, 0))
            
            # Result on card
            res_f = ctk.CTkFrame(card, fg_color="transparent")
            res_f.pack(fill="x", padx=15, pady=(10, 15))
            if r["actual"] is not None:
                sold = r["sold"]
                val = r["deficit_value"]
                # Breaking down to fix RTL flipping
                txt_f = ctk.CTkFrame(res_f, fg_color="transparent")
                txt_f.pack()
                ctk.CTkLabel(txt_f, text="تم بيع", font=(FONT, 12), text_color=self.C["blue"]).pack(side="right")
                ctk.CTkLabel(txt_f, text=f" \u200E{sold} ", font=(FONT, 12, "bold"), text_color=self.C["blue"]).pack(side="right")
                ctk.CTkLabel(txt_f, text="قطع بقيمة", font=(FONT, 12), text_color=self.C["blue"]).pack(side="right")
                ctk.CTkLabel(txt_f, text=f" \u200E₪{val:,.0f} ", font=(FONT, 12, "bold"), text_color=self.C["blue"]).pack(side="right")
            else:
                ctk.CTkLabel(res_f, text="بانتظار العد...", font=(FONT, 12, "italic"), text_color=self.C["text2"]).pack()

    def _save_item(self, pid, entry):
        val = entry.get().strip()
        if not val: return
        try: actual = int(val)
        except: return
        db.save_inventory_item(self._current_session, pid, actual, "")
        self._load_report() # Refresh UI

    def _save_all(self):
        if not self._current_session: return
        for pid, ent in self._entries.items():
            val = ent.get().strip()
            if val:
                try:
                    actual = int(val)
                    db.save_inventory_item(self._current_session, pid, actual, "")
                except: continue
        self._load_report()
        from tkinter import messagebox
        messagebox.showinfo("نجاح", "تم حفظ جميع القيم وتحديث التقرير.")

    def _clear_item(self, pid):
        db.delete_inventory_item(self._current_session, pid)
        self._load_report()

    def _update_summary(self):
        s = self._summary
        if not s: return
        
        diff = s["net_result"]
        res_text = "النتيجة النهائية: "
        if diff == 0:
            res_text += "الحسابات مطابقة تماماً ✅"
            color = self.C["success"]
        elif diff < 0:
            res_text += f"يوجد عجز مالي بمقدار "
            color = self.C["danger"]
        else:
            res_text += f"يوجد زيادة (فائض) بمقدار "
            color = self.C["success"]
            
        for w in self._bot_bar.winfo_children(): w.destroy()
        
        main_f = ctk.CTkFrame(self._bot_bar, fg_color="transparent")
        main_f.pack(expand=True, fill="both", padx=30)
        
        # Result Button (Left)
        res_btn = ctk.CTkFrame(main_f, fg_color=color, corner_radius=15, height=54)
        res_btn.pack(side="left", padx=20, pady=13)
        
        btn_inner = ctk.CTkFrame(res_btn, fg_color="transparent")
        btn_inner.pack(padx=25, pady=10)
        
        # Correctly order text and value
        ctk.CTkLabel(btn_inner, text=f" \u200E₪{abs(diff):,.2f}", font=(FONT, 18, "bold"), text_color="#FFFFFF").pack(side="left")
        ctk.CTkLabel(btn_inner, text=res_text, font=(FONT, 18, "bold"), text_color="#FFFFFF").pack(side="left", padx=(5, 0))

        # KPIs (Right) - Separate labels to fix RTL mess
        kpi_f = ctk.CTkFrame(main_f, fg_color="transparent")
        kpi_f.pack(side="right", fill="y")
        
        def add_kpi(label, val, color=None):
            f = ctk.CTkFrame(kpi_f, fg_color="transparent")
            f.pack(side="right", padx=10)
            # Label on the right
            ctk.CTkLabel(f, text=label + ":", font=(FONT, 14), text_color=self.C["text2"]).pack(side="right")
            # Value to its left
            ctk.CTkLabel(f, text=f" \u200E₪{val:,.0f} ", font=(FONT, 17, "bold"), text_color=color or self.C["text"]).pack(side="right", padx=(5, 0))
            # Separator to the left of the value
            ctk.CTkLabel(f, text="  |", font=(FONT, 16), text_color=self.C["border"]).pack(side="right", padx=(10, 0))

        add_kpi("المقبوضات", s["total_sales"], self.C["success"])
        add_kpi("المصاريف", s["total_expenses"], self.C["danger"])
        add_kpi("الديون", s["total_debts"], self.C["warning"])
        add_kpi("بضاعة خارجة", s["physical_deficit_value"], self.C["accent"])

    def _filter_cards(self):
        q = self._search_e.get().strip().lower()
        for w in self._scroll.winfo_children():
            # w is the grid frame
            for card in w.winfo_children():
                if hasattr(card, "_row_data"):
                    r = card._row_data
                    if q in r["name"].lower() or q in r["code"].lower():
                        card.grid(padx=10, pady=10, sticky="nsew")
                    else:
                        card.grid_forget()

    def _new_session(self):
        def on_save(new_id):
            self._refresh_sessions()
            # البحث عن الجلسة الجديدة في القائمة واختيارها
            for val in self._sess_combo.cget("values"):
                if val.startswith(f"{new_id} |"):
                    self._sess_combo.set(val)
                    self._load_report()
                    break
        _SessionDialog(self, self.C, on_save=on_save)

    def refresh(self):
        self._refresh_sessions()

class _SessionDialog(ctk.CTkToplevel):
    def __init__(self, parent, colors, on_save=None):
        super().__init__(parent)
        self.C = colors; self._on_save = on_save
        self.title("جلسة جرد جديدة"); self.geometry("460x580")
        self.resizable(False, False); self.configure(fg_color=self.C["bg"]); self.grab_set()
        self.update_idletasks()
        try:
            sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
            self.geometry(f"460x580+{(sw-460)//2}+{(sh-580)//2}")
        except: pass
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color=self.C["accent"], corner_radius=0, height=80)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="بدء جلسة جرد جديدة", font=(FONT_HDR, 22, "bold"), text_color="#FFFFFF").pack(expand=True)
        
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=40, pady=(20, 10))
        
        def field(label, ph="", has_cal=False):
            ctk.CTkLabel(body, text=label, font=(FONT, 14, "bold"), text_color=self.C["text"], anchor="e").pack(fill="x", pady=(5, 2))
            f = ctk.CTkFrame(body, fg_color="transparent"); f.pack(fill="x", pady=(0, 12))
            e = ctk.CTkEntry(f, placeholder_text=ph, font=(FONT, 15), height=42, fg_color=self.C["input"], border_color=self.C["border"], text_color=self.C["text"], corner_radius=10, justify="right")
            e.pack(side="right", fill="x", expand=True)
            if has_cal:
                ctk.CTkButton(f, text="", width=35, height=42, fg_color="transparent", image=get_icon("calendar", (20, 20)), corner_radius=10, hover_color=self.C["sidebar"], command=lambda: self.show_calendar(self, e, self.C)).pack(side="right", padx=(5, 0))
            return e
            
        self._name = field("عنوان الجلسة", "مثال: جرد الأسبوع")
        self._from = field("من تاريخ *", "YYYY-MM-DD", True)
        self._from.insert(0, date.today().replace(day=1).isoformat())
        self._to   = field("إلى تاريخ *", "YYYY-MM-DD", True)
        self._to.insert(0, date.today().isoformat())
        self._notes = field("ملاحظات")

        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x", pady=(25, 0))
        ctk.CTkButton(btn_row, text="💾 إنشاء الجلسة", font=(FONT, 16, "bold"), fg_color=self.C["accent"], height=48, corner_radius=12, command=self._save).pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkButton(btn_row, text="إلغاء", font=(FONT, 15), fg_color="#F1F5F9", text_color="#475569", height=48, corner_radius=12, command=self.destroy).pack(side="right", fill="x", expand=True, padx=(0, 5))

    def _save(self):
        f, t = self._from.get().strip(), self._to.get().strip()
        if not f or not t: return
        # تصحيح اسم الدالة وترتيب المدخلات (تاريخ البدء، تاريخ الانتهاء، الاسم، الملاحظات)
        db.create_inventory_session(f, t, self._name.get().strip(), self._notes.get().strip())
        # جلب ID الجلسة التي أُنشئت للتو
        sessions = db.get_inventory_sessions()
        new_id = sessions[0]["id"] if sessions else None
        if self._on_save: self._on_save(new_id)
        self.destroy()

    @staticmethod
    def show_calendar(parent, entry, C):
        from page_sales import _SaleDialog
        _SaleDialog.show_calendar(parent, entry, C)

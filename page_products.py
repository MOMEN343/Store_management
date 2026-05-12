"""
صفحة الأصناف – بطاقات مع صور (مش جدول!)
"""
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import os, shutil
import database as db

FONT_HDR = "Thmanyah Sans"
FONT_REG = "Cairo"
FONT = FONT_REG
import sys
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
IMG_DIR  = os.path.join(BASE_DIR, "product_images")
ICON_DIR = os.path.join(BASE_DIR, "icons")
os.makedirs(IMG_DIR, exist_ok=True)

def get_icon(name, size=(20, 20)):
    """تحميل أيقونة بجودة عالية للوضعين الفاتح والداكن"""
    try:
        light_path = os.path.join(ICON_DIR, f"{name}_light.png")
        dark_path  = os.path.join(ICON_DIR, f"{name}_dark.png")
        from PIL import Image
        return ctk.CTkImage(
            light_image=Image.open(light_path),
            dark_image=Image.open(dark_path),
            size=size
        )
    except:
        return None

# ألوان الفئات
CAT_COLORS = [
    "#0D9488", "#3B82F6", "#F59E0B", "#EF4444",
    "#10B981", "#8B5CF6", "#14B8A6", "#F59E0B",
    "#EC4899", "#0EA5E9",
]


def _get_product_image(product, size=(80, 80)):
    """تحميل صورة المنتج أو إنشاء placeholder ملون"""
    img_path = os.path.join(IMG_DIR, f"{product['id']}.png")
    if os.path.exists(img_path):
        try:
            img = Image.open(img_path)
            img = img.resize(size, Image.LANCZOS)
            return ctk.CTkImage(img, size=size)
        except:
            pass

    # Placeholder: صورة ملونة بحرف المنتج (شكل دائري أو مربع بحدود ناعمة)
    color_idx = product["id"] % len(CAT_COLORS)
    color = CAT_COLORS[color_idx]

    from PIL import ImageDraw, ImageFont
    # ننشئ صورة أكبر للتنعيم (Antialiasing)
    canvas_size = (size[0]*4, size[1]*4)
    img = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # رسم مربع بحدود دائرية
    draw.rounded_rectangle([0, 0, canvas_size[0], canvas_size[1]], radius=40, fill=color)
    
    # أول حرف من اسم المنتج
    letter = product["name"][0] if product["name"] else "?"
    try:
        font = ImageFont.truetype("arial.ttf", size[0]*2)
    except:
        font = ImageFont.load_default()
        
    bbox = draw.textbbox((0, 0), letter, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (canvas_size[0] - tw) // 2
    y = (canvas_size[1] - th) // 2 - bbox[1]
    draw.text((x, y), letter, fill="#FFFFFF", font=font)
    
    img = img.resize(size, Image.LANCZOS)
    return ctk.CTkImage(img, size=size)


class ProductsPage(ctk.CTkFrame):
    def __init__(self, parent, colors):
        super().__init__(parent, fg_color=colors["bg"], corner_radius=0)
        self.C = colors
        
        # Load Icons
        self._edit_icon = get_icon("edit", (18, 18))
        self._del_icon  = get_icon("delete", (18, 18))
        self._box_icon  = get_icon("supply", (18, 18))
        self._plus_icon = get_icon("add", (20, 20))
        self._prod_icon = get_icon("products", (28, 28))
        
        self._build()


    def _build(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 10))

        ctk.CTkLabel(hdr, text="  إدارة الأصناف",
                     font=(FONT_HDR, 24, "bold"),
                     image=self._prod_icon, compound="right",
                     text_color=self.C["accent"]).pack(side="right")


        ctk.CTkButton(hdr, text="إضافة صنف جديد",
                      font=(FONT, 15, "bold"),
                      image=self._plus_icon, compound="right",
                      fg_color=self.C["accent"], text_color=self.C["btn_text"],
                      hover_color="#00BFA0", corner_radius=10,
                      height=44, command=self._open_add).pack(side="left")

        # Search
        search_frame = ctk.CTkFrame(self, fg_color=self.C["card"], corner_radius=12, height=50)
        search_frame.pack(fill="x", padx=24, pady=(0, 12))

        self._search_entry = ctk.CTkEntry(search_frame, placeholder_text="ابحث باسم المنتج، الكود، أو الفئة",
                                          font=(FONT, 14), height=44,
                                          fg_color=self.C["input"], border_color=self.C["border"],
                                          text_color=self.C["text"], placeholder_text_color="#64748B",
                                          corner_radius=10,
                                          justify="right")
        self._search_entry.pack(fill="x", padx=12, pady=8)
        self._search_entry.bind("<KeyRelease>", self._on_search_key)
        self._search_timer = None

        # Cards container (scrollable)
        self._scroll = ctk.CTkScrollableFrame(self, fg_color=self.C["bg"],
                                               corner_radius=0,
                                               scrollbar_button_color=self.C["muted"],
                                               scrollbar_button_hover_color=self.C["accent"])
        self._scroll.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        # Stats bar
        stats = ctk.CTkFrame(self, fg_color=self.C["card"], corner_radius=12, height=48)
        stats.pack(fill="x", padx=24, pady=(0, 12))
        stats.pack_propagate(False)
        
        # Container for RTL stats
        self._stats_container = ctk.CTkFrame(stats, fg_color="transparent")
        self._stats_container.pack(side="right", padx=20)

        

    def _on_search_key(self, event):
        """تأخير البحث قليلاً لتجنب التعليق أثناء الكتابة (Debounce)"""
        if self._search_timer:
            self.after_cancel(self._search_timer)
        self._search_timer = self.after(300, self._filter)

    def refresh(self):
        self._all = db.get_all_products()
        self._filter()

    def _filter(self):
        term = self._search_entry.get().strip().lower()
        rows = self._all if hasattr(self, '_all') else []
        if term:
            rows = [r for r in rows
                    if term in r["name"].lower()
                    or term in r["code"].lower()
                    or term in (r["category"] or "").lower()]

        # Clear old cards
        for w in self._scroll.winfo_children():
            w.destroy()

        if not rows:
            msg = "عفواً، لا توجد نتائج تطابق بحثك..." if term else "لا توجد أصناف بعد ... أضف صنفك الأول! "
            ctk.CTkLabel(self._scroll, text=msg,
                         font=(FONT, 18), text_color=self.C["text2"]).pack(pady=60)
            if self._stats_container:
                for w in self._stats_container.winfo_children(): w.destroy()
                msg_stats = "لا توجد نتائج" if term else "لا توجد أصناف"
                ctk.CTkLabel(self._stats_container, text=msg_stats, font=(FONT, 14), text_color=self.C["text2"]).pack()
            return


        # Always use 3 columns to keep card size consistent even if only 1 exists
        cols = 3
        
        for i, prod in enumerate(rows):
            if i % cols == 0:
                row_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
                row_frame.pack(fill="x", pady=4, padx=10)
                # Force all 3 columns to have equal width and UNIFORM behavior
                for c in range(cols):
                    row_frame.columnconfigure(c, weight=1, uniform="group1")

            card = self._make_card(row_frame, prod)
            # Position the card from right to left (Column 2, then 1, then 0)
            # sticky="nsew" ensures they fill the column and match height
            card.grid(row=0, column=(cols - 1 - (i % cols)), padx=8, pady=8, sticky="nsew")

        # Update stats with multi-label RTL fix
        for w in self._stats_container.winfo_children(): w.destroy()
        
        total_stock = sum(db.get_product_stock(r["id"]) for r in rows)
        
        # عدد الأصناف
        ctk.CTkLabel(self._stats_container, text="عدد الأصناف", font=(FONT, 14), text_color=self.C["text2"]).pack(side="right")
        ctk.CTkLabel(self._stats_container, text=" : ", font=(FONT, 14), text_color=self.C["text2"]).pack(side="right")
        ctk.CTkLabel(self._stats_container, text=f"{len(rows)}", font=(FONT, 14, "bold"), text_color=self.C["accent"]).pack(side="right")
        
        ctk.CTkLabel(self._stats_container, text="  |  ", font=(FONT, 14), text_color=self.C["border"]).pack(side="right")
        
        # إجمالي المخزون
        ctk.CTkLabel(self._stats_container, text="إجمالي المخزون", font=(FONT, 14), text_color=self.C["text2"]).pack(side="right")
        ctk.CTkLabel(self._stats_container, text=" : ", font=(FONT, 14), text_color=self.C["text2"]).pack(side="right")
        ctk.CTkLabel(self._stats_container, text=f"{total_stock:,}", font=(FONT, 14, "bold"), text_color=self.C["accent"]).pack(side="right")


    def _make_card(self, parent, prod):
        stock = db.get_product_stock(prod["id"])
        is_low = stock <= prod["min_stock"] and prod["min_stock"] > 0

        # Card base - Dynamic height, but fills the grid cell
        card = ctk.CTkFrame(parent, fg_color=self.C["card"], corner_radius=20,
                            border_width=1.5 if is_low else 1,
                            border_color=self.C["danger"] if is_low else self.C["border"])
        # No fixed height, no pack_propagate(False)

        # Top Image Section
        img_container = ctk.CTkFrame(card, fg_color=self.C["bg"], corner_radius=15, height=120)
        img_container.pack(fill="x", padx=10, pady=10)
        img_container.pack_propagate(False)

        try:
            img = _get_product_image(prod, size=(90, 90))
            img_lbl = ctk.CTkLabel(img_container, text="", image=img)
            img_lbl.image = img
            img_lbl.place(relx=0.5, rely=0.5, anchor="center")
        except:
            ctk.CTkLabel(img_container, text="📷", font=(FONT, 30),
                         text_color=self.C["muted"]).place(relx=0.5, rely=0.5, anchor="center")

        # Info Section
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=12, pady=(0, 10))

        # Category Badge (Small)
        if prod["category"]:
            cat_frame = ctk.CTkFrame(info_frame, fg_color=self.C["accent"], corner_radius=6, height=18)
            cat_frame.pack(side="top", anchor="e", pady=(0, 4))
            ctk.CTkLabel(cat_frame, text=prod["category"], font=(FONT, 9, "bold"), 
                         text_color=self.C["btn_text"], height=18).pack(padx=6)

        # Name
        ctk.CTkLabel(info_frame, text=prod["name"],
                     font=(FONT, 15, "bold"),
                     text_color=self.C["text"], anchor="e").pack(fill="x")

        # Price & Stock Row
        ps_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        ps_row.pack(fill="x", pady=4)

        # Price
        ctk.CTkLabel(ps_row, text=f"\u200E{prod['sell_price']:,.2f} ₪",
                     font=(FONT_HDR, 18, "bold"),
                     text_color=self.C["accent"]).pack(side="right")

        # Stock (on the LEFT) - RTL Fix by splitting
        stock_color = self.C["danger"] if is_low else self.C["success"]
        stock_f = ctk.CTkFrame(ps_row, fg_color="transparent")
        stock_f.pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(stock_f, text="المخزون", font=(FONT, 12), text_color=stock_color).pack(side="right")
        ctk.CTkLabel(stock_f, text=" : ", font=(FONT, 12, "bold"), text_color=stock_color).pack(side="right")
        ctk.CTkLabel(stock_f, text=f"{stock}", font=(FONT, 12, "bold"), text_color=stock_color).pack(side="right")


        # Separator
        ctk.CTkFrame(card, fg_color=self.C["border"], height=1).pack(fill="x", padx=15)

        # Action buttons - Compact in one row
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", padx=15, pady=15)

        ctk.CTkButton(btn_frame, text="", width=38, height=38,
                      image=self._del_icon,
                      fg_color=self.C["danger_bg"], hover_color=self.C["danger_hover"],
                      text_color=self.C["danger"], corner_radius=10,
                      command=lambda p=prod: self._delete(p)).pack(side="left")

        ctk.CTkButton(btn_frame, text="", width=38, height=38,
                      image=self._edit_icon,
                      fg_color=self.C["input"], hover_color=self.C["hover"],
                      text_color=self.C["text"], corner_radius=10,
                      command=lambda p=prod: self._open_edit(p)).pack(side="left", padx=5)

        # Supply (Main button - Takes remaining space)
        ctk.CTkButton(btn_frame, text="توريد سريع", height=38,
                      image=self._box_icon, compound="right",
                      fg_color=self.C["blue"], hover_color="#2563EB",
                      text_color=self.C["btn_text"], corner_radius=10, font=(FONT, 12, "bold"),
                      command=lambda p=prod: self._open_supply(p)).pack(side="right", fill="x", expand=True)

        return card

    def _open_add(self):
        _ProductDialog(self, self.C, on_save=self.refresh)

    def _open_edit(self, prod):
        _ProductDialog(self, self.C, product=prod, on_save=self.refresh)
        
    def _open_supply(self, prod):
        _QuickSupplyDialog(self, self.C, product=prod, on_save=self.refresh)

    def _delete(self, prod):
        from tkinter import messagebox
        
        if messagebox.askyesno("تأكيد الحذف النهائي", f"هل أنت متأكد من حذف الصنف '{prod['name']}' نهائياً؟\nسيتم حذف جميع سجلات التوريد والمبيعات المرتبطة به!"):
            try:
                # حذف الصورة أولاً إذا وجدت
                img_path = os.path.join(IMG_DIR, f"{prod['id']}.png")
                if os.path.exists(img_path):
                    try: os.remove(img_path)
                    except: pass
                
                # محاولة الحذف من قاعدة البيانات
                db.delete_product(prod["id"])
                self.refresh()
                messagebox.showinfo("تم", f"تم حذف الصنف '{prod['name']}' بنجاح.")
                
            except Exception as e:
                # إذا فشل الحذف بسبب وجود مبيعات أو توريد (Foreign Key Constraint)
                messagebox.showerror("فشل الحذف", 
                    f"لا يمكن حذف الصنف '{prod['name']}' لأنه مرتبط بسجلات مبيعات أو توريد في النظام.\n\n"
                    "يجب حذف السجلات المرتبطة به أولاً إذا كنت ترغب في إزالته تماماً.")


# ═══════════════════════════════════════════════════════════════════════════════
#  نافذة إضافة / تعديل صنف
# ═══════════════════════════════════════════════════════════════════════════════
class _ProductDialog(ctk.CTkToplevel):
    def __init__(self, parent, colors, product=None, on_save=None):
        super().__init__(parent)
        self.C = colors
        self._product = product
        self._on_save = on_save
        self._img_path = None

        title = "تعديل الصنف" if product else "إضافة صنف جديد"
        self.title(title)
        self.geometry("480x620")
        self.resizable(False, False)
        self.configure(fg_color=self.C["bg"])
        self.grab_set()

        # 🖥️ Unified Center Positioning
        self.update_idletasks()
        try:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            # Dimensions for Product Dialog
            dw, dh = 480, 620
            px = (sw - dw) // 2
            py = (sh - dh) // 2
            self.geometry(f"{dw}x{dh}+{px}+{py}")
        except: pass

        self._build()
        if product:
            self._populate(product)

    def _build(self):
        # 🟢 Main Container (No scrollbar if not needed)
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=25, pady=20)

        # 🖼️ Image Picker (Compact)
        ctk.CTkLabel(main, text="صورة الصنف", font=(FONT, 12), text_color=self.C["text2"], anchor="e").pack(fill="x")
        img_card = ctk.CTkFrame(main, fg_color=self.C["card"], corner_radius=15, height=120, border_width=1, border_color=self.C["border"])
        img_card.pack(fill="x", pady=(5, 15))
        img_card.pack_propagate(False)

        self._img_label = ctk.CTkLabel(img_card, text="📸 اضغط هنا", font=(FONT, 12), text_color=self.C["muted"], cursor="hand2")
        self._img_label.pack(expand=True, fill="both")
        self._img_label.bind("<Button-1>", lambda e: self._pick_image())

        # Form Fields
        self._cost_var = ctk.StringVar(value="0")
        self._sell_var = ctk.StringVar(value="0")

        def field(parent, label, ph="", var=None):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=label, font=(FONT, 13, "bold"), text_color=self.C["text"], anchor="e").pack(fill="x")
            e = ctk.CTkEntry(f, placeholder_text=ph, textvariable=var, font=(FONT, 14), height=40,
                              fg_color=self.C["input"], border_color=self.C["border"],
                              text_color=self.C["text"], corner_radius=10, justify="right")
            e.pack(fill="x", pady=(2, 0))
            return e

        self._name = field(main, "اسم الصنف *", "ادخل اسم المنتج")
        
        # Prices Row
        price_row = ctk.CTkFrame(main, fg_color="transparent")
        price_row.pack(fill="x", pady=5)
        
        c_f = ctk.CTkFrame(price_row, fg_color="transparent")
        c_f.pack(side="right", expand=True, fill="x", padx=(10, 0))
        ctk.CTkLabel(c_f, text="سعر التكلفة", font=(FONT, 12), text_color=self.C["text2"], anchor="e").pack(fill="x")
        self._cost = ctk.CTkEntry(c_f, textvariable=self._cost_var, font=(FONT, 15, "bold"), height=40,
                                  fg_color=self.C["input"], border_width=0,
                                  text_color=self.C["text"], corner_radius=10, justify="center")
        self._cost.pack(fill="x")

        s_f = ctk.CTkFrame(price_row, fg_color="transparent")
        s_f.pack(side="right", expand=True, fill="x")
        ctk.CTkLabel(s_f, text="سعر البيع", font=(FONT, 12), text_color=self.C["accent"], anchor="e").pack(fill="x")
        self._sell = ctk.CTkEntry(s_f, textvariable=self._sell_var, font=(FONT, 15, "bold"), height=40,
                                  fg_color=self.C["input"], border_width=0,
                                  text_color=self.C["text"], corner_radius=10, justify="center")
        self._sell.pack(fill="x")

        # 💰 Profit Display
        profit_card = ctk.CTkFrame(main, fg_color=self.C["sidebar"], corner_radius=10, height=45)
        profit_card.pack(fill="x", pady=10)
        profit_card.pack_propagate(False)
        
        inner_profit = ctk.CTkFrame(profit_card, fg_color="transparent")
        inner_profit.place(relx=0.5, rely=0.5, anchor="center")
        
        self._profit_text_lbl = ctk.CTkLabel(inner_profit, text=": المربح المتوقع", font=(FONT, 15, "bold"), text_color=self.C["success"])
        self._profit_text_lbl.pack(side="right", padx=5)

        self._profit_val_lbl = ctk.CTkLabel(inner_profit, text="\u200E0.00 ₪", font=("Segoe UI", 16, "bold"), text_color=self.C["success"])
        self._profit_val_lbl.pack(side="right")

        # Description
        ctk.CTkLabel(main, text="الوصف / ملاحظات", font=(FONT, 12), text_color=self.C["text2"], anchor="e").pack(fill="x")
        self._desc = ctk.CTkTextbox(main, font=(FONT, 12), height=60, fg_color=self.C["input"], border_color=self.C["border"],
                                     text_color=self.C["text"], corner_radius=10, border_width=1)
        self._desc.pack(fill="x", pady=(2, 15))

        # Bottom Buttons Row (Side-by-side)
        btn_row = ctk.CTkFrame(main, fg_color="transparent")
        btn_row.pack(fill="x", pady=(5, 0))

        ctk.CTkButton(btn_row, text="إلغاء", font=(FONT, 14), 
                      fg_color=self.C["danger"], text_color=self.C["btn_text"],
                      hover_color="#B91C1C", corner_radius=12, height=45, command=self.destroy).pack(side="left", padx=5, fill="x", expand=True)
                      
        ctk.CTkButton(btn_row, text="حفظ الصنف", font=(FONT, 15, "bold"), image=get_icon("save", (20,20)), compound="right",
                      fg_color=self.C["accent"], text_color=self.C["btn_text"], hover_color="#00BFA0", corner_radius=12,
                      height=45, command=self._save).pack(side="left", padx=5, fill="x", expand=True)

        # Listen to changes
        self._cost_var.trace_add("write", lambda *a: self._calc_profit())
        self._sell_var.trace_add("write", lambda *a: self._calc_profit())

    def _calc_profit(self):
        try:
            cost = float(self._cost_var.get() or 0)
            sell = float(self._sell_var.get() or 0)
            profit = sell - cost
            color = self.C["success"] if profit >= 0 else self.C["danger"]
            # \u200E is the Left-to-Right Mark, forcing digits to render in English format
            self._profit_val_lbl.configure(text=f"\u200E{profit:,.2f} ₪", text_color=color)
            self._profit_text_lbl.configure(text_color=color)
        except:
            self._profit_val_lbl.configure(text="خطأ", text_color=self.C["danger"])
            self._profit_text_lbl.configure(text_color=self.C["danger"])

    def _pick_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("صور", "*.png *.jpg *.jpeg *.bmp *.gif *.webp")])
        if path:
            self._img_path = path
            self._show_preview(path)

    def _show_preview(self, path):
        try:
            img = Image.open(path).resize((130, 130), Image.LANCZOS)
            photo = ctk.CTkImage(img, size=(130, 130))
            self._img_label.configure(image=photo, text="")
            self._img_label.image = photo
        except:
            pass

    def _populate(self, p):
        # Clear then insert to avoid appending
        self._name.delete(0, "end")
        self._name.insert(0, p["name"])
        
        # Category and unit are removed from UI, but keep in DB logic if needed
        # For now, just handle the variables we actually have in the UI
        self._cost_var.set(str(p["cost_price"]))
        self._sell_var.set(str(p["sell_price"]))
        
        self._desc.delete("1.0", "end")
        self._desc.insert("1.0", p["description"] or "")
        self._calc_profit()

    def _save(self):
        name = self._name.get().strip()
        if not name:
            self._name.configure(border_color=self.C["danger"])
            return

        try:
            cost   = float(self._cost_var.get() or 0)
            sell   = float(self._sell_var.get() or 0)
        except: return

        desc = self._desc.get("1.0", "end").strip()

        if self._product:
            pid = self._product["id"]
            db.update_product(pid, name, "", desc, "قطعة", cost, sell, 0)
        else:
            code = db.add_product(name, "", desc, "قطعة", cost, sell, 0)
            # Get the new product ID
            products = db.get_all_products()
            pid = max(p["id"] for p in products)

        # Save image
        if self._img_path and self._img_path != os.path.join(IMG_DIR, f"{pid}.png"):
            dest = os.path.join(IMG_DIR, f"{pid}.png")
            try:
                img = Image.open(self._img_path)
                img = img.resize((300, 300), Image.LANCZOS)
                img.save(dest, "PNG")
            except:
                if os.path.exists(self._img_path):
                    shutil.copy2(self._img_path, dest)

        if self._on_save:
            self._on_save()
        self.destroy()

from datetime import date

class _QuickSupplyDialog(ctk.CTkToplevel):
    def __init__(self, parent, colors, product, on_save=None):
        super().__init__(parent)
        self.C = colors
        self._product = product
        self._on_save = on_save
        self.title("توريد سريع")
        self.geometry("460x580")
        self.resizable(False, False)
        self.configure(fg_color=self.C["bg"])
        self.grab_set()

        # 🖥️ Unified Center Positioning
        self.update_idletasks()
        try:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            # Dimensions for Quick Supply (keeping it similar to Add Product for consistency)
            dw, dh = 480, 620
            px = (sw - dw) // 2
            py = (sh - dh) // 2
            self.geometry(f"{dw}x{dh}+{px}+{py}")
        except: pass

        self._build()

    def _build(self):
        # 🟢 Main Container with better padding
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=25)

        # 🏷️ Header
        hdr = ctk.CTkFrame(main, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 20))
        
        icon_lbl = ctk.CTkLabel(hdr, text="📦", font=("Segoe UI", 28))
        icon_lbl.pack(side="right", padx=(10, 0))
        
        txt_f = ctk.CTkFrame(hdr, fg_color="transparent")
        txt_f.pack(side="right")
        
        ctk.CTkLabel(txt_f, text="توريد سريع للمخزن", font=(FONT_HDR, 18, "bold"), 
                     text_color=self.C["accent"], anchor="e").pack(fill="x")
        ctk.CTkLabel(txt_f, text=self._product['name'], font=(FONT_REG, 13), 
                     text_color=self.C["text2"], anchor="e").pack(fill="x")

        # 📝 Form
        self._qty_var = ctk.StringVar()
        self._cost_var = ctk.StringVar(value=str(self._product["cost_price"]))

        def premium_field(label, ph="", var=None):
            lbl = ctk.CTkLabel(main, text=label, font=(FONT_REG, 12, "bold"), text_color=self.C["text"], anchor="e")
            lbl.pack(fill="x", pady=(10, 2))
            
            e = ctk.CTkEntry(main, placeholder_text=ph, textvariable=var, font=(FONT_REG, 14), height=42,
                              fg_color=self.C["input"], border_width=1, border_color=self.C["border"],
                              text_color=self.C["text"], corner_radius=12, justify="right")
            e.pack(fill="x")
            return e

        self._qty = premium_field("الكمية المطلوبة *", "مثال: 50", self._qty_var)
        self._cost = premium_field("سعر الشراء (للوحدة)", "0.00", self._cost_var)
        
        # حسابات ديناميكية (Slim Design)
        calc_frame = ctk.CTkFrame(main, fg_color="transparent")
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
        self._lbl_total_sale = badge(calc_frame, "قيمة البيع", "0.00 ₪", "#2563EB", "#1E40AF")
        self._lbl_total_profit = badge(calc_frame, "الربح", "0.00 ₪", "#16A34A", "#166534")

        self._qty_var.trace_add("write", self._calc)
        self._cost_var.trace_add("write", self._calc)

        self._date_e = premium_field("تاريخ العملية", "YYYY-MM-DD")
        self._date_e.insert(0, date.today().isoformat())

        # 🔘 Action Buttons
        btn_row = ctk.CTkFrame(main, fg_color="transparent")
        btn_row.pack(fill="x", pady=(30, 0))

        # Save Button (Left/Primary)
        ctk.CTkButton(btn_row, text="إتمام التوريد", font=(FONT_REG, 15, "bold"),
                      fg_color=self.C["accent"], text_color=self.C["btn_text"], hover_color="#00BFA0",
                      corner_radius=15, height=48, command=self._save).pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Cancel Button (Right/Secondary)
        ctk.CTkButton(btn_row, text="إلغاء", font=(FONT_REG, 14),
                      fg_color="#F1F5F9", text_color="#64748B", hover_color="#E2E8F0",
                      corner_radius=15, height=48, command=self.destroy).pack(side="left", fill="x", expand=True, padx=(5, 0))

    def _calc(self, *args):
        try:
            qty = float(self._qty_var.get() or 0)
            cost = float(self._cost_var.get() or 0)
            sell = float(self._product["sell_price"] or 0)
            
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

    def _save(self):
        try:
            qty = int(self._qty_var.get() or 0)
            if qty <= 0: return
        except: return
        
        try:
            cost = float(self._cost_var.get() or 0)
        except:
            cost = 0.0

        s_date = self._date_e.get().strip() or date.today().isoformat()
        db.add_supply(self._product["id"], qty, cost, "", "توريد سريع من الأصناف", s_date)
        if self._on_save: self._on_save()
        self.destroy()

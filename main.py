"""
نظام إدارة متجر الملابس – CustomTkinter
الملف الرئيسي
"""
import customtkinter as ctk
from datetime import datetime, date
import os, sys
import ctypes
from datetime import datetime, date
import database as db

# ─── تسجيل الخطوط المخصصة ──────────────────────────────────────────────────
def load_custom_fonts():
    fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
    if os.path.exists(fonts_dir):
        # البحث في المجلد الرئيسي والمجلدات الفرعية
        for root, dirs, files in os.walk(fonts_dir):
            for font_file in files:
                if font_file.endswith(".ttf") or font_file.endswith(".otf"):
                    font_path = os.path.join(root, font_file)
                    # تسجيل الخط في ويندوز
                    if sys.platform == "win32":
                        FR_PRIVATE = 0x10
                        FR_NOT_ENUM = 0x20
                        ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)

load_custom_fonts()

# ─── الإعدادات العامة ──────────────────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ألوان مخصصة - نظام متكامل يدعم Light و Dark تلقائياً
C = {
    "bg":       ("#F3F4F6", "#0F172A"),
    "card":     ("#FFFFFF", "#1E293B"),
    "sidebar":  ("#FFFFFF", "#1E293B"),
    "accent":   ("#0D9488", "#2DD4BF"),
    "accent2":  ("#F59E0B", "#FBBF24"),
    "blue":     ("#3B82F6", "#60A5FA"),
    "success":  ("#10B981", "#34D399"),
    "danger":   ("#EF4444", "#F87171"),
    "warning":  ("#F59E0B", "#FBBF24"),
    "text":     ("#1F2937", "#F8FAFC"),
    "btn_text": ("#FFFFFF", "#0F172A"),
    "text2":    ("#4B5563", "#CBD5E1"),
    "muted":    ("#9CA3AF", "#64748B"),
    "border":   ("#E5E7EB", "#334155"),
    "input":    ("#F9FAFB", "#0F172A"),
    "hover":    ("#F3F4F6", "#334155"),
    "danger_bg":    ("#FEE2E2", "#311111"), 
    "danger_hover": ("#FECACA", "#4C1D1D"),
    "danger_f":     ("#FEE2E2", "#311111"), # تم إضافته ليتوافق مع بقية الألوان _f
    "accent_f":     ("#E0F2F1", "#0D2E2B"),
    "blue_f":       ("#E3F2FD", "#0D1E2E"),
    "success_f":    ("#E8F5E9", "#11261A"),
    "warning_f":    ("#FFF3E0", "#2E2111"),
}

FONT       = "Cairo"
FONT_FALLBACK = "Tahoma"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR  = os.path.join(BASE_DIR, "product_images")
ICON_DIR = os.path.join(BASE_DIR, "icons")
os.makedirs(IMG_DIR, exist_ok=True)

def get_icon(name, size=(24, 24)):
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

# ─── الخطوط ──────────────────────────────────────────────────
FONT_HDR = "Thmanyah Sans"
FONT_REG = "Cairo"
FONT = FONT_REG

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        db.init_db()

        self.title("إدارة متجر الملابس")
        self.geometry("1200x720")
        self.minsize(1000, 650)
        self.configure(fg_color=C["bg"])

        # تشغيل البرنامج في وضع التكبير (Maximized) مباشرة
        self.after(0, lambda: self.state("zoomed"))

        self._pages = {}
        self._active_btn = None
        self._nav_buttons = []

        self._build_layout()
        self._show_page("products")
        self._update_clock()
        self._refresh_net()

    def _build_layout(self):
        # ═══ Top Bar ═══
        topbar = ctk.CTkFrame(self, fg_color=C["card"], height=85, corner_radius=0, # زدنا الطول شوية
                              border_width=1, border_color=C["border"])
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        # Right: Logo
        logo = ctk.CTkFrame(topbar, fg_color="transparent")
        logo.pack(side="right", padx=24)
        ctk.CTkLabel(logo, text="إدارة متــــجر الملابــــس  👔",
                     font=(FONT_HDR, 26, "bold"), text_color=C["accent"]).pack(side="right")

        # Left: Styled Info Cards
        left_info = ctk.CTkFrame(topbar, fg_color="transparent")
        left_info.pack(side="left", padx=24)

        # 📅 Clock Card
        clock_card = ctk.CTkFrame(left_info, fg_color=C["sidebar"], corner_radius=12, 
                                  border_width=1, border_color=C["border"])
        clock_card.pack(side="left", padx=12, pady=5)
        
        self._time_lbl = ctk.CTkLabel(clock_card, text="", font=(FONT, 20, "bold"), text_color=C["accent"])
        self._time_lbl.pack(padx=25, pady=(6, 0))
        
        self._date_lbl = ctk.CTkLabel(clock_card, text="", font=(FONT, 12), text_color=C["text2"])
        self._date_lbl.pack(padx=25, pady=(0, 6))

        # (Mode button moved to sidebar)
        self._sun_icon = get_icon("sun", (24, 24))
        self._moon_icon = get_icon("moon", (24, 24))

        # 🏦 Net Daily Card (Styled like clock)
        net_card = ctk.CTkFrame(left_info, fg_color=C["sidebar"], corner_radius=12, 
                                border_width=1, border_color=C["border"])
        net_card.pack(side="left", padx=12, pady=5)
        
        self._net_val_lbl = ctk.CTkLabel(net_card, text="", font=(FONT, 20, "bold"))
        self._net_val_lbl.pack(padx=25, pady=(6, 0))
        
        ctk.CTkLabel(net_card, text="صندوق اليوم 🏦", font=(FONT, 12), 
                     text_color=C["text2"]).pack(padx=25, pady=(0, 6))

        # ═══ Main container ═══
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True)

        # ═══ Sidebar – RIGHT ═══
        sidebar = ctk.CTkFrame(main_container, fg_color=C["sidebar"], width=230,
                               corner_radius=0, border_width=1, border_color=C["border"])
        sidebar.pack(side="right", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="القائمة الرئيسية",
                     font=(FONT_HDR, 12, "bold"), text_color=C["muted"],
                     anchor="e").pack(fill="x", padx=20, pady=(15, 5))

        nav = [
            ("products",  get_icon("products"), "الأصناف"),
            ("supply",    get_icon("supply"),   "التوريد"),
            ("sales",     get_icon("sales"),    "المبيعات"),
            ("cashbox",   get_icon("cashbox"),  "الصندوق"),
            ("expenses",  get_icon("expenses"), "المصروفات"),
            ("debts",     get_icon("debts"),    "الديون"),
            ("inventory", get_icon("inventory"),"الجرد"),
        ]

        self._nav_widgets = {} # Store widgets by key

        for key, icon, label in nav:
            # Container frame for the menu item
            item_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=40, corner_radius=8, cursor="hand2")
            item_frame.pack(fill="x", padx=10, pady=2)
            item_frame.pack_propagate(False)
            item_frame._key = key

            # Icon (Fixed width container to ensure alignment)
            icon_lbl = ctk.CTkLabel(item_frame, text="", image=icon, width=45)
            icon_lbl.pack(side="right", padx=(0, 10))

            # Label (Starts from a fixed point)
            text_lbl = ctk.CTkLabel(item_frame, text=label, font=(FONT_REG, 15), text_color=C["text"])
            text_lbl.pack(side="right", padx=(0, 0))

            # Bindings for hover and click
            def on_enter(e, f=item_frame, t=text_lbl, i=icon_lbl, k=key):
                if self._active_btn != f:
                    f.configure(fg_color=C["accent"])
                    t.configure(text_color=C["btn_text"])
                    i.configure(text_color=C["btn_text"])
            
            def on_leave(e, f=item_frame, t=text_lbl, i=icon_lbl, k=key):
                if self._active_btn != f:
                    f.configure(fg_color="transparent")
                    t.configure(text_color=C["text"])
                    i.configure(text_color=C["text"])

            def on_click(e, k=key):
                self._show_page(k)

            # Bind to all components
            for w in [item_frame, icon_lbl, text_lbl]:
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
                w.bind("<Button-1>", on_click)

            self._nav_widgets[key] = {
                "frame": item_frame,
                "text":  text_lbl,
                "icon":  icon_lbl
            }
            self._nav_buttons.append(item_frame)

        # 🛠️ Factory Reset Function
        def factory_reset():
            from tkinter import messagebox
            if not messagebox.askyesno("تحذير", "أنت على وشك حذف جميع بيانات النظام!\nهل أنت متأكد؟"):
                return
            if not messagebox.askyesno("تأكيد أخير", "هل أنت متأكد تماماً؟"):
                return
            if db.reset_all_data():
                self._pages = {}
                self._show_page("products")
                messagebox.showinfo("نجاح", "تم تصفير البيانات.")
            else:
                messagebox.showerror("خطأ", "فشلت العملية.")

        # Version (at the very bottom)
        ctk.CTkLabel(sidebar, text="الإصدار 1.0", font=(FONT, 10),
                     text_color=C["muted"]).pack(side="bottom", pady=10)

        # ═══ Sidebar Footer (Reset & Theme) ═══
        footer = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=10, pady=(5, 0))

        # Hint Label (appears on hover)
        self._hint_lbl = ctk.CTkLabel(footer, text="", font=(FONT, 11, "bold"), text_color=C["muted"])
        self._hint_lbl.pack(side="top", pady=(5, 0))

        btns_row = ctk.CTkFrame(footer, fg_color="transparent")
        btns_row.pack(side="top", pady=5)

        def on_btn_enter(hint_text):
            self._hint_lbl.configure(text=hint_text)
        
        def on_btn_leave():
            self._hint_lbl.configure(text="")

        # Factory Reset Button (Icon only)
        self._reset_btn = ctk.CTkButton(btns_row, text="", image=get_icon("delete", (20, 20)),
                                        width=45, height=45, fg_color=C["sidebar"],
                                        border_width=1, border_color=C["border"],
                                        hover_color="#7F1D1D", corner_radius=12,
                                        command=factory_reset)
        self._reset_btn.pack(side="right", padx=5)
        self._reset_btn.bind("<Enter>", lambda e: on_btn_enter("ضبط المصنع"))
        self._reset_btn.bind("<Leave>", lambda e: on_btn_leave())

        # Theme Toggle Button (Icon only)
        self._mode_btn = ctk.CTkButton(btns_row, text="", image=self._moon_icon,
                                       width=45, height=45, fg_color=C["sidebar"],
                                       border_width=1, border_color=C["border"],
                                       hover_color=C["accent"], corner_radius=12,
                                       command=self._toggle_mode)
        self._mode_btn.pack(side="right", padx=5)
        self._mode_btn.bind("<Enter>", lambda e: on_btn_enter("تبديل الوضع"))
        self._mode_btn.bind("<Leave>", lambda e: on_btn_leave())
        
        self._update_mode_icon()

        # ═══ Content area ═══
        self._content = ctk.CTkFrame(main_container, fg_color=C["bg"], corner_radius=0)
        self._content.pack(side="left", fill="both", expand=True)

        # Page classes (lazy import)
        from page_products  import ProductsPage
        from page_supply    import SupplyPage
        from page_sales     import SalesPage
        from page_expenses  import ExpensesPage
        from page_debts     import DebtsPage
        from page_cashbox   import CashboxPage
        from page_inventory import InventoryPage

        self._page_classes = {
            "products":  ProductsPage,
            "supply":    SupplyPage,
            "sales":     SalesPage,
            "cashbox":   CashboxPage,
            "expenses":  ExpensesPage,
            "debts":     DebtsPage,
            "inventory": InventoryPage,
        }

    def _show_page(self, key):
        # Reset all sidebar widgets
        for k, widgets in self._nav_widgets.items():
            widgets["frame"].configure(fg_color="transparent")
            widgets["text"].configure(text_color=C["text"])
            widgets["icon"].configure(text_color=C["text"])

        # Highlight the active one
        if key in self._nav_widgets:
            w = self._nav_widgets[key]
            w["frame"].configure(fg_color=C["accent"])
            w["text"].configure(text_color=C["btn_text"])
            w["icon"].configure(text_color=C["btn_text"])
            self._active_btn = w["frame"]

        # Hide current pages
        for w in self._content.winfo_children():
            w.pack_forget()

        # Create/Show page
        if key not in self._pages:
            cls = self._page_classes[key]
            self._pages[key] = cls(self._content, C)

        page = self._pages[key]
        if hasattr(page, "refresh"):
            page.refresh()
        page.pack(fill="both", expand=True)

    def _update_clock(self):
        now = datetime.now()
        days = {"Monday":"الإثنين","Tuesday":"الثلاثاء","Wednesday":"الأربعاء",
                "Thursday":"الخميس","Friday":"الجمعة","Saturday":"السبت","Sunday":"الأحد"}
        d_name = days.get(now.strftime("%A"), "")
        
        # وقت بصيغة 12 ساعة مع AM/PM بالعربي (ص/م على اليسار مع الحفاظ على أرقام 0-9)
        suffix = "ص" if now.strftime("%p") == "AM" else "م"
        time_part = now.strftime('%I:%M')
        t_str = f"{suffix} \u200E{time_part}"
        self._time_lbl.configure(text=t_str)
        self._date_lbl.configure(text=f"{d_name}  \u200E{now.strftime('%d/%m/%Y')}")
        
        self.after(10000, self._update_clock)

    def _refresh_net(self):
        today = date.today().isoformat()
        s = db.get_cashbox_summary(today, today)
        n = s["net"]
        sign = "+" if n >= 0 else ""
        color = C["success"] if n >= 0 else C["danger"]
        self._net_val_lbl.configure(text=f"\u200E{sign}{n:,.2f} ₪", text_color=color)
        self.after(30000, self._refresh_net)

    def _toggle_mode(self):
        current_mode = ctk.get_appearance_mode()
        new_mode = "Dark" if current_mode == "Light" else "Light"
        ctk.set_appearance_mode(new_mode)
        self._update_mode_icon()

    def _update_mode_icon(self):
        mode = ctk.get_appearance_mode()
        if hasattr(self, "_mode_btn"):
            icon = self._sun_icon if mode == "Dark" else self._moon_icon
            self._mode_btn.configure(image=icon)


if __name__ == "__main__":
    app = App()
    app.mainloop()

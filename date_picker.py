"""
نسخة طبق الأصل 100% من تقويم 'نافذة التوريد'
"""

import customtkinter as ctk
from datetime import date
import calendar

FONT_REG = "Cairo"

def show_date_picker(parent, entry, C, callback=None):
    import calendar
    from datetime import date
    
    top = ctk.CTkToplevel(parent)
    top.title("اختر التاريخ")
    top.geometry("320x360")
    top.configure(fg_color=C["bg"])
    top.attributes("-topmost", True)
    top.grab_set()
    
    try:
        sw = parent.winfo_screenwidth(); sh = parent.winfo_screenheight()
        top.geometry(f"+{(sw-320)//2}+{(sh-360)//2}")
    except: pass
    
    today = date.today()
    curr_yr = [today.year]; curr_mo = [today.month]; view_mode = ["days"]
    ar_months = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", 
                 "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
    
    hdr = ctk.CTkFrame(top, fg_color="transparent")
    hdr.pack(fill="x", padx=10, pady=10)
    
    mo_btn = ctk.CTkButton(hdr, text="", font=(FONT_REG, 15, "bold"), text_color=C["text"],
                           fg_color=C["card"], border_width=1, border_color=C["border"],
                           hover_color=C["hover"], corner_radius=8, height=35, command=lambda: toggle_view())
    mo_btn.pack(side="right", expand=True)
    
    main_fr = ctk.CTkFrame(top, fg_color="transparent")
    main_fr.pack(fill="both", expand=True, padx=10, pady=5)
    
    def pick(d):
        entry.delete(0, "end"); entry.insert(0, f"{curr_yr[0]}-{curr_mo[0]:02d}-{d:02d}"); top.destroy()
        if callback: callback()

    def toggle_view(): view_mode[0] = "months" if view_mode[0] == "days" else "days"; render()
    def pick_month(m): curr_mo[0] = m; view_mode[0] = "days"; render()

    def render():
        for w in main_fr.winfo_children(): w.destroy()
        if view_mode[0] == "days":
            mo_btn.configure(text=f"{ar_months[curr_mo[0]-1]} {curr_yr[0]}")
            days = ["أحد","إثنين","ثلاثاء","أربعاء","خميس","جمعة","سبت"]
            for c, d in enumerate(days):
                ctk.CTkLabel(main_fr, text=d, font=(FONT_REG, 11, "bold"), text_color=C["text2"]).grid(row=0, column=6-c, padx=4, pady=5)
            
            cal = calendar.Calendar(firstweekday=6)
            for r, week in enumerate(cal.monthdayscalendar(curr_yr[0], curr_mo[0])):
                for c, day in enumerate(week):
                    if day != 0:
                        is_today = (curr_yr[0] == today.year and curr_mo[0] == today.month and day == today.day)
                        bg = C["accent"] if is_today else C["card"]; tc = "#FFF" if is_today else C["text"]
                        btn = ctk.CTkButton(main_fr, text=str(day), width=35, height=35, font=(FONT_REG, 13, "bold"),
                                            fg_color=bg, text_color=tc, hover_color=C["hover"], corner_radius=8,
                                            command=lambda d=day: pick(d))
                        btn.grid(row=r+1, column=6-c, padx=3, pady=2)
        else:
            mo_btn.configure(text=f"{curr_yr[0]}")
            for i in range(12):
                r, c = i // 3, i % 3
                is_curr = (curr_yr[0] == today.year and (i+1) == today.month)
                bg = C["accent"] if is_curr else C["card"]; tc = "#FFF" if is_curr else C["text"]
                ctk.CTkButton(main_fr, text=ar_months[i], width=85, height=45, font=(FONT_REG, 14, "bold"),
                                    fg_color=bg, text_color=tc, hover_color=C["hover"], corner_radius=8,
                                    command=lambda m=(i+1): pick_month(m)).grid(row=r, column=2 - c, padx=5, pady=5)
    
    def shift(m):
        if view_mode[0] == "days":
            curr_mo[0] += m
            if curr_mo[0] > 12: curr_mo[0] = 1; curr_yr[0] += 1
            if curr_mo[0] < 1: curr_mo[0] = 12; curr_yr[0] -= 1
        else: curr_yr[0] += m
        render()
            
    ctk.CTkButton(hdr, text="<", width=30, fg_color=C["card"], text_color=C["text"], hover_color=C["hover"], command=lambda: shift(1)).pack(side="left")
    ctk.CTkButton(hdr, text=">", width=30, fg_color=C["card"], text_color=C["text"], hover_color=C["hover"], command=lambda: shift(-1)).pack(side="right")
    
    render()

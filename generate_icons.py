
from PIL import Image, ImageDraw, ImageOps
import os

def create_icons(color_light="#1F2937", color_dark="#F8FAFC", size=(48, 48)):
    os.makedirs("icons", exist_ok=True)
    
    # Simple icons using PIL
    icons = {
        "sun": draw_sun,
        "moon": draw_moon,
        "edit": draw_pencil,
        "delete": draw_trash,
        "supply": draw_box,
        "add": draw_plus,
        "products": draw_tag,
        "sales": draw_cart,
        "cashbox": draw_bank,
        "expenses": draw_money_off,
        "debts": draw_list,
        "inventory": draw_chart,
        "receipt": draw_receipt,
        "numbers": draw_numbers,
        "save": draw_save,
        "calendar": draw_calendar,
    }
    
    for name, func in icons.items():
        # Light version
        img_l = Image.new("RGBA", size, (255, 255, 255, 0))
        func(ImageDraw.Draw(img_l), size, color_light)
        img_l.save(f"icons/{name}_light.png")
        
        # Dark version
        img_d = Image.new("RGBA", size, (255, 255, 255, 0))
        func(ImageDraw.Draw(img_d), size, color_dark)
        img_d.save(f"icons/{name}_dark.png")

def draw_sun(draw, size, color):
    w, h = size
    cx, cy = w//2, h//2
    r = w//4
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=color, width=3)
    for i in range(8):
        import math
        angle = i * (math.pi/4)
        x1 = cx + math.cos(angle) * (r + 4)
        y1 = cy + math.sin(angle) * (r + 4)
        x2 = cx + math.cos(angle) * (r + 10)
        y2 = cy + math.sin(angle) * (r + 10)
        draw.line([x1, y1, x2, y2], fill=color, width=3)

def draw_moon(draw, size, color):
    w, h = size
    cx, cy = w//2, h//2
    draw.ellipse([cx-12, cy-12, cx+12, cy+12], fill=color)
    draw.ellipse([cx-4, cy-12, cx+20, cy+12], fill=(0,0,0,0)) # Punch hole for crescent

def draw_pencil(draw, size, color):
    # Simple pencil shape
    draw.polygon([(10,38), (14,38), (38,14), (34,10)], outline=color, width=2)
    draw.polygon([(10,38), (14,38), (10,34)], fill=color)

def draw_trash(draw, size, color):
    draw.rectangle([12,14,36,38], outline=color, width=2)
    draw.line([10,14,38,14], fill=color, width=2)
    draw.rectangle([20,10,28,14], outline=color, width=2)

def draw_box(draw, size, color):
    draw.rectangle([10,14,38,34], outline=color, width=2)
    draw.line([10,14,24,24,38,14], fill=color, width=2)

def draw_plus(draw, size, color):
    w, h = size
    cx, cy = w//2, h//2
    draw.line([cx-12, cy, cx+12, cy], fill=color, width=4)
    draw.line([cx, cy-12, cx, cy+12], fill=color, width=4)

def draw_tag(draw, size, color):
    draw.polygon([(14,14), (28,14), (38,24), (24,38), (10,24)], outline=color, width=2)
    draw.ellipse([18,18,22,22], fill=color)

def draw_cart(draw, size, color):
    draw.line([10,12,14,12,18,30,34,30,38,18,18,18], fill=color, width=2)
    draw.ellipse([18,34,22,38], fill=color)
    draw.ellipse([30,34,34,38], fill=color)

def draw_bank(draw, size, color):
    draw.polygon([(10,18), (24,10), (38,18)], outline=color, width=2)
    draw.rectangle([12,18,36,34], outline=color, width=2)
    draw.line([18,18,18,34], fill=color, width=2)
    draw.line([30,18,30,34], fill=color, width=2)

def draw_money_off(draw, size, color):
    draw.rectangle([12,16,36,32], outline=color, width=2)
    draw.ellipse([20,20,28,28], outline=color, width=2)
    draw.line([10,10,38,38], fill=color, width=2)

def draw_list(draw, size, color):
    draw.rectangle([12,10,36,38], outline=color, width=2)
    draw.line([16,18,32,18], fill=color, width=2)
    draw.line([16,26,32,26], fill=color, width=2)
    draw.line([16,34,32,34], fill=color, width=2)

def draw_chart(draw, size, color):
    draw.line([10,34,38,34], fill=color, width=2)
    draw.line([10,34,10,10], fill=color, width=2)
    draw.rectangle([14,24,20,34], fill=color)
    draw.rectangle([22,14,28,34], fill=color)
    draw.rectangle([30,18,36,34], fill=color)

def draw_receipt(draw, size, color):
    draw.rectangle([14,10,34,38], outline=color, width=2)
    draw.line([18,18,30,18], fill=color, width=2)
    draw.line([18,26,30,26], fill=color, width=2)
    draw.line([18,34,30,34], fill=color, width=2)

def draw_numbers(draw, size, color):
    # Just simple 123 representation
    draw.text((12,12), "1", fill=color)
    draw.text((22,22), "2", fill=color)
    draw.text((32,12), "3", fill=color)

def draw_save(draw, size, color):
    draw.rectangle([12,12,36,36], outline=color, width=2)
    draw.rectangle([18,12,30,22], outline=color, width=2)
    draw.line([18,28,30,28], fill=color, width=4)

def draw_calendar(draw, size, color):
    draw.rectangle([12,14,36,36], outline=color, width=2)
    draw.line([12,20,36,20], fill=color, width=2)
    draw.line([18,12,18,16], fill=color, width=2)
    draw.line([30,12,30,16], fill=color, width=2)

if __name__ == "__main__":
    create_icons()

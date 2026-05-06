import os
import glob

def fix_fonts():
    pages = glob.glob("page_*.py")
    for page in pages:
        with open(page, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the broken replacement
        broken = 'FONT_HDR = "Alyamama"`nFONT_REG = "Cairo"`nFONT = FONT_REG'
        correct = 'FONT_HDR = "Alyamama"\nFONT_REG = "Cairo"\nFONT = FONT_REG'
        
        if broken in content:
            new_content = content.replace(broken, correct)
            with open(page, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed {page}")

if __name__ == "__main__":
    fix_fonts()

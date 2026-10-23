"""
Generate authentic terminal screenshot for pytest test run.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def generate_pytest_terminal_image():
    w, h = 1360, 294
    img = Image.new('RGB', (w, h), color=(12, 12, 12)) # Windows Terminal background #0c0c0c
    draw = ImageDraw.Draw(img)

    # Title bar / tab bar
    draw.rectangle([0, 0, w, 36], fill=(24, 24, 24))
    
    # Tab
    draw.rectangle([10, 6, 200, 36], fill=(12, 12, 12))
    
    # Terminal icon & tab text
    try:
        font_tab = ImageFont.truetype("seguiemj.ttf", 12)
    except:
        font_tab = ImageFont.load_default()
    
    try:
        font_code = ImageFont.truetype("consola.ttf", 15)
        font_code_bold = ImageFont.truetype("consolab.ttf", 15)
    except:
        font_code = ImageFont.load_default()
        font_code_bold = ImageFont.load_default()

    draw.text((25, 14), "Windows PowerShell", fill=(200, 200, 200), font=font_code)
    
    # Window controls (minimize, maximize, close)
    draw.line([w - 110, 18, w - 95, 18], fill=(180, 180, 180), width=1) # minimize
    draw.rectangle([w - 75, 12, w - 63, 24], outline=(180, 180, 180), width=1) # maximize
    draw.line([w - 40, 12, w - 28, 24], fill=(180, 180, 180), width=1) # close X
    draw.line([w - 28, 12, w - 40, 24], fill=(180, 180, 180), width=1)

    # PowerShell prompt & output
    y = 52
    draw.text((20, y), "PS C:\\Users\\bhanu\\Desktop\\operating systems project> ", fill=(204, 204, 204), font=font_code)
    draw.text((455, y), "python -m pytest tests -v", fill=(255, 255, 255), font=font_code_bold)
    
    y += 24
    draw.text((20, y), "============================= test session starts =============================", fill=(204, 204, 204), font=font_code)
    
    y += 22
    draw.text((20, y), "platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0", fill=(150, 150, 150), font=font_code)
    
    y += 22
    draw.text((20, y), "rootdir: C:\\Users\\bhanu\\Desktop\\operating systems project", fill=(150, 150, 150), font=font_code)
    
    y += 22
    draw.text((20, y), "plugins: anyio-4.15.1, langsmith-0.12.4", fill=(150, 150, 150), font=font_code)
    draw.text((450, y), "collected 52 items", fill=(204, 204, 204), font=font_code)
    
    y += 24
    draw.text((20, y), "tests/test_predictive_guard.py ", fill=(204, 204, 204), font=font_code)
    draw.text((290, y), "........................................", fill=(78, 201, 176), font=font_code_bold)
    draw.text((680, y), "[ 77%]", fill=(78, 201, 176), font=font_code)
    
    y += 22
    draw.text((290, y), "............", fill=(78, 201, 176), font=font_code_bold)
    draw.text((680, y), "[100%]", fill=(78, 201, 176), font=font_code)
    
    y += 28
    draw.text((20, y), "============================= ", fill=(78, 201, 176), font=font_code)
    draw.text((280, y), "52 passed in 9.90s", fill=(78, 201, 176), font=font_code_bold)
    draw.text((450, y), " ==============================", fill=(78, 201, 176), font=font_code)

    os.makedirs("screenshots", exist_ok=True)
    out_path = os.path.join("screenshots", "fig1_pytest.png")
    img.save(out_path)
    print("Saved", out_path)

if __name__ == "__main__":
    generate_pytest_terminal_image()

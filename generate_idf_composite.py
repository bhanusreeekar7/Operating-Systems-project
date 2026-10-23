"""
Create composite architecture and output image for IDF-B Page 2.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_idf_page2_composite():
    w, h = 1536, 1024
    comp = Image.new('RGB', (w, h), color=(255, 255, 255))
    draw = ImageDraw.Draw(comp)

    try:
        font_title = ImageFont.truetype("arialbd.ttf", 22)
        font_sub = ImageFont.truetype("arial.ttf", 16)
        font_box_title = ImageFont.truetype("arialbd.ttf", 14)
        font_box_body = ImageFont.truetype("arial.ttf", 11)
        font_caption = ImageFont.truetype("arialbd.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_box_title = ImageFont.load_default()
        font_box_body = ImageFont.load_default()
        font_caption = ImageFont.load_default()

    # Border around architecture block
    draw.rectangle([30, 15, w - 30, 480], outline=(200, 200, 200), width=1)

    # Header text
    draw.text((w // 2 - 100, 30), "PredictiveGuard", fill=(10, 10, 10), font=font_title)
    draw.text((w // 2 - 135, 58), "AI-Based Predictive Reliability Engine", fill=(80, 80, 80), font=font_sub)
    draw.text((w // 2 - 80, 78), "(System Architecture)", fill=(100, 100, 100), font=font_box_body)

    # 6 pipeline boxes across
    boxes = [
        ("Multi-Source Ingestion", ["• System Logs", "• App Event Logs", "• Network Telemetry", "• Resource Metrics"], (254, 243, 199)), # warm yellow
        ("Parser & Normalizer", ["• Regex Syslog Match", "• JSON Payload Decode", "• Timestamp Standard.", "• Sanitization Filter"], (254, 249, 195)), 
        ("Feature Engineering", ["• Rolling Window Stats", "• Mean / Std / Roc", "• Error Frequencies", "• Critical Keywords"], (224, 242, 254)), # blue
        ("Local DB & Cache", ["• SQLite Persistence", "• Time-Series Metrics", "• Unified Timeline", "• Cooldown Cache"], (243, 232, 255)), # purple
        ("AI / ML Analysis", ["• Isolation Forest", "  Anomaly Detector", "• Random Forest", "  Failure Classifier"], (220, 252, 231)), # green
        ("Autonomous Recovery", ["• Policy Mapping", "• Service Restart", "• Cache Flush & Clean", "• Pre/Post Health Eval"], (255, 228, 230)), # rose
    ]

    box_w = 210
    box_h = 175
    gap = 26
    start_x = 65
    box_y = 120

    for i, (b_title, b_items, bg_col) in enumerate(boxes):
        bx = start_x + i * (box_w + gap)
        draw.rectangle([bx, box_y, bx + box_w, box_y + box_h], fill=bg_col, outline=(160, 160, 160), width=1)
        draw.text((bx + 12, box_y + 12), b_title, fill=(20, 20, 20), font=font_box_title)
        draw.line([bx + 10, box_y + 36, bx + box_w - 10, box_y + 36], fill=(180, 180, 180), width=1)
        
        iy = box_y + 44
        for item in b_items:
            draw.text((bx + 12, iy), item, fill=(50, 50, 50), font=font_box_body)
            iy += 20

        # Arrow between boxes
        if i < len(boxes) - 1:
            ax = bx + box_w + 5
            ay = box_y + box_h // 2
            draw.line([ax, ay, ax + 16, ay], fill=(100, 100, 100), width=2)
            draw.polygon([(ax + 16, ay), (ax + 11, ay - 4), (ax + 11, ay + 4)], fill=(100, 100, 100))

    # Bottom UI row: Web Interface / Dashboard box
    ui_box_x = 250
    ui_box_y = 330
    ui_box_w = w - 500
    ui_box_h = 120
    draw.rectangle([ui_box_x, ui_box_y, ui_box_x + ui_box_w, ui_box_y + ui_box_h], fill=(241, 245, 249), outline=(148, 163, 184), width=1)
    draw.text((ui_box_x + 20, ui_box_y + 15), "Flask Real-Time Web Interface & REST API Engine", fill=(15, 23, 42), font=font_box_title)
    draw.text((ui_box_x + 20, ui_box_y + 45), "• Real-Time Chart.js Visualizations (CPU, RAM, Disk, Net I/O)    • Severity Badges & Anomaly Timeline", fill=(51, 65, 85), font=font_box_body)
    draw.text((ui_box_x + 20, ui_box_y + 70), "• Live Multi-Source Log Streaming & Filter Matrix                • Interactive Manual & Autonomous Self-Healing Trigger", fill=(51, 65, 85), font=font_box_body)
    draw.text((ui_box_x + 20, ui_box_y + 92), "• Dynamic System Health Gauge & Alert Manager With Cooldown Throttling", fill=(51, 65, 85), font=font_box_body)

    # Caption for Figure 1
    draw.text((w // 2 - 140, 455), "Figure 1: Overall architecture of PredictiveGuard", fill=(10, 10, 10), font=font_caption)

    # Bottom Half: Two screenshots side-by-side
    dash_img_path = os.path.join("screenshots", "fig2_dashboard.png")
    pred_img_path = os.path.join("screenshots", "fig5_predictions.png")

    target_w = 710
    target_h = 440

    if os.path.exists(dash_img_path):
        d_img = Image.open(dash_img_path).resize((target_w, target_h), Image.Resampling.LANCZOS)
        comp.paste(d_img, (35, 520))
        draw.rectangle([35, 520, 35 + target_w, 520 + target_h], outline=(200, 200, 200), width=1)
    
    if os.path.exists(pred_img_path):
        p_img = Image.open(pred_img_path).resize((target_w, target_h), Image.Resampling.LANCZOS)
        comp.paste(p_img, (790, 520))
        draw.rectangle([790, 520, 790 + target_w, 520 + target_h], outline=(200, 200, 200), width=1)

    # Captions for Figure 2 and Figure 3
    draw.text((180, 985), "Figure 2: Dashboard showing system telemetry & health score", fill=(10, 10, 10), font=font_caption)
    draw.text((910, 985), "Figure 3: Failure predictions and autonomous recovery logs", fill=(10, 10, 10), font=font_caption)

    out_file = os.path.join("screenshots", "idf_p2_composite.png")
    comp.save(out_file, quality=95)
    print("Saved", out_file)

if __name__ == "__main__":
    create_idf_page2_composite()

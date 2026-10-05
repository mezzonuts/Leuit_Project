from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    img = Image.new('RGBA', (size, size), (22, 163, 74, 255))  # Green #16a34a
    draw = ImageDraw.Draw(img)
    
    # Draw a simple "L" letter
    font_size = size // 2
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Center the letter
    bbox = draw.textbbox((0, 0), "L", font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), "L", fill=(255, 255, 255, 255), font=font)
    
    img.save(output_path, 'PNG')
    print(f"Created: {output_path}")

os.makedirs("frontend/public/icons", exist_ok=True)
create_icon(192, "frontend/public/icons/icon-192.png")
create_icon(512, "frontend/public/icons/icon-512.png")
create_icon(180, "frontend/public/icons/apple-touch-icon.png")
print("Done!")

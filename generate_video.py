import numpy as np
import math
from PIL import Image, ImageDraw

def draw_thick_line(draw, pt1, pt2, color, thickness):
    """Draws a thick line with rounded, realistic joints."""
    draw.line([pt1, pt2], fill=color, width=thickness)
    r = thickness // 2
    draw.ellipse([pt1[0]-r, pt1[1]-r, pt1[0]+r, pt1[1]+r], fill=color)
    draw.ellipse([pt2[0]-r, pt2[1]-r, pt2[0]+r, pt2[1]+r], fill=color)

def draw_base_body(draw, cx, cy):
    """Draws a clinical mannequin torso, head, and legs."""
    # Chair back
    draw.rectangle([cx-70, cy-40, cx+70, cy+180], fill=(40, 40, 45))
    
    # Head and Neck
    draw.line([cx, cy-40, cx, cy-20], fill=(200, 200, 200), width=30) 
    draw.ellipse([cx-40, cy-110, cx+40, cy-30], fill=(220, 220, 220)) 
    
    # Torso
    draw.ellipse([cx-75, cy-20, cx+75, cy+160], fill=(180, 180, 180)) 
    
    # Legs (Dark Gray)
    draw_thick_line(draw, (cx-40, cy+140), (cx-40, cy+250), (100, 100, 100), 50)
    draw_thick_line(draw, (cx+40, cy+140), (cx+40, cy+250), (100, 100, 100), 50)

def generate_reach():
    frames = []
    w, h, fps = 640, 480, 30
    cx, cy = w // 2, h // 3
    for t in range(fps * 6): 
        img = Image.new('RGB', (w, h), color=(240, 245, 250)) # Clinical soft background
        draw = ImageDraw.Draw(img)
        draw_base_body(draw, cx, cy)
        
        ext = (math.sin(t * 0.05) + 1) / 2 
        
        # Right Arm (Static, resting on lap)
        draw_thick_line(draw, (cx+60, cy+10), (cx+70, cy+100), (150, 150, 150), 35)

        # Left Arm (Reaching - highlighted in clinical blue)
        l_elb_x = int((cx - 65) - 30 * ext)
        l_elb_y = int(cy + 80 - 40 * ext)
        l_wri_x = int(l_elb_x + 10 + 50 * ext)
        l_wri_y = int(l_elb_y + 60 - 70 * ext)
        thickness = int(35 + 15 * ext) # Gets slightly thicker as it reaches forward
        
        draw_thick_line(draw, (cx-65, cy+10), (l_elb_x, l_elb_y), (70, 130, 180), 35) 
        draw_thick_line(draw, (l_elb_x, l_elb_y), (l_wri_x, l_wri_y), (100, 160, 210), thickness)
        
        frames.append(img)
    frames[0].save('reach_demo.gif', save_all=True, append_images=frames[1:], duration=33, loop=0)
    print("Created reach_demo.gif")

def generate_slide():
    frames = []
    w, h, fps = 640, 480, 30
    cx, cy = w // 2, h // 3
    for t in range(fps * 6): 
        img = Image.new('RGB', (w, h), color=(240, 245, 250))
        draw = ImageDraw.Draw(img)
        draw_base_body(draw, cx, cy)
        
        # Table
        draw.rectangle([cx-180, cy+110, cx+180, cy+130], fill=(139, 69, 19))

        ext = (math.sin(t * 0.05) + 1) / 2 
        
        # Right Arm
        draw_thick_line(draw, (cx+60, cy+10), (cx+70, cy+100), (150, 150, 150), 35)
        
        # Left Arm (Sliding)
        l_elb_x = int((cx - 65) - 40 * ext)
        l_wri_x = int(l_elb_x - 30 - 60 * ext)
        
        draw_thick_line(draw, (cx-65, cy+10), (l_elb_x, cy+60), (70, 130, 180), 35) 
        draw_thick_line(draw, (l_elb_x, cy+60), (l_wri_x, cy+100), (100, 160, 210), 35)
        # Towel
        draw.ellipse([l_wri_x-25, cy+95, l_wri_x+25, cy+115], fill=(255, 255, 255))

        frames.append(img)
    frames[0].save('slide_demo.gif', save_all=True, append_images=frames[1:], duration=33, loop=0)
    print("Created slide_demo.gif")

def generate_bilateral():
    frames = []
    w, h, fps = 640, 480, 30
    cx, cy = w // 2, h // 3
    for t in range(fps * 6): 
        img = Image.new('RGB', (w, h), color=(240, 245, 250))
        draw = ImageDraw.Draw(img)
        draw_base_body(draw, cx, cy)

        ext = (math.sin(t * 0.05) + 1) / 2 
        y_wri = int(cy + 100 - 130 * ext) 
        
        # Left Arm
        l_elb_x, l_elb_y = int(cx - 85), int(cy + 60 - 30 * ext)
        draw_thick_line(draw, (cx-65, cy+10), (l_elb_x, l_elb_y), (70, 130, 180), 35) 
        draw_thick_line(draw, (l_elb_x, l_elb_y), (cx-65, y_wri), (100, 160, 210), 35)

        # Right Arm
        r_elb_x, r_elb_y = int(cx + 85), int(cy + 60 - 30 * ext)
        draw_thick_line(draw, (cx+65, cy+10), (r_elb_x, r_elb_y), (70, 130, 180), 35) 
        draw_thick_line(draw, (r_elb_x, r_elb_y), (cx+65, y_wri), (100, 160, 210), 35)

        frames.append(img)
    frames[0].save('bilateral_demo.gif', save_all=True, append_images=frames[1:], duration=33, loop=0)
    print("Created bilateral_demo.gif")

if __name__ == "__main__":
    generate_reach()
    generate_slide()
    generate_bilateral()
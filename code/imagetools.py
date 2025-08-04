import subprocess
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import shutil



def detect_bounding_boxes(image_path, alpha_threshold=0, min_line_height=5, line_gap_threshold=1):
    """
    Detect bounding boxes for text lines in an image
    
    Args:
        image_path: Path to image file
        alpha_threshold: Minimum alpha value to consider as non-transparent (0-255)
        min_line_height: Minimum height in pixels for a line to be considered text
        line_gap_threshold: Minimum gap between lines to separate them
    
    Returns:
        List of bounding box dictionaries with x, y, width, height, right, bottom
    """
    try:
        img = Image.open(image_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Get image data as numpy array
        img_array = np.array(img)
        
        # Find non-transparent pixels (alpha > threshold)
        alpha_channel = img_array[:, :, 3]
        non_transparent = np.where(alpha_channel > alpha_threshold)
        
        if len(non_transparent[0]) == 0:
            return []
        
        # Get overall bounding box first
        min_y, max_y = non_transparent[0].min(), non_transparent[0].max()
        min_x, max_x = non_transparent[1].min(), non_transparent[1].max()
        
        # Create a binary mask of the text region
        text_mask = np.zeros((img.height, img.width), dtype=bool)
        text_mask[non_transparent] = True
        
        # Find horizontal projection (count of pixels per row)
        horizontal_projection = np.sum(text_mask[min_y:max_y+1, min_x:max_x+1], axis=1)
        
        # Find line boundaries
        line_boundaries = []
        in_line = False
        line_start = 0
        
        for i, pixel_count in enumerate(horizontal_projection):
            row_index = min_y + i
            
            if pixel_count > 0 and not in_line:
                line_start = row_index
                in_line = True
            elif pixel_count == 0 and in_line:
                line_end = row_index - 1
                if line_end - line_start >= min_line_height:
                    line_boundaries.append((line_start, line_end))
                in_line = False
        
        # Handle case where last line extends to the end
        if in_line and max_y - line_start >= min_line_height:
            line_boundaries.append((line_start, max_y))
        
        # Merge lines that are too close together
        merged_boundaries = []
        for line_start, line_end in line_boundaries:
            if merged_boundaries and line_start - merged_boundaries[-1][1] <= line_gap_threshold:
                merged_boundaries[-1] = (merged_boundaries[-1][0], line_end)
            else:
                merged_boundaries.append((line_start, line_end))
        
        # Create bounding boxes for each line
        bboxes = []
        for line_start, line_end in merged_boundaries:
            # Find horizontal bounds for this line
            line_mask = text_mask[line_start:line_end+1, :]
            line_pixels = np.where(line_mask)
            
            if len(line_pixels[1]) > 0:
                line_min_x = line_pixels[1].min()
                line_max_x = line_pixels[1].max()
                
                bbox = {
                    'x': int(line_min_x),
                    'y': int(line_start),
                    'width': int(line_max_x - line_min_x + 1),
                    'height': int(line_end - line_start + 1),
                    'right': int(line_max_x),
                    'bottom': int(line_end)
                }
                bboxes.append(bbox)
        return bboxes
        
    except Exception as e:
        print(f"Detection error: {e}")
        return []

def draw_bounding_boxes(image_path, bboxes, output_path, selected_bbox=0, skip = False):
    """
    Draw bounding boxes on image and save result
    
    Args:
        image_path: Path to original image
        bboxes: List of bounding box dictionaries
        output_path: Path to save visualization
    """
    
    img = Image.open(image_path)
    print(f"Image mode: {img.mode}")
    draw = ImageDraw.Draw(img, mode=img.mode)
    
    for i, bbox in enumerate(bboxes):
        if i == selected_bbox:
            color = 2
        else:
            color = 3

        # Draw bounding box rectangle
        x, y = bbox['x'], bbox['y']
        right, bottom = bbox['right'], bbox['bottom']

        if not skip:
            draw.rectangle(xy = [x, y, right, bottom], outline=color, width=2)
        else:
            draw.rectangle(xy = [0, 0, 0, 0], outline="blue", width=2)

        # Add text label
        text = f"Line {i+1}: {bbox['width']}x{bbox['height']}"
        
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        # Position text above bounding box
        text_x = x
        text_y = y - 15 if y > 15 else y + bbox['height'] + 5
        
        # Draw text background
        text_bbox = draw.textbbox((text_x, text_y), text, font=font)
        #draw.rectangle([text_bbox[0]-2, text_bbox[1]-2, text_bbox[2]+2, text_bbox[3]+2], 
        #                fill=(255, 255, 255, 200))
        #draw.text((text_x, text_y), text, fill=color, font=font)
    img = img.convert('P')
    img.save(output_path)
    print(f"Saved visualization with {len(bboxes)} bounding boxes to {output_path}")
        
    # except Exception as e:
    #     print(f"Drawing error: {e}")

# def apply_write_config(write_config_json = {}, selected_bbox=0):
#     """
#     Apply the write config JSON to the image processing functions.
    
#     Args:
#         write_config_json: Dictionary containing configuration options
#     """
#     original_png = write_config_json['original_png']
#     output_png = write_config_json['output_png']
#     draw_bboxes = write_config_json['draw_bboxes']
#     delete_japanese = write_config_json['delete_japanese']
#     font_size = write_config_json['font_size']
#     font_name = write_config_json['font_name']
#     text_color = write_config_json['text_color']
#     text_outline = write_config_json['text_outline']
#     lines = write_config_json['lines']
#     bboxes = write_config_json['bboxes']
#     stroke_width = write_config_json['stroke_width']
#     # Detect bounding boxes
#     shutil.copy(original_png, output_png)

#     if delete_japanese:
#         # Erase bounding boxes (make transparent)
#         erase_bounding_boxes(output_png, bboxes, output_png, fill=(0, 0, 0, 0))

#     if draw_bboxes and bboxes:
#         draw_bounding_boxes(output_png, bboxes, output_png, selected_bbox=selected_bbox)
    
#     # Write text onto the image
#     if lines:
#         for i, bbox in enumerate(bboxes):
#             write_onto_png(output_png, output_png, lines[i],
#                            font_size=font_size, x=bbox["x"], y=bbox["bottom"], 
#                            color=text_color, font=font_name, stroke_width=stroke_width)

# Example usage
if __name__ == "__main__":
    image_path = "text_image.png"
    
    # Detect bounding boxes
    bboxes = detect_bounding_boxes(image_path)
    print(f"Found {len(bboxes)} text lines")
    
    # Draw bounding boxes
    if bboxes:
        draw_bounding_boxes(image_path, bboxes, "output_with_boxes.png")



def get_available_fonts():
    """
    Get list of available fonts from ImageMagick
    """
    cmd = [
        "C:/Users/nickf/Documents/Zoids_FMC/tools/ImageMagick/magick.exe",
        "-list", "font"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            fonts = []
            for line in result.stdout.split('\n'):
                if 'Font:' in line:
                    font_name = line.split('Font:')[1].strip()
                    fonts.append(font_name)
            return fonts
        else:
            print(f"Error getting fonts: {result.stderr}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def write_onto_png(input_png, output_png, text, font_size=24, x=10, y=30, height=22, color="white", font_path=None,
                   text_outline=True, stroke_color="black", stroke_width=2):
    """
    Overlay text onto a PNG image using PIL, with optional outline/stroke.

    Args:
        input_png: Path to input PNG file
        output_png: Path to output PNG file
        text: Text to add
        font_size: Font size in points
        x, y: Text position coordinates
        color: Text color (e.g., "white", "red", "#FF0000")
        font: Font name or path to TTF file
        text_outline: Whether to draw outline/stroke
        stroke_color: Outline color
        stroke_width: Outline width
    """
    if not os.path.exists(input_png):
        print(f"Error: Input file does not exist: {input_png}")
        return

    img = Image.open(input_png).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Try to load the specified font, fallback to default if not found
    try:
        font_obj = ImageFont.truetype(font_path, font_size)
    except Exception:
        font_obj = ImageFont.load_default()
        print(f"Warning: Could not load font '{font_path}', using default.")

    # In PIL, (x, y) is the top-left corner of the text bounding box, not the bottom-right.
    y = y - height - 5

    # Draw outline/stroke if requested
    if text_outline and stroke_width > 0:
        # Draw text multiple times offset by stroke_width in all directions
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font_obj, fill=stroke_color)

    # Draw main text
    draw.text((x, y), text, font=font_obj, fill=color)

    # Convert to 'P' mode for palette-based PNG if needed
    img = img.convert('P')
    img.save(output_png)
    print(f"Added text '{text}' at ({x}, {y}) and saved to {output_png}")

def write_onto_png_old(input_png, output_png, text, font_size=24, x=10, y=30, color="white", font="Arial",
                    text_outline=True, stroke_color="black", stroke_width=2):
    """
    ImageMagick text overlay function with optional stroke/outline effects and font selection.

    Args:
        input_png: Path to input PNG file
        output_png: Path to output PNG file
        text: Text to add
        font_size: Font size in points
        x, y: Text position coordinates
        color: Text color (e.g., "white", "red", "#FF0000")
        font: Font name (use list_common_fonts() to see options)
        stroke_color: Outline color (optional)
        stroke_width: Outline width (optional)
    """

    print(f"Adding text: {text} at ({x}, {y}) with font '{font}'")
    if not os.path.exists(input_png):
        print(f"Error: Input file does not exist: {input_png}")
        return

    cmd = [
        "C:/Users/nickf/Documents/Zoids_FMC/tools/ImageMagick/magick.exe",
        input_png,
        "-font", font,
        "-pointsize", str(font_size),
        "-fill", color,
    ]

    if text_outline:
        cmd += [
            "-stroke", stroke_color,
            "-strokewidth", str(stroke_width),
        ]

    cmd += [
        "-draw", f"text {x},{y} '{text}'",
        output_png
    ]

    print(f"Using font: {font}" + (f" with stroke {stroke_color} width {stroke_width}" if stroke_color else ""))
    print(f"Command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Successfully added text" + (" with effects" if stroke_color else ""))
    else:
        print(f"Error: {result.stderr}")

def erase_bounding_boxes(image_path, bboxes, output_path, fill=(0, 0, 0, 0)):
    """
    Erase (make transparent or fill) all pixels inside the given bounding boxes.

    Args:
        image_path: Path to input image.
        bboxes: List of bounding box dictionaries.
        output_path: Path to save the modified image.
        fill: RGBA tuple to fill the erased area (default: fully transparent).
    """
    img = Image.open(image_path).convert('RGBA')
    draw = ImageDraw.Draw(img)
    for bbox in bboxes:
        x, y = bbox['x'], bbox['y']
        right, bottom = bbox['right'], bbox['bottom']
        draw.rectangle([x, y, right, bottom], fill=fill)
    img = img.convert('P')  # Ensure P mode for transparency
    img.save(output_path)
    print(f"Erased {len(bboxes)} bounding boxes and saved to {output_path}")

def convert_png_to_P(img_path):
    """
    Convert a PNG image to P mode (palette-based) for reduced file size.

    Args:
        img_path: Path to input PNG file.
        output_path: Path to save the converted image.
    """
    img = Image.open(img_path).convert('P')
    img.save(img_path)
    print(f"Converted {img_path} to P mode")

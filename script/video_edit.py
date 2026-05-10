import os, subprocess, json
from math import ceil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from config import VIDEO_DIR, SHARE_DIR, OUTPUT_DIR

FONT_BOLD_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
W, H = 1080, 1920

WHITE = (255, 255, 255)
GOLD = (252, 208, 20)
BLACK = (0, 0, 0)

IMG_TOP = int(H * 0.275)
IMG_BOTTOM = int(H * 0.789)

MAX_TEXT_W = int(W * 0.9)

def _wrap_by_pixel(text, font, draw, max_w):
    lines = []
    cur = ""
    for ch in text:
        test = cur + ch
        bb = draw.textbbox((0, 0), test, font=font)
        if bb[2] - bb[0] > max_w and cur:
            lines.append(cur)
            cur = ch
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines

def make_frame(image_path, display_text):
    canvas = Image.new("RGB", (W, H), BLACK)

    img = Image.open(image_path).convert("RGB")

    from PIL import ImageFilter
    img = img.filter(ImageFilter.SMOOTH)

    img_w, img_h = img.size
    crop_h = IMG_BOTTOM - IMG_TOP
    if img_w >= img_h:
        new_w = max(W, int(crop_h * img_w / img_h))
        new_h = crop_h
        if new_w < W:
            new_w = W
            new_h = int(W * img_h / img_w)
    else:
        new_w = W
        new_h = max(crop_h, int(W * img_h / img_w))
    img_resized = img.resize((new_w, new_h), Image.LANCZOS)

    paste_x = (W - new_w) // 2
    paste_y = IMG_TOP + (crop_h - new_h) // 2
    canvas.paste(img_resized, (paste_x, paste_y))

    canvas_rgba = canvas.convert("RGBA")

    grad_top = int(H * 0.04)
    overlay_top = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay_top)
    for row in range(grad_top):
        alpha = int(255 * (1 - row / grad_top))
        ov_draw.line([(0, IMG_TOP + row), (W, IMG_TOP + row)], fill=(0, 0, 0, alpha))
    canvas_rgba = Image.alpha_composite(canvas_rgba, overlay_top)

    grad_bot = int(H * 0.03)
    overlay_bot = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov2_draw = ImageDraw.Draw(overlay_bot)
    for row in range(grad_bot):
        alpha = int(255 * (row / grad_bot))
        ov2_draw.line([(0, IMG_BOTTOM - grad_bot + row), (W, IMG_BOTTOM - grad_bot + row)], fill=(0, 0, 0, alpha))
    canvas = Image.alpha_composite(canvas_rgba, overlay_bot).convert("RGB")

    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(FONT_BOLD_PATH, 88)

    if "\n" in display_text:
        raw_lines = display_text.split("\n", 1)
    else:
        raw_lines = display_text.split(",", 1) if "," in display_text else [display_text]

    line1 = raw_lines[0].strip()[:12] if len(raw_lines) > 0 else ""
    line2 = raw_lines[1].strip()[:12] if len(raw_lines) > 1 else ""

    texts_top = int(H * 0.149)
    line_h = 88 + 15

    for i, line in enumerate([line1, line2]):
        if not line:
            continue
        color = WHITE if i == 0 else GOLD
        bb = draw.textbbox((0, 0), line, font=font)
        tw = bb[2] - bb[0]
        x = (W - tw) / 2
        y = texts_top + i * line_h
        draw.text((x, y), line, font=font, fill=color)

    return canvas

def create_clips(image_paths, audio_paths, durations, scenes=None):
    os.makedirs(VIDEO_DIR, exist_ok=True)

    if scenes is None:
        scenes_path = os.path.join(OUTPUT_DIR, "scenes.json")
        if os.path.exists(scenes_path):
            with open(scenes_path) as f:
                scenes = json.load(f)

    for i in range(len(image_paths)):
        scene = i + 1
        frame_path = os.path.join(VIDEO_DIR, f"frame_{scene}.png")
        clip_path = os.path.join(VIDEO_DIR, f"clip_{scene}.mp4")

        display_text = ""
        if scenes and i < len(scenes):
            s = scenes[i]
            display_text = s.get("display_text", s.get("narration", ""))

        frame = make_frame(image_paths[i], display_text)
        frame.save(frame_path)

        total_dur = durations[i] + 5.0

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", frame_path,
            "-i", audio_paths[i],
            "-c:v", "libx264",
            "-c:a", "aac",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-t", f"{total_dur:.2f}",
            clip_path
        ]
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    concat_path = os.path.join(VIDEO_DIR, "concat.txt")
    with open(concat_path, "w") as f:
        for i in range(len(image_paths)):
            cp = os.path.join(VIDEO_DIR, f"clip_{i+1}.mp4")
            f.write(f"file '{cp}'\n")

    final_path = os.path.join(VIDEO_DIR, "final.mp4")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_path,
        "-c", "copy",
        final_path
    ], capture_output=True, text=True, timeout=120)

    share_path = os.path.join(SHARE_DIR, "final.mp4")
    subprocess.run(["cp", final_path, share_path], timeout=10)

    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", final_path],
        capture_output=True, text=True, timeout=10
    )
    final_dur = float(result.stdout.strip())

    return final_path, share_path, final_dur
import os, time, requests, random, copy, io
from PIL import Image, ImageEnhance, ImageFilter

from config import COMFY_API, COMFY_WORKFLOW, IMAGES_DIR

def _download_image(api_url, filename, subfolder, img_type):
    r = requests.get(f"{api_url}/view", params={"filename": filename, "subfolder": subfolder, "type": img_type}, timeout=30)
    return Image.open(io.BytesIO(r.content))

def generate_images(image_prompts):
    image_paths = []
    for i, prompt in enumerate(image_prompts):
        scene = i + 1
        print(f"  Generating image {scene}/{len(image_prompts)}...", flush=True)

        workflow = copy.deepcopy(COMFY_WORKFLOW)
        workflow["6"]["inputs"]["prompt"] = prompt
        workflow["9"]["inputs"]["seed"] = random.randint(1, 99999)
        workflow["11"]["inputs"]["filename_prefix"] = f"shorts_{scene}"

        resp = requests.post(f"{COMFY_API}/prompt", json={"prompt": workflow}, timeout=10)
        pid = resp.json().get("prompt_id", "")
        if not pid:
            raise RuntimeError(f"ComfyUI error: {resp.json()}")

        for _ in range(300):
            time.sleep(2)
            try:
                h = requests.get(f"{COMFY_API}/history", timeout=5).json()
                if pid in h and h[pid].get("status", {}).get("status_str") == "success":
                    break
            except:
                pass

        h = requests.get(f"{COMFY_API}/history", timeout=5).json()
        img_info = None
        for nid, no in h[pid].get("outputs", {}).items():
            imgs = no.get("images", [])
            if imgs:
                img_info = imgs[-1]
                break
        if not img_info:
            raise RuntimeError(f"No output image for scene {scene}")

        img = _download_image(COMFY_API, img_info["filename"], img_info.get("subfolder", ""), img_info.get("type", "output"))

        img = ImageEnhance.Contrast(img).enhance(1.35)
        img = ImageEnhance.Sharpness(img).enhance(8.0)
        img = ImageEnhance.Brightness(img).enhance(1.05)
        img = ImageEnhance.Color(img).enhance(1.2)
        img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=150, threshold=0))
        img = ImageEnhance.Sharpness(img).enhance(1.5)

        out_path = os.path.join(IMAGES_DIR, f"scene_{scene}.png")
        img.save(out_path)
        image_paths.append(out_path)

    return image_paths

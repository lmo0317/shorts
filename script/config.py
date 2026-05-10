import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_DIR = os.path.join(BASE_DIR, "script")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
TTS_DIR = os.path.join(OUTPUT_DIR, "tts")
VIDEO_DIR = os.path.join(OUTPUT_DIR, "video")
SHARE_DIR = "/home/lmo0317/share"

LLM_API_KEY = "sk-fIFrh97fxYzdXBuy7ckY6lyPdSGLZsGkJJRECp21m9zqFcY4t6BIQbGBcci6m8Cu"
LLM_BASE_URL = "https://opencode.ai/zen/go/v1"
LLM_MODEL = "deepseek-v4-flash"

COMFY_API = "http://192.168.219.120:8000"
COMFY_OUTPUT = None

TTS_MODEL_PATH = "/home/lmo0317/models/Qwen3-TTS-0.6B"
TTS_REF_VOICE = "/tmp/ref_voice.wav"
TTS_SAMPLE_RATE = 24000
TTS_PYTHON = "/home/lmo0317/miniconda3/envs/qwen-tts/bin/python"

NUM_SCENES = 6

COMFY_WORKFLOW = {
    "3": {"class_type": "UNETLoader", "inputs": {"unet_name": "z_image_turbo_bf16.safetensors", "weight_dtype": "default"}},
    "12": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "qwen_image"}},
    "6": {"class_type": "TextEncodeZImageOmni", "inputs": {"prompt": "", "auto_resize_images": True, "clip": ["12", 0]}},
    "7": {"class_type": "TextEncodeZImageOmni", "inputs": {"prompt": "ugly, blurry, low quality, deformed, disfigured, text, watermark, cropped, extra limbs, bad anatomy, naked, explicit, nude, porn", "auto_resize_images": True, "clip": ["12", 0]}},
    "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
    "10": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
    "8": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["10", 0]}},
    "9": {"class_type": "KSampler", "inputs": {"seed": 42, "steps": 12, "cfg": 2.0, "sampler_name": "euler", "scheduler": "sgm_uniform", "denoise": 1.0, "model": ["3", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
    "11": {"class_type": "SaveImage", "inputs": {"filename_prefix": "shorts", "images": ["8", 0]}},
}

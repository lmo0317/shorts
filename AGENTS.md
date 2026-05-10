# NatePann Shorts Pipeline - AGENTS.md

## Project Overview
Automated shorts video pipeline: crawl -> AI rewrite -> TTS -> image gen -> video assembly.

## Tech Stack
- **LLM**: DeepSeek V4 Flash via OpenCode Go API (`https://opencode.ai/zen/go/v1`)
- **TTS**: Qwen3-TTS-0.6B (local, `/home/lmo0317/models/Qwen3-TTS-0.6B`)
- **Image**: Remote ComfyUI at `192.168.219.120:8000` (z_image_turbo_bf16, 6 steps)
- **Video**: 1080x1920 portrait, NotoSansCJK-Bold, dark theme + gold accent
- **Python venv**: `/home/lmo0317/comfy/ComfyUI/venv/bin/python3`
- **Output**: `/home/lmo0317/share/final.mp4`

## Key Files
- `script/main.py` - Pipeline orchestrator
- `script/crawler.py` - NatePann scraper (`get_top_by_views()`)
- `script/ai_rewrite.py` - DeepSeek V4 Flash rewrite
- `script/tts.py` - Qwen3-TTS generation
- `script/image_gen.py` - Remote ComfyUI API
- `script/video_edit.py` - Styled frame composition + ffmpeg assembly
- `script/config.py` - All config (API keys, paths, workflow dict)
- `script/templates/system_prompt.txt` - LLM prompt

## Video Layout (matching reference screenshot)
- Canvas: 1080x1920, black background
- White text (255,255,255) at y=14.9%, Bold 88px
- Gold text (252,208,20) at y=21%, Bold 88px
- Image region: y=27.5% to y=78.9%
- Gradient overlays at image top/bottom edges
- Narration: exactly 2 lines, max 12 chars each, `\n` separated
- Font: `/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc`

## Pipeline Order
1. Crawl articles (`crawler.py`)
2. AI rewrite (`ai_rewrite.py`) - produces 2-line narrations per scene
3. Generate images (remote ComfyUI)
4. Free local GPU memory (`free_comfy_memory()`)
5. Generate TTS (local Qwen3-TTS)
6. Assemble video (`video_edit.py`)

## Run Command
```bash
cd /home/lmo0317/shorts_v2/script && /home/lmo0317/comfy/ComfyUI/venv/bin/python3 main.py --articles 1
```

---

## Skill: Content Research (콘텐츠 리서치)

### Invocation
User says: "리서치 해줘", "콘텐츠 찾아줘", "소스 가져와", etc. with a topic keyword.

### How to Run
```bash
cd /home/lmo0317/shorts_v2/script && /home/lmo0317/comfy/ComfyUI/venv/bin/python3 research.py [키워드] [옵션]
```

Options:
- `--nate N` - NatePann results count (default: 10)
- `--youtube N` - YouTube results count (default: 10)
- `--ranking` - Use NatePann hot ranking instead of keyword search
- `--json` - Output as JSON

Examples:
```bash
# 커플 갈등 리서치
python3 research.py 커플 갈등

# 연애 서운함 리서치 (JSON 출력)
python3 research.py 연애 서운함 --json

# 네이트판 인기글 리서치
python3 research.py --ranking
```

### Output Format
Always present results as TWO tables:

**YouTube Shorts:**

| # | 제목 | 간략 내용 | 조회수 |
|---|------|----------|--------|
| 1 | ... | ... | ... |

**네이트판:**

| # | 제목 | 간략 내용 | 조회수/댓글 |
|---|------|----------|------------|
| 1 | ... | ... | ... |

### Fallback
If `research.py` script results are insufficient (YouTube scraping is limited without API), supplement with:
1. Use the Task tool (subagent_type "general") to webfetch search YouTube and NatePann
2. Combine script results + web search results
3. Present in the same table format

### After User Selection
Once user picks topics, use the pipeline to:
1. Crawl from NatePann using `get_top_by_views()` or use selected topic as source
2. Run `ai_rewrite.py` to create scenes with 2-line narrations
3. Generate images, TTS, and video
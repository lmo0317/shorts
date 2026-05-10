---
name: shorts
description: "Shorts pipeline: /shorts 리서치 [키워드] for content research, /shorts 제작 [대본파일] for video production"
metadata:
  audience: content-creators
  workflow: youtube-natepann-research
---

## Sub-commands

This skill has two modes. Parse the user's input after `/shorts` to determine which mode:

### `/shorts 리서치 [키워드]` — Content Research

Search YouTube Shorts AND NatePann for trending content. Default keyword: 연애 갈등

**Examples:**
- `/shorts 리서치` — search default topic (연애 갈등)
- `/shorts 리서치 가스라이팅` — search gaslighting content
- `/shorts 리서치 이별 후회` — search breakup regret

**Steps:**
1. Run: `cd /home/lmo0317/shorts_v2/script && /home/lmo0317/comfy/ComfyUI/venv/bin/python3 research.py [KEYWORD]`
2. Options: `--nate N`, `--youtube N`, `--ranking`, `--json`
3. If script results are insufficient (especially YouTube), supplement with Task tool (subagent_type "general") web searches
4. Present results as TWO formatted tables:

**YouTube Shorts:**

| # | 제목 | 간략 내용 | 조회수 |
|---|------|----------|--------|

**네이트판:**

| # | 제목 | 간략 내용 | 조회수/댓글 |
|---|------|----------|------------|

5. Ask: "어떤 걸 각색할까요?"

### `/shorts 제작 [대본파일]` — Video Production

Run the full shorts pipeline to generate a final video.

**Examples:**
- `/shorts 제작` — run pipeline with NatePann top article (default)
- `/shorts 제작 대본.md` — run pipeline using a custom script file
- `/shorts 제작 scenes.json` — run pipeline using existing scenes

**Steps:**

If no argument provided (default):
```bash
cd /home/lmo0317/shorts_v2/script && /home/lmo0317/comfy/ComfyUI/venv/bin/python3 main.py --articles 1
```

If a script file is provided:
1. Read the file at the given path
2. Parse it as a JSON array of scenes with `scene`, `summary`, `narration` (2 lines, `\n` separated, max 12 chars each), and `image_prompt` fields
3. Save to `/home/lmo0317/shorts_v2/output/scenes.json`
4. Generate images → free GPU → TTS → video assembly

**Skip steps:** If `--skip-research` or `--skip-images` flags are mentioned, skip the corresponding pipeline steps.

## Pipeline Order (for 제작 mode)

1. Crawl articles (`crawler.py`) — unless custom script provided
2. AI rewrite (`ai_rewrite.py`) — produces 2-line narrations per scene
3. Generate images (remote ComfyUI at `192.168.219.120:8000`)
4. Free local GPU memory (`free_comfy_memory()`)
5. Generate TTS (local Qwen3-TTS-0.6B)
6. Assemble video (`video_edit.py`) → output to `/home/lmo0317/share/final.mp4`

## Key Files

- `script/main.py` — Pipeline orchestrator
- `script/crawler.py` — NatePann scraper (`get_top_by_views()`)
- `script/ai_rewrite.py` — DeepSeek V4 Flash rewrite
- `script/tts.py` — Qwen3-TTS generation
- `script/image_gen.py` — Remote ComfyUI API
- `script/video_edit.py` — Styled frame composition + ffmpeg
- `script/research.py` — Content research script (YouTube + NatePann)
- `script/config.py` — All configuration
- `script/templates/system_prompt.txt` — LLM rewrite prompt (2-line narration, max 12 chars each)

## Video Layout (matching reference screenshot)

- Canvas: 1080x1920, black background
- White text (255,255,255) at y=14.9%, Bold 88px
- Gold text (252,208,20) at y=21%, Bold 88px
- Image region: y=27.5% to y=78.9%
- Gradient overlays at image top/bottom edges
- Narration: exactly 2 lines, max 12 chars each, `\n` separated
- Font: `/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc`

## Tech Stack

- **LLM**: DeepSeek V4 Flash via OpenCode Go API
- **TTS**: Qwen3-TTS-0.6B (local, `/home/lmo0317/models/Qwen3-TTS-0.6B`)
- **Image**: Remote ComfyUI at `192.168.219.120:8000` (z_image_turbo_bf16, 6 steps)
- **Python venv**: `/home/lmo0317/comfy/ComfyUI/venv/bin/python3`
- **Output**: `/home/lmo0317/share/final.mp4`

## Important Notes

- Always search BOTH platforms (YouTube + NatePann) for 리서치 mode
- Korean content is primary — search in Korean
- Focus on high-engagement content (views, comments, recommends)
- Default topic is couple/relationship conflict but adapt to user's keyword
- Video layout must match the reference screenshot style
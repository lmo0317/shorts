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
4. Present results as TWO formatted tables. NatePann table includes **본문길이** column — prefer articles with 200+ characters for longer videos.

**YouTube Shorts:**

| # | 제목 | 간략 내용 | 조회수 |
|---|------|----------|--------|

**네이트판:**

| # | 제목 | 간략 내용 | 조회수 | 본문길이 |
|---|------|----------|--------|----------|

5. Ask: "어떤 걸 각색할까요?"

### `/shorts 제작 [대본파일]` — Video Production

Run the full shorts pipeline to generate a final video (~90 seconds).

**Examples:**
- `/shorts 제작` — run pipeline with NatePann top article (default)
- `/shorts 제작 대본.md` — run pipeline using a custom script file

**Steps:**

If no argument provided (default):
```bash
cd /home/lmo0317/shorts_v2/script && /home/lmo0317/comfy/ComfyUI/venv/bin/python3 main.py --articles 1
```

## Pipeline Architecture

- **Image**: 1024x1024 (1:1 square), then fitted into video layout
- **Video**: 1080x1920 portrait (9:16 shorts)
- **Scenes**: 6 scenes for ~90 seconds total
- **display_text**: 2 lines, max 12 chars each (white + gold, shown on screen)
- **narration**: 50~80 chars per scene (for TTS voiceover)
- **Target duration**: ~15 seconds per scene × 6 = ~90 seconds

## Key Files

- `script/main.py` — Pipeline orchestrator
- `script/crawler.py` — NatePann scraper (`get_top_by_views()`)
- `script/ai_rewrite.py` — DeepSeek V4 Flash rewrite (produces display_text + narration)
- `script/tts.py` — Qwen3-TTS generation (reads narration, NOT display_text)
- `script/image_gen.py` — Remote ComfyUI API (1024x1024 images)
- `script/video_edit.py` — Styled frame composition (uses display_text for overlay)
- `script/research.py` — Content research script (YouTube + NatePann)
- `script/config.py` — All configuration (NUM_SCENES=6, 1024x1024 workflow)
- `script/templates/system_prompt.txt` — LLM rewrite prompt

## Video Layout (matching reference screenshot)

- Canvas: 1080x1920, black background
- White text (255,255,255) at y=14.9%, Bold 88px
- Gold text (252,208,20) at y=21%, Bold 88px
- Image region: y=27.5% to y=78.9%
- 1:1 images are cover-fitted (center-cropped to fill width)
- Gradient overlays at image top/bottom edges
- display_text: exactly 2 lines, max 12 chars each, `\n` separated
- narration: 50~80 chars, natural spoken Korean for TTS

## Tech Stack

- **LLM**: DeepSeek V4 Flash via OpenCode Go API
- **TTS**: Qwen3-TTS-0.6B (local)
- **Image**: Remote ComfyUI at `192.168.219.120:8000` (z_image_turbo_bf16, 1024x1024, 6 steps)
- **Python venv**: `/home/lmo0317/comfy/ComfyUI/venv/bin/python3`
- **Output**: `/home/lmo0317/share/final.mp4`

## Important Notes

- Always search BOTH platforms (YouTube + NatePann) for 리서치 mode
- Prefer NatePann articles with 200+ chars body length for ~90s videos
- Korean content is primary — search in Korean
- Video layout must match the reference screenshot style
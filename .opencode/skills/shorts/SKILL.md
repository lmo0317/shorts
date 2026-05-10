---
name: shorts
description: Research trending content from YouTube Shorts and NatePann for couple/relationship conflict themes, then optionally run the full shorts video pipeline (crawl, AI rewrite, TTS, image gen, video assembly)
metadata:
  audience: content-creators
  workflow: youtube-natepann-research
---

## What I do

1. **Content Research**: Search YouTube Shorts AND NatePann for trending content on a given topic (default: couple/relationship conflicts). Present results as two formatted tables (YouTube Shorts + NatePann) with title, summary, and view count.

2. **Video Pipeline**: After topic selection, run the full NatePann shorts pipeline to generate a final video.

## When to use me

Use this skill when the user says anything like:
- "리서치 해줘", "쇼츠 소스 찾아줘", "콘텐츠 찾아줘"
- "유튜브+네이트판에서 가져와"
- "쇼츠 만들어줘", "영상 만들어줘"
- Any request involving finding trending content or running the shorts pipeline

## Step 1: Content Research

Run the research script to gather content from both platforms:

```bash
cd /home/lmo0317/shorts_v2/script && /home/lmo0317/comfy/ComfyUI/venv/bin/python3 research.py [KEYWORD] [OPTIONS]
```

Options:
- `--nate N` - NatePann results count (default: 10)
- `--youtube N` - YouTube results count (default: 10)
- `--ranking` - Use NatePann hot ranking instead of keyword search
- `--json` - Output as JSON

The script outputs two tables:

**YouTube Shorts:**

| # | 제목 | 간략 내용 | 조회수 |
|---|------|----------|--------|

**네이트판:**

| # | 제목 | 간략 내용 | 조회수/댓글 |
|---|------|----------|------------|

If the script results are insufficient (especially for YouTube), supplement with web searches using the Task tool (subagent_type "general"). Combine and present in the same format.

## Step 2: Content Selection

Present results to the user and ask:
"어떤 걸 각색할까요?"

Wait for user selection before proceeding.

## Step 3: Run Pipeline

After user selects content, run the full pipeline:

```bash
cd /home/lmo0317/shorts_v2/script && /home/lmo0317/comfy/ComfyUI/venv/bin/python3 main.py --articles 1
```

## Key Files

- `script/main.py` - Pipeline orchestrator
- `script/crawler.py` - NatePann scraper (`get_top_by_views()`)
- `script/ai_rewrite.py` - DeepSeek V4 Flash rewrite
- `script/tts.py` - Qwen3-TTS generation
- `script/image_gen.py` - Remote ComfyUI API
- `script/video_edit.py` - Styled frame composition + ffmpeg
- `script/research.py` - Content research script (YouTube + NatePann)
- `script/config.py` - All configuration
- `script/templates/system_prompt.txt` - LLM rewrite prompt

## Video Layout (matching reference screenshot)

- Canvas: 1080x1920, black background
- White text (255,255,255) at y=14.9%, Bold 88px
- Gold text (252,208,20) at y=21%, Bold 88px
- Image region: y=27.5% to y=78.9%
- Gradient overlays at image top/bottom edges
- Narration: exactly 2 lines, max 12 chars each, `\n` separated
- Font: `/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc`

## Important Notes

- Always search BOTH platforms (YouTube + NatePann)
- Korean content is primary - search in Korean
- Focus on high-engagement content (views, comments, recommends)
- Default topic is couple/relationship conflict but adapt to user's topic
- The user's reference screenshot style must be maintained in all video output
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

When the user asks to find content ideas for shorts, follow this workflow to search BOTH YouTube Shorts AND NatePann, then present results in a unified table format.

### Step 1: Search YouTube Shorts
Use webfetch to search YouTube for popular shorts on the given topic. Try multiple search queries:

```
https://www.youtube.com/results?search_query={KEYWORD}+쇼츠
```

Search keywords to combine with the topic (use Korean):
- `{topic} 쇼츠`
- `{topic} 연애 쇼츠`
- `{topic} 갈등 쇼츠`
- `{topic} 질문 쇼츠`
- `{topic} 사연 쇼츠`

For each result found, collect:
- Title
- Brief content summary (1-2 sentences)
- View count (if available)
- Comments/engagement (if available)

### Step 2: Search NatePann
The project already has a crawler (`script/crawler.py`). For content research, also use webfetch to search NatePann:

```
https://m.search.nate.com/search/search.html?q={KEYWORD}&ss=natepann
```

Alternatively, browse NatePann hot articles:
```
https://pann.nate.com/talk/ranking
```

For each post, collect:
- Title
- Brief content summary
- View count
- Comment count / recommends

### Step 3: Present Results
Format results as TWO separate tables with these columns:

**YouTube Shorts:**

| # | 제목 | 간략 내용 | 조회수 |
|---|------|----------|--------|
| 1 | ... | ... | ... |

**네이트판:**

| # | 제목 | 간략 내용 | 조회수/댓글 |
|---|------|----------|------------|
| 1 | ... | ... | ... |

Present ~10 items from each source. Sort by popularity (views/recommends).

### Step 4: After User Selection
Once user picks topics, use the pipeline to:
1. Either crawl from NatePann using `get_top_by_views()` or use the selected topic as source
2. Run `ai_rewrite.py` to create scenes with 2-line narrations
3. Generate images, TTS, and video

### Important Notes
- Always search BOTH platforms (YouTube + NatePann)
- Use the Task tool with subagent_type "general" for parallel web searches
- Korean content is primary - search in Korean
- Focus on high-engagement content (views, comments, recommends)
- The user prefers couple/relationship conflict topics by default but may ask for other themes
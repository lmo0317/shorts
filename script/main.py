import sys, os, json, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import NUM_SCENES, OUTPUT_DIR
from crawler import get_top_by_views
from ai_rewrite import rewrite_article
from tts import generate_tts
from image_gen import generate_images
from video_edit import create_clips

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def run_pipeline(scenes):
    for s in scenes:
        dt = s.get("display_text", s.get("narration", "?"))
        nar = s.get("narration", "")[:50]
        log(f"  Scene {s.get('scene', '?')}: display={repr(dt)} nar={nar}...")

    scenes_path = os.path.join(OUTPUT_DIR, "scenes.json")
    with open(scenes_path, "w") as f:
        json.dump(scenes, f, ensure_ascii=False, indent=2)

    log("이미지 생성 중...")
    image_prompts = [s["image_prompt"] for s in scenes]
    try:
        image_paths = generate_images(image_prompts)
    except Exception as e:
        log(f"이미지 생성 실패: {e}")
        return
    log(f"이미지 완료: {len(image_paths)}장")

    log("TTS 생성 중...")
    narrations = [s["narration"] for s in scenes]
    try:
        audio_paths, durations = generate_tts(narrations)
    except Exception as e:
        log(f"TTS 실패: {e}")
        return
    log(f"TTS 완료: 총 {sum(durations):.1f}초")

    log("영상 합성 중...")
    try:
        final_path, share_path, final_dur = create_clips(image_paths, audio_paths, durations, scenes)
    except Exception as e:
        log(f"영상 합성 실패: {e}")
        return

    log(f"✅ 최종 영상: {final_path}")
    log(f"   공유: {share_path}")
    log(f"   길이: {final_dur:.1f}초")
    log(f"   크기: {os.path.getsize(final_path) / 1024 / 1024:.1f}MB")

def main(num_articles=1, script_path=None):
    log("=" * 50)
    log("NatePann Shorts Pipeline 시작")
    log("=" * 50)

    if script_path:
        with open(script_path, encoding="utf-8") as f:
            scenes = json.load(f)
        log(f"대본 로드: {script_path} ({len(scenes)}개 장면)")
        run_pipeline(scenes)
        return

    articles = get_top_by_views(limit=10, min_body=100)
    if isinstance(articles, str):
        log(f"크롤링 실패: {articles}")
        return
    log(f"조회수 Top {len(articles)}개:")

    for a in articles:
        log(f"  {a['_views_int']:>7,}  {a['title'][:50]}")

    for idx, article in enumerate(articles[:num_articles], 1):
        log(f"\n--- 글 {idx}: {article['title']} ---")
        log(f"조회수: {article['views']} | 본문: {len(article['body'])}자")

        log("AI 각색 중...")
        try:
            scenes = rewrite_article(article["title"], article["body"])
        except Exception as e:
            log(f"각색 실패: {e}")
            continue
        log(f"각색 완료: {len(scenes)}개 장면")

        run_pipeline(scenes)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NatePann Shorts Pipeline")
    parser.add_argument("--articles", type=int, default=1, help="처리할 글 개수")
    parser.add_argument("--script", type=str, default=None, help="대본 JSON 파일 경로 (크롤링+AI 각색 스킵)")
    args = parser.parse_args()
    main(num_articles=args.articles, script_path=args.script)
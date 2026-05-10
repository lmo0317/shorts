import os, json, numpy as np, soundfile as sf, torch

from config import TTS_MODEL_PATH, TTS_REF_VOICE, TTS_SAMPLE_RATE, TTS_DIR

def generate_tts(narrations):
    from qwen_tts import Qwen3TTSModel

    torch.cuda.empty_cache()
    torch.manual_seed(42)

    model = Qwen3TTSModel.from_pretrained(
        TTS_MODEL_PATH,
        dtype=torch.bfloat16,
        device_map='cuda:0',
        trust_remote_code=True,
    )

    ref_audio, sr_ref = sf.read(TTS_REF_VOICE)
    if sr_ref != TTS_SAMPLE_RATE:
        import scipy.signal
        ref_audio = scipy.signal.resample(ref_audio, int(len(ref_audio) * TTS_SAMPLE_RATE / sr_ref))

    prompt = model.create_voice_clone_prompt(
        ref_audio=(ref_audio.astype(np.float32), TTS_SAMPLE_RATE),
        ref_text="안녕하세요. 반갑습니다. 오늘 이야기를 들려드릴게요.",
        x_vector_only_mode=False,
    )
    prompt_list = [p.to_dict() if hasattr(p, 'to_dict') else p for p in prompt]

    durations = []
    audio_paths = []
    for i, text in enumerate(narrations):
        scene = i + 1
        output_path = os.path.join(TTS_DIR, f"tts_{scene}.wav")

        torch.manual_seed(42)
        wavs, sr = model.generate_voice_clone(
            text=text,
            language='korean',
            voice_clone_prompt=prompt_list,
            non_streaming_mode=True,
        )

        combined = np.concatenate(wavs)
        sf.write(output_path, combined, sr)

        duration = len(combined) / sr
        durations.append(duration)
        audio_paths.append(output_path)

    durations_path = os.path.join(TTS_DIR, "durations.json")
    with open(durations_path, "w") as f:
        json.dump(durations, f)

    return audio_paths, durations

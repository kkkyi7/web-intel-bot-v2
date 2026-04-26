# -*- coding: utf-8 -*-
"""
声音 A/B 试听 · 第二轮（加速 +15%，新候选）

用法：
    cd C:\Claude\web-intel-bot\04-采集脚本
    python voice_sample_v2.py
"""

import asyncio
import os
import sys
from pathlib import Path

for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
    os.environ.pop(k, None)
print("[proxy] 已绕过代理")

import edge_tts


# 第二轮新候选（不重复 01-04），编号 05 起
VOICES = [
    ("05", "zh-CN-YunfengNeural",  "云枫男声",  "青年男声，比云希更稳一点，音色偏成熟"),
    ("06", "zh-CN-XiaoyiNeural",   "晓伊女声",  "年轻活泼女声，替代挂掉的晓涵"),
    ("07", "zh-CN-XiaomoNeural",   "晓墨女声",  "情感丰富女声，朗读体特化"),
    ("08", "zh-CN-YunhaoNeural",   "云皓男声",  "正式男声，稳重感"),
]

# 加速 +15%（播客甜区）
RATE = "+15%"

SAMPLE_TEXT = (
    "嘿，今天聊一件挺猛的事。OpenAI 又发了 GPT-5，我刷了一下发布会，"
    "最大的感受是，这次他们明显在跟编程能力较劲。"
    "Claude 那边也没闲着，4.5 Opus 据说推理速度快了三倍。"
    "咱们做产品的，看着就一句话：又得加班学新工具了。"
)

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR.parent / "05-数据样本" / "voice-samples"


async def synth_one(idx, voice_id, cn_name, desc, max_retries=2):
    out_path = OUT_DIR / (idx + "-" + cn_name + "-" + voice_id + ".mp3")
    print("  [" + idx + "] " + cn_name + " (" + voice_id + ") -- " + desc)

    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            communicate = edge_tts.Communicate(text=SAMPLE_TEXT, voice=voice_id, rate=RATE)
            await communicate.save(str(out_path))
            size_kb = out_path.stat().st_size / 1024.0
            if size_kb < 5:
                raise RuntimeError("输出文件太小 " + str(round(size_kb, 1)) + "KB")
            print("       OK " + out_path.name + "  (" + str(round(size_kb)) + " KB)")
            return
        except Exception as e:
            last_err = e
            print("       第 " + str(attempt) + "/" + str(max_retries) + " 次失败: " + type(e).__name__)
            if attempt < max_retries:
                await asyncio.sleep(2)

    print("       这个声音生成失败，跳过。最后一次错: " + str(last_err))


async def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("")
    print("声音 A/B 试听 · 第二轮（加速 " + RATE + "）")
    print("稿子（" + str(len(SAMPLE_TEXT)) + " 字）：")
    print("   " + SAMPLE_TEXT)
    print("")

    for idx, voice_id, cn_name, desc in VOICES:
        await synth_one(idx, voice_id, cn_name, desc)

    print("")
    print("生成完毕，去这个文件夹挨个听（跟第一轮的 01-04 在同一个目录）：")
    print("   " + str(OUT_DIR))
    print("")
    print("听完告诉我编号，我把对应声音 + 速度写进 .env。")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("被用户中断。")
        sys.exit(130)

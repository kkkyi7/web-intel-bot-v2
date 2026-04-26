# -*- coding: utf-8 -*-
"""
声音 A/B 试听脚本

让 4 个候选声音念同一段口播稿，方便你听完挑一个最对味的，
然后把选中的声音 ID 写进 .env 的 TTS_VOICE。

用法：
    cd C:\Claude\web-intel-bot\04-采集脚本
    python voice_sample.py
"""

import asyncio
import os
import sys
from pathlib import Path

# 关键：先清掉系统 / .env 里的 HTTP/HTTPS 代理。
# edge-tts 走微软 speech.platform.bing.com，国内直连更稳，
# 走 clash 之类的代理反而经常 NoAudioReceived。
for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
    os.environ.pop(k, None)
print("[proxy] 已绕过代理（edge-tts 走微软直连更稳）")

import edge_tts


VOICES = [
    ("01", "zh-CN-YunxiNeural",     "云希男声",   "阳光年轻男声，最像小宇宙播客主持"),
    ("02", "zh-CN-XiaohanNeural",   "晓涵女声",   "温暖知性大姐姐，得到/混沌讲师风"),
    ("03", "zh-CN-YunjianNeural",   "云健男声",   "体育解说风，节奏感强，硬核题材合适"),
    ("04", "zh-CN-XiaoxiaoNeural",  "晓晓女声",   "当前默认，温柔但偏 AI 客服感（对照组）"),
]

SAMPLE_TEXT = (
    "嘿，今天聊一件挺猛的事。OpenAI 又发了 GPT-5，我刷了一下发布会，"
    "最大的感受是，这次他们明显在跟编程能力较劲。"
    "Claude 那边也没闲着，4.5 Opus 据说推理速度快了三倍。"
    "咱们做产品的，看着就一句话：又得加班学新工具了。"
)

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR.parent / "05-数据样本" / "voice-samples"


async def synth_one(idx, voice_id, cn_name, desc, max_retries=3):
    out_path = OUT_DIR / (idx + "-" + cn_name + "-" + voice_id + ".mp3")
    print("  [" + idx + "] " + cn_name + "（" + voice_id + "）—— " + desc)

    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            communicate = edge_tts.Communicate(text=SAMPLE_TEXT, voice=voice_id)
            await communicate.save(str(out_path))
            size_kb = out_path.stat().st_size / 1024.0
            if size_kb < 5:
                raise RuntimeError("输出文件太小 " + str(round(size_kb, 1)) + "KB，多半是空音频")
            print("       OK " + out_path.name + "  (" + str(round(size_kb)) + " KB)")
            return
        except Exception as e:
            last_err = e
            print("       第 " + str(attempt) + "/" + str(max_retries) + " 次失败: " + type(e).__name__ + ": " + str(e))
            if attempt < max_retries:
                await asyncio.sleep(2)

    print("       这个声音生成失败，跳过。最后一次错: " + str(last_err))


async def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("")
    print("声音 A/B 试听样本生成中……")
    print("念的稿子（" + str(len(SAMPLE_TEXT)) + " 字，约 15-18 秒）：")
    print("   「" + SAMPLE_TEXT + "」")
    print("")

    for idx, voice_id, cn_name, desc in VOICES:
        await synth_one(idx, voice_id, cn_name, desc)

    print("")
    print("全部生成完毕，去这个文件夹挨个听：")
    print("   " + str(OUT_DIR))
    print("")
    print("听完，把你最喜欢的那个声音的编号或 voice_id 告诉我，")
    print("我帮你写进 .env，正式跑起来。")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("被用户中断。")
        sys.exit(130)

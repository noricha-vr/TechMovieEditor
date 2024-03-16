from moviepy.editor import VideoFileClip, concatenate_videoclips, concatenate_audioclips, CompositeVideoClip
import numpy as np
import os
import sys
import subprocess
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class VideoFormatter:
    def __init__(self, input_path, output_dir, start_time="00:00:00", end_time=None, target_resolution=(1920, 1080), target_fps=30, target_audio_rate=48000):
        self.input_path = input_path
        self.output_dir = output_dir
        self.start_time = start_time
        self.end_time = end_time if end_time else VideoFileClip(
            input_path).duration
        self.target_resolution = target_resolution
        self.target_fps = target_fps
        self.target_audio_rate = target_audio_rate

    def format_video(self):
        input_name, input_ext = os.path.splitext(
            os.path.basename(self.input_path))
        output_path = os.path.join(
            self.output_dir, f"{input_name}_formatted{input_ext}")

        # ffmpegコマンドを構築
        cmd = [
            "ffmpeg",
            "-ss", str(self.start_time),  # 開始時間
            "-to", str(self.end_time),  # 終了時間
            "-i", self.input_path,  # 入力ファイル
            # 解像度の変更
            "-vf", f"scale={self.target_resolution[0]
                            }:{self.target_resolution[1]}",
            "-r", str(self.target_fps),  # フレームレートの設定
            "-ar", str(self.target_audio_rate),  # オーディオサンプルレートの設定
            "-c:a", "aac",  # オーディオコーデックの指定
            "-c:v", "libx264",  # ビデオコーデックの指定
            "-preset", "medium",  # エンコード速度と圧縮率のバランス
            "-crf", "23",  # 品質レベルの設定
            "-movflags", "+faststart",  # ストリーミングの最適化
            "-pix_fmt", "yuv420p",  # ピクセルフォーマットの指定
            "-y",  # 出力ファイルの上書き確認をスキップ
            output_path  # 出力ファイルパス
        ]

        subprocess.run(cmd, check=True)

        return output_path


class SilenceRemover:
    def __init__(self, video_clip, silence_threshold=-50, chunk_size=0.3):
        self.video_clip = video_clip
        self.silence_threshold = silence_threshold
        self.chunk_size = chunk_size

    def remove_silent_parts(self):
        audio = self.video_clip.audio
        audio_chunks = self.make_chunks(audio)
        video_chunks = self.make_chunks(self.video_clip)

        non_silent_indices = []

        for i, chunk in enumerate(audio_chunks):
            max_volume = np.max(chunk.max_volume())
            max_volume_db = 20 * np.log10(max_volume)

            if max_volume_db > self.silence_threshold:
                non_silent_indices.append(i)
                print(f"Chunk {i}: Max volume = {
                      max_volume_db:.2f} dB - Added")
            else:
                print(f"Chunk {i}: Max volume = {
                      max_volume_db:.2f} dB - Skipped")

        for i in range(1, len(non_silent_indices) - 1):
            if non_silent_indices[i] - non_silent_indices[i - 1] > 1 and non_silent_indices[i + 1] - non_silent_indices[i] > 1:
                non_silent_indices.insert(i, non_silent_indices[i] - 1)
                non_silent_indices.insert(i + 2, non_silent_indices[i + 1] + 1)

        non_silent_indices = list(set(non_silent_indices))
        non_silent_indices.sort()

        non_silent_audio = [audio_chunks[i] for i in non_silent_indices]
        non_silent_video = [video_chunks[i] for i in non_silent_indices]

        final_audio = concatenate_audioclips(non_silent_audio)
        final_video = concatenate_videoclips(non_silent_video)
        final_video.audio = final_audio

        return final_video

    def make_chunks(self, clip):
        num_chunks = int(clip.duration // self.chunk_size) + 1
        return [clip.subclip(i * self.chunk_size, min((i + 1) * self.chunk_size, clip.duration)) for i in range(num_chunks)]


class CrossfadeTransition:
    @staticmethod
    def create_crossfade_transition(clip_start, clip_end, duration):
        clip_start_fade = clip_start.crossfadeout(duration)
        clip_end_fade = clip_end.crossfadein(
            duration).set_start(clip_start.duration - duration)
        return CompositeVideoClip([clip_start_fade, clip_end_fade])

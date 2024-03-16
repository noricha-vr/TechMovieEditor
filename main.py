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

        cmd = [
            "ffmpeg",
            "-ss", str(self.start_time),
            "-to", str(self.end_time),
            "-i", self.input_path,
            "-vf", f"scale={self.target_resolution[0]
                            }:{self.target_resolution[1]}",
            "-r", str(self.target_fps),
            "-ar", str(self.target_audio_rate),
            "-c:a", "aac",
            "-c:v", "libx264",
            "-y",
            output_path
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


if __name__ == "__main__":
    args = sys.argv[1:]

    event_name = args[0] if len(args) > 0 else 'kojin'
    input_video = args[1] if len(args) > 1 else 'input/sample.mp4'
    start_time = args[2] if len(args) > 2 else "00:00:00"
    end_time = args[3] if len(args) > 3 else None

    logging.info(f'event_name: {event_name}')
    logging.info(f'input_video: {input_video}')
    logging.info(f'start_time: {start_time}')
    logging.info(f'end_time: {end_time}')

    now = datetime.now().strftime('%Y%m%d-%H%M%S')
    opening_video = f"input/{event_name}/opening.mp4"
    ending_video = f"input/{event_name}/ending.mp4"
    output_video = f"output/{event_name}_{now}.mp4"
    tmp_dir = "tmp"
    silence_threshold = -45
    chunk_size = 0.3
    crossfade_duration = 1
    target_resolution = (1280, 720)
    target_fps = 30
    target_audio_rate = 48000

    input_formatter = VideoFormatter(
        input_video, tmp_dir, start_time, end_time, target_resolution, target_fps, target_audio_rate)
    formatted_input_video = input_formatter.format_video()

    opening_formatter = VideoFormatter(opening_video, tmp_dir, target_resolution=target_resolution,
                                       target_fps=target_fps, target_audio_rate=target_audio_rate)
    formatted_opening_video = opening_formatter.format_video()

    ending_formatter = VideoFormatter(ending_video, tmp_dir, target_resolution=target_resolution,
                                      target_fps=target_fps, target_audio_rate=target_audio_rate)
    formatted_ending_video = ending_formatter.format_video()

    main_video = VideoFileClip(formatted_input_video)
    opening = VideoFileClip(formatted_opening_video)
    ending = VideoFileClip(formatted_ending_video)

    silence_remover = SilenceRemover(main_video, silence_threshold, chunk_size)
    final_main_video = silence_remover.remove_silent_parts()

    opening_main = CrossfadeTransition.create_crossfade_transition(
        opening, final_main_video.subclip(0, crossfade_duration), crossfade_duration)

    main_ending = CrossfadeTransition.create_crossfade_transition(final_main_video.subclip(
        final_main_video.duration - crossfade_duration), ending, crossfade_duration)

    main_video_without_crossfade = final_main_video.subclip(
        crossfade_duration, final_main_video.duration - crossfade_duration)
    final_video = concatenate_videoclips(
        [opening_main, main_video_without_crossfade, main_ending]).set_fps(24000/1001)
    final_video.write_videofile(
        output_video, codec="libx264", audio_codec="aac")

from moviepy.editor import VideoFileClip, concatenate_videoclips, concatenate_audioclips, CompositeVideoClip
import numpy as np
import os
import subprocess


def format_video(input_path, output_dir, start_time="00:00:00", end_time=None, target_resolution=(1920, 1080), target_fps=30, target_audio_rate=48000):
    if end_time is None:
        # 動画の長さを取得
        end_time = VideoFileClip(input_path).duration
    # 入力ファイルの情報を取得
    input_name, input_ext = os.path.splitext(os.path.basename(input_path))
    output_path = os.path.join(
        output_dir, f"{input_name}_formatted{input_ext}")

    # ffmpegコマンドを構築
    cmd = [
        "ffmpeg",
        "-ss", str(start_time),  # 動画の開始時間を設定
        "-to", str(end_time),  # 動画の終了時間を設定
        "-i", input_path,
        "-vf", f"scale={target_resolution[0]}:{target_resolution[1]}",
        "-r", str(target_fps),
        "-ar", str(target_audio_rate),
        "-c:a", "aac",
        "-c:v", "libx264",
        "-y",
        output_path
    ]

    # ffmpegコマンドを実行
    subprocess.run(cmd, check=True)

    return output_path


def remove_silent_parts(video_clip, silence_threshold=-50, chunk_size=0.1):
    audio = video_clip.audio
    audio_chunks = make_chunks(audio, chunk_size)
    video_chunks = make_chunks(video_clip, chunk_size)

    non_silent_indices = []

    for i, chunk in enumerate(audio_chunks):
        max_volume = np.max(chunk.max_volume())
        max_volume_db = 20 * np.log10(max_volume)  # Convert to decibel scale

        if max_volume_db > silence_threshold:
            non_silent_indices.append(i)
            print(f"Chunk {i}: Max volume = {max_volume_db:.2f} dB - Added")
        else:
            print(f"Chunk {i}: Max volume = {
                max_volume_db:.2f} dB - Skipped")

    # added の前後のskip は added に置き換える
    for i in range(1, len(non_silent_indices)-1):
        if non_silent_indices[i] - non_silent_indices[i-1] > 1 and non_silent_indices[i+1] - non_silent_indices[i] > 1:
            non_silent_indices.insert(i, non_silent_indices[i]-1)
            non_silent_indices.insert(i+2, non_silent_indices[i+1]+1)

    non_silent_indices = list(set(non_silent_indices))
    non_silent_indices.sort()

    non_silent_audio = [audio_chunks[i] for i in non_silent_indices]
    non_silent_video = [video_chunks[i] for i in non_silent_indices]

    final_audio = concatenate_audioclips(non_silent_audio)
    final_video = concatenate_videoclips(non_silent_video)
    final_video.audio = final_audio  # Set the audio of the final video

    return final_video


def make_chunks(clip, chunk_size):
    num_chunks = int(clip.duration // chunk_size) + 1
    return [clip.subclip(i * chunk_size, min((i + 1) * chunk_size, clip.duration)) for i in range(num_chunks)]


def crossfade(clip1, clip2, duration):
    clip1_fade = clip1.crossfadein(duration)
    clip2_fade = clip2.crossfadeout(duration)
    return CompositeVideoClip([clip1_fade, clip2_fade.set_start(clip1.duration - duration)])


if __name__ == "__main__":
    start_time = "00:00:30"
    end_time = "00:01:00"
    event_name = 'kojin'
    input_video = "input/sample.mp4"
    opening_video = f"input/{event_name}/opening.mp4"
    ending_video = f"input/{event_name}/ending.mp4"
    output_video = "output/sample.mp4"
    silence_threshold = -40  # 無音とみなす音量のしきい値（dB）
    chunk_size = 0.2  # 動画をチャンクに分割するサイズ（秒）
    crossfade_duration = 1  # クロスディゾルブの時間（秒）
    target_resolution = (1920, 1080)  # 解像度
    target_fps = 30  # fps
    target_audio_rate = 48000  # サンプリング周波数
    tmp_dir = "tmp"
    # 動画をフォーマット
    formatted_input_video = format_video(
        input_video, tmp_dir, start_time, end_time, target_resolution, target_fps, target_audio_rate)
    formatted_opening_video = format_video(
        opening_video, tmp_dir, target_resolution=target_resolution, target_fps=target_fps, target_audio_rate=target_audio_rate)
    formatted_ending_video = format_video(
        ending_video, tmp_dir, target_resolution=target_resolution, target_fps=target_fps, target_audio_rate=target_audio_rate)

    main_video = VideoFileClip(formatted_input_video)
    opening = VideoFileClip(formatted_opening_video)
    ending = VideoFileClip(formatted_ending_video)

    final_main_video = remove_silent_parts(
        main_video, silence_threshold, chunk_size)

    # openingとmain_videoのクロスディゾルブ
    opening_crossfade = opening.crossfadeout(crossfade_duration)
    main_video_crossfade = final_main_video.crossfadein(crossfade_duration)
    main_video_crossfade = main_video_crossfade.set_start(
        opening.duration - crossfade_duration)
    opening_main = CompositeVideoClip(
        [opening_crossfade, main_video_crossfade])

    # main_videoとendingのクロスディゾルブ
    main_video_crossfade_out = final_main_video.crossfadeout(
        crossfade_duration)
    ending_crossfade = ending.crossfadein(crossfade_duration)
    ending_crossfade = ending_crossfade.set_start(
        final_main_video.duration - crossfade_duration)
    main_ending = CompositeVideoClip(
        [main_video_crossfade_out, ending_crossfade])

    # 動画を結合して書き出し
    final_video = concatenate_videoclips(
        [opening_main, main_ending]).set_fps(24000/1001)
    final_video.write_videofile(
        output_video, codec="libx264", audio_codec="aac")

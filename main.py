from moviepy.editor import VideoFileClip, concatenate_videoclips, concatenate_audioclips
import numpy as np


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


if __name__ == "__main__":
    input_video = "input/sample.mp4"
    output_video = "output/sample.mp4"
    silence_threshold = -35  # 無音とみなす音量のしきい値（dB）
    chunk_size = 0.2  # 動画をチャンクに分割するサイズ（秒）

    video = VideoFileClip(input_video)
    final_video = remove_silent_parts(video, silence_threshold, chunk_size)
    final_video.write_videofile(
        output_video, codec="libx264", audio_codec="aac")

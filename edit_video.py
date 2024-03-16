from moviepy.editor import VideoFileClip, concatenate_videoclips, concatenate_audioclips, CompositeVideoClip
import sys
import logging
from datetime import datetime
from video_editor import VideoFileClip, SilenceRemover, CrossfadeTransition, VideoFormatter
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


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
    # target_resolution = (720,480) # debug
    target_resolution = (1920, 1080)
    target_fps = 60
    target_audio_rate = 48000
    is_monaural = True

    # 入力動画をフォーマットする
    input_formatter = VideoFormatter(
        input_video, tmp_dir,  target_resolution, target_fps, target_audio_rate, start_time, end_time, is_monaural)
    formatted_input_video = input_formatter.format_video()

    # オープニング動画をフォーマットする
    opening_formatter = VideoFormatter(
        opening_video, tmp_dir, target_resolution, target_fps, target_audio_rate)
    formatted_opening_video = opening_formatter.format_video()

    # エンディング動画をフォーマットする
    ending_formatter = VideoFormatter(
        ending_video, tmp_dir, target_resolution, target_fps, target_audio_rate)
    formatted_ending_video = ending_formatter.format_video()

    # フォーマットされた動画を読み込む
    main_video = VideoFileClip(formatted_input_video)
    opening = VideoFileClip(formatted_opening_video)
    ending = VideoFileClip(formatted_ending_video)

    # 無音部分を削除する
    silence_remover = SilenceRemover(main_video, silence_threshold, chunk_size)
    final_main_video = silence_remover.remove_silent_parts()

    # オープニングとメイン動画のクロスフェードを作成する
    opening_main = CrossfadeTransition.create_crossfade_transition(
        opening, final_main_video.subclip(0, crossfade_duration), crossfade_duration)

    # メイン動画とエンディングのクロスフェードを作成する
    main_ending = CrossfadeTransition.create_crossfade_transition(final_main_video.subclip(
        final_main_video.duration - crossfade_duration), ending, crossfade_duration)

    # クロスフェードを除いたメイン動画の部分を取得する
    main_video_without_crossfade = final_main_video.subclip(
        crossfade_duration, final_main_video.duration - crossfade_duration)
    # 最終的な動画を結合する
    final_video = concatenate_videoclips(
        [opening_main, main_video_without_crossfade, main_ending]).set_fps(24000/1001)
    # 動画をファイルに書き出す
    final_video.write_videofile(
        output_video,
        codec="libx264",
        audio_codec="aac",
        fps=60
    )

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

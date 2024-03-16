from moviepy.editor import VideoFileClip
# 仮にSilenceRemoverクラスが別ファイルに定義されているとします
from video_editor import SilenceRemover
import sys
import os

if __name__ == "__main__":
    args = sys.argv
    if len(sys.argv) != 2:
        print("使用法: python remove_silence.py 入力動画パス")
        sys.exit(1)
    silence_threshold = -45
    chunk_size = 0.3
    input_video_path = args[1] if len(args) > 1 else 'input/sample.mp4'
    file_name = os.path.basename(input_video_path)
    # 出力ファイルパスを設定（'output'フォルダー内に同じファイル名で）
    output_video_path = os.path.join('output', file_name)
    video_clip = VideoFileClip(input_video_path)

    # SilenceRemover インスタンスを作成
    silence_remover = SilenceRemover(video_clip, silence_threshold, chunk_size)

    # 無音部分を削除
    processed_video = silence_remover.remove_silent_parts()

    # 処理後の動画を保存
    processed_video.write_videofile(
        output_video_path, codec="libx264", audio_codec="aac")

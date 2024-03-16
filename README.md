
# Tech Movie Editor

## 概要

このプロジェクトは技術系VRChatイベントで撮影した動画を編集するためのツールです

オープニングとエンディングを含む動画を作る機能と、動画の無音部分だけをカットした動画を作る機能があります

## セットアップ方法

このプロジェクトを使用するためのセットアップ手順は以下の通りです

1. このリポジトリをクローンします

```bash
git clone git@github.com:noricha-vr/TechMovieEditor.git
```

2. クローンしたディレクトリに移動します

```bash
cd TechMovieEditor
```

3. 必要な依存関係をインストールします

```bash
pip install -r requirements.txt
```

これでセットアップは完了です👏

## 機能と使い方

### オープニングとエンディングが付いた動画作成

```bash
python edit_video.py EVENT_NAME VIDEO_PATH START_TIME END_TIME
```

- EVENT_NAME: イベント名 [kojin, ds, ml, etc...] (kojinのみ実装済み )
- VIDEO_PATH: 動画のパス
- START_TIME: トリミングの開始位置（00:00:00） (オプション)
- END_TIME: トリミングの終了位置（00:00:00） (オプション)

**例**

```bash
# 動画をそのまま使うとき
python edit_video.py kojin input/sample.mp4

# 動画のトリミングするとき
python edit_video.py kojin input/sample.mp4 00:00:30 00:01:00
```

1. 動画をフォーマット（1920x1080、60fps、モノラル）でtmpフォルダーに書き出し
1. オープニングとエンディングをクロスディゾルブを設定して結合
1. outputフォルダーに書き出し

#### イベントの追加方法

イベント名のフォルダーにオープニングとエンディングの動画を配置してください

- input/EVENT_NAME/ending.mp4
- input/EVENT_NAME/opening.mp4

### 動画の無音部分だけをカットした動画を作る

```bash
python remove_silence.py VIDEO_PATH
```

- VIDEO_PATH: 動画のパス

**例**

```bash
python remove_silence.py input/sample.mp4
```

※ カットだけを行い、フォーマットはしません

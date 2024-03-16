
# Tech Movie Editor

## 概要

このプロジェクトは技術系VRChatイベントで撮影した動画を編集するためのツールです。

### 機能

- 動画のトリミング（開始位置、終了位置を入力）
- 無音部分をカット（しきい値と長さを入力）
- オープニングとエンディングを追加(動画のパスを入力)

## セットアップ方法

このプロジェクトを使用するためのセットアップ手順は以下の通りです。

1. このリポジトリをクローンします。

```bash
git clone git@github.com:noricha-vr/TechMovieEditor.git
```

2. クローンしたディレクトリに移動します。

```bash
cd TechMovieEditor
```

3. 必要な依存関係をインストールします。

```bash
pip install -r requirements.txt
```

これでセットアップは完了です👏

## 使い方

### オープニングとエンディングが付いた動画を作る

- EVENT_NAME: イベント名 [kojin, ds, ml, etc...] (kojinのみ実装済み )
- INPUT_VIDEO: 動画のパス
- START_TIME: トリミングの開始位置（00:00:00） (オプション)
- END_TIME: トリミングの終了位置（00:00:00） (オプション)

```bash
python edit_video.py EVENT_NAME VIDEO_PATH START_TIME END_TIME
```

**例**

```bash
# 動画をそのまま使うとき
python edit_video.py kojin input/sample.mp4

# 動画のトリミングするとき
python edit_video.py kojin input/sample.mp4 00:00:30 00:01:00
```

#### イベントの追加方法

イベント名のフォルダーにオープニングとエンディングの動画を配置してください。

- input/EVENT_NAME/ending.mp4
- input/EVENT_NAME/opening.mp4

### 動画の無音部分だけをカットした動画を作る

```bash
python remove_silence.py VIDEO_PATH
```

```bash
python remove_silence.py input/sample.mp4
```

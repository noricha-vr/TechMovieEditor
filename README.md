
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

これでセットアップは完了です。

## 使い方

- EVENT_NAME: イベント名 [kojin, ds, ml, etc...] （未実装）
- INPUT_VIDEO: 編集対象の動画のパス （未実装）
- START_TIME: トリミングの開始位置（秒） (オプション)（未実装）
- END_TIME: トリミングの終了位置（秒） (オプション)（未実装）

```bash
python main.py EVENT_NAME INPUT_VIDEO START_TIME END_TIM
```

# create-subtitles-movie.sh

[SubRip形式](https://ja.wikipedia.org/wiki/SubRip)の字幕ファイルからBlenderで字幕アニメーションを作成します

## 使い方

`create-subtitles-movie.sh`の引数にSubRip形式を指定して呼び出します。

Blenderが起動し、字幕ファイルをもとに作成された字幕アニメーションのプロジェクトを表示します。

### 使用例

~~~shell
~/bin/create-subtitles-movie.sh -s 25 -r 60 -g ./sample_srt/50on.srt
~~~

### ヘルプ

~~~shell
~/bin/create-subtitles-movie.sh -h
usage: create-subtitles-movie.py [-h] [-s MOVIE_SEC] [-r FRAME_RATE] [-c TEXT_COLOR] [-f VORTEX_FORCE] [-w] [-p RESOLUTION_PERCENTAGE] [-x INITIAL_LOC_X] [-y INITIAL_LOC_Y] [-z INITIAL_LOC_Z] [-g] SRT_FILE

指定された字幕ファイルの内容をムービーに変換する

positional arguments:
  SRT_FILE              SubRip形式の字幕ファイルのパス

options:
  -h, --help            show this help message and exit
  -s MOVIE_SEC, --sec MOVIE_SEC
                        作成するムービーの長さ(秒). デフォルト値: 60
  -r FRAME_RATE, --fps FRAME_RATE
                        フレームレート(fps). デフォルト値: 60
  -c TEXT_COLOR, --color TEXT_COLOR
                        デフォルトの文字色. デフォルト値: #D10806
  -f VORTEX_FORCE, --force VORTEX_FORCE
                        渦の強さ. デフォルト値: 1.0
  -w, --wall            部屋の壁を表示する. デフォルト値: False
  -p RESOLUTION_PERCENTAGE, --percentage RESOLUTION_PERCENTAGE
                        解像度のパーセンテージ. デフォルト値: 100
  -x INITIAL_LOC_X, --locx INITIAL_LOC_X
                        テキストのX座標の表示位置. デフォルト値: 0
  -y INITIAL_LOC_Y, --locy INITIAL_LOC_Y
                        テキストのY座標の表示位置. デフォルト値: 0
  -z INITIAL_LOC_Z, --locz INITIAL_LOC_Z
                        テキストのZ座標の表示位置. デフォルト値: 0
  -g, --greenback       グリーンバックを使用する. デフォルト値: False
~~~

## インストール方法

`Makefile`にインストール先ディレクトリと、`Blender`コマンドのパスが変数に定義されています。
環境に合せて以下の変数を修正し、

~~~Makefile
# 環境に合せてインストール先とBlenderコマンドを変更してください
DST_BIN=${HOME}/bin
DST_DIR=${HOME}/opt/create-subtitles-movie
BLENDER_COMMAND=/Applications/Blender.app/Contents/MacOS/Blender
FONT_PATH=~/Library/Fonts/BIZUDGothic-Bold.ttf
~~~

以下のコマンドでインストールできます。
デフォルトでは、`~/bin`に`create-subtitles-movie.sh`がインストールされます。
なお、`~/bin/create-subtitles-movie.sh`は、`~/opt/bin/create-subtitles-movie.sh`のシンボリックリンクになります。

~~~shell
make install
~~~

また、以下でインストールしたスクリプトを削除できます。

~~~shell
make clean
~~~

### インストールディレクトリ

`Makefile`で指定した`DST_DIR`配下に以下のディレクトリが作成されます

~~~shell
% tree -I __pycache__ ~/opt/create-subtitles-movie
~/opt/create-subtitles-movie
├── bin
│   └── create-subtitles-movie.sh
├── etc
│   └── config.py
├── lib
│   ├── create-subtitles-movie.py
│   ├── my_blender.py
│   └── my_srt.py
└── share
    └── assets
        ├── camera_and_lights.blend
        └── room.blend
~~~

### デフォルト設定

`${DST_DIR}/etc/config.py`がデフォルトの設定です。

~~~python
output = dict(
    # 出力動画の長さ(sec)
    movie_sec=60,
    # 出力動画のフレームレート(fps)
    frame_rate=60,
    # 解像度のパーセンテージ
    resolution_percentage=100,
)
assets = dict(
    # アセットのディレクトリ
    parts_dir="~/opt/create-subtitles-movie/share/assets",
)
text = dict(
    # テキストのデフォルト色
    color="#D10806",
    # テキストの初期位置
    initial_location=[0, 0, 2],
    # フォント
    font_path="~/Library/Fonts/BIZUDGothic-Bold.ttf"
)
vortex = dict(
    # 渦の強さ
    strength=1.0,
)
room = dict(
    # 実験ルームの正面以外の壁を表示する
    show_wall=False
)
world = dict(
    # ワールドをグリーンバックにする
    use_green_screen=False
)
~~~

### アセット

`${DST_DIR}/share/assets`に、実験ルームと、実験ルーム用のライトとカメラがあります。
各Blendファイルは、`Blender v3.3.1`で作成したものになります。


## 字幕ファイルの拡張

[SubRip形式](https://ja.wikipedia.org/wiki/SubRip)の1レコードは、通常以下の形式となります。

1. レコード番号
2. 字幕の表示開始、終了時間行
3. 字幕(複数行可)
4. 空行(次のレコードとの区切り)

~~~text
1
00:00:03,0 --> 00:00:25,0
アメンボ赤いな

~~~

本ツールでは、`字幕の表示開始、終了時間行`の行末に、
`空白`とともに`JSON: `ラベルを記載すれば、`JSONデータ`を記載できます。

~~~text
1
00:00:03,0 --> 00:00:25,0 JSON: { "location": [0, -1.5, 0], "color": "#cf9696", "strength": 0.8 }
アメンボ赤いな

~~~

本ツールで対応している`JSONデータ`は以下になります。

|項目|説明|
|----|----|
|location|字幕の初期表示時の位置 [x,y,z]|
|color|字幕のテキスト色 #ではじまる16進数色|
|strength|Vortexの強さ 表示開始時間にVortexの強さを指定値に変更する|

# create-subtitles-movie.sh

[SubRip形式](https://ja.wikipedia.org/wiki/SubRip)の字幕ファイルからBlenderで字幕アニメーションを作成する

## 使い方

Blenderコマンドの`-P`オプションとともに `create-subtitles-movie.py` を呼びだす。
`create-subtitles-movie.py`に引き渡す引数は、`--`以降に記載する。

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
DST_BIN=${HOME}/bin
DST_DIR=${HOME}/opt/create-subtitles-movie
BLENDER_COMMAND=/Applications/Blender.app/Contents/MacOS/Blender
~~~

以下のコマンドでインストールできます。
デフォルトでは、`~/bin`に`create-subtitles-movie.sh`がインストールされます。

~~~shell
make install
~~~

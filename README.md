# create-subtitles-movie.py

[SubRip形式](https://ja.wikipedia.org/wiki/SubRip)の字幕ファイルからBlenderで字幕アニメーションを作成する

## 使い方

Blenderコマンドの`-P`オプションとともに `create-subtitles-movie.py` を呼びだす。
`create-subtitles-movie.py`に引き渡す引数は、`--`以降に記載する。


~~~shell
/Applications/Blender.app/Contents/MacOS/Blender -P ./create-subtitles-movie.py -- -h
usage: create-subtitles-movie.py [-h] [-s MOVIE_SEC] [-r FRAME_RATE] SRT_FILE

指定された字幕ファイルの内容をムービーに変換する

positional arguments:
  SRT_FILE              SubRip形式の字幕ファイルのパス

options:
  -h, --help            show this help message and exit
  -s MOVIE_SEC, --sec MOVIE_SEC
                        作成するムービーの長さ(秒). デフォルト値: 60
  -r FRAME_RATE, --fps FRAME_RATE
                        フレームレート(fps). デフォルト値: 30
~~~

### 使用例

~~~shell
/Applications/Blender.app/Contents/MacOS/Blender -P ./create-subtitles-movie.py -- ./50on.srt -s 25 -r 60
~~~

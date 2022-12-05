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
    parts_dir="../share/assets",
)
text = dict(
    # テキストのデフォルト色
    color="#D10806",
    # テキストの初期位置
    initial_location=[0, 0, 0],
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

import bpy
import sys
import os
import argparse

if __name__ == "__main__":
    print("hello!!")

    MOVIE_SEC = 60
    FRAME_RATE = 60
    PARTS_DIR = "~/spike/45_sagyoudai/parts"
    TEXT_COLOR = "#D10806"
    VORTEX_FORCE = 1.0
    RESOLUTION_PERCENTAGE = 100
    INITIAL_LOC_X = 0
    INITIAL_LOC_Y = 0
    INITIAL_LOC_Z = 0

    # 引数の解析
    script_args = []
    if "--" in sys.argv:
        script_args = sys.argv[sys.argv.index("--")+1:]
    print(script_args)

    parser = argparse.ArgumentParser(prog='create-subtitles-movie.py', description='指定された字幕ファイルの内容をムービーに変換する')
    parser.add_argument('srtfile', metavar='SRT_FILE', type=str, help="SubRip形式の字幕ファイルのパス")
    parser.add_argument('-s', '--sec', metavar='MOVIE_SEC', type=int, default=MOVIE_SEC,
                        help=f"作成するムービーの長さ(秒). デフォルト値: {MOVIE_SEC}")
    parser.add_argument('-r', '--fps', metavar='FRAME_RATE', type=int, default=FRAME_RATE,
                        help=f"フレームレート(fps). デフォルト値: {FRAME_RATE}")
    parser.add_argument('-c', '--color', metavar='TEXT_COLOR', type=str, default=TEXT_COLOR,
                        help=f"デフォルトの文字色. デフォルト値: {TEXT_COLOR}")
    parser.add_argument('-f', '--force', metavar='VORTEX_FORCE', type=float, default=VORTEX_FORCE,
                        help=f"渦の強さ. デフォルト値: {VORTEX_FORCE}")
    parser.add_argument('-w', '--wall', action='store_true', default=False,
                        help=f"部屋の壁を表示する. デフォルト値: {False}")
    parser.add_argument('-p', '--percentage', metavar='RESOLUTION_PERCENTAGE', type=int, default=RESOLUTION_PERCENTAGE,
                        help=f"解像度のパーセンテージ. デフォルト値: {RESOLUTION_PERCENTAGE}")
    parser.add_argument('-x', '--locx', metavar='INITIAL_LOC_X', type=float, default=INITIAL_LOC_X,
                        help=f"テキストのX座標の表示位置. デフォルト値: {INITIAL_LOC_X}")
    parser.add_argument('-y', '--locy', metavar='INITIAL_LOC_Y', type=float, default=INITIAL_LOC_Y,
                        help=f"テキストのY座標の表示位置. デフォルト値: {INITIAL_LOC_Y}")
    parser.add_argument('-z', '--locz', metavar='INITIAL_LOC_Z', type=float, default=INITIAL_LOC_Z,
                        help=f"テキストのZ座標の表示位置. デフォルト値: {INITIAL_LOC_Z}")
    parser.add_argument('-g', '--greenback', action='store_true', default=False,
                        help=f"グリーンバックを使用する. デフォルト値: {False}")

    args = parser.parse_args(script_args)
    print(args)

    # モジュールのパス追加
    module_dir = os.path.dirname(__file__)
    sys.path += [module_dir]

    import my_blender
    import my_srt

    # 最初の手順
    my_blender.initailize_blender()

    # 出力の設定
    my_blender.setup_output(args.fps, args.sec, args.percentage)

    # Rigid Body Worldの設定
    my_blender.setup_rigid_body_world(args.sec)

    # roomを追加
    my_blender.append_collection(os.path.expanduser(os.path.join(PARTS_DIR, "room.blend")), "room")

    # 壁を非表示に
    hidden_walls = ["f_wall"]
    if not args.wall:
        hidden_walls = ["f_wall", "b_wall", "l_wall", "r_wall", "floor", "ceil"]

    for w in hidden_walls:
        bpy.context.scene.objects[w].hide_viewport = True
        bpy.context.scene.objects[w].hide_render = True

    # 既存のカメラとライトを削除する
    for obj in [o for o in bpy.data.objects if o.name in ['Camera', 'Light']]:
        bpy.data.objects.remove(obj)
    # 実験ルーム用のカメラとライトを配置する
    my_blender.append_collection(os.path.expanduser(os.path.join(PARTS_DIR, "camera_and_lights.blend")),
                                 "camera_and_lights")

    # 渦追加
    force = my_blender.add_vortex(args.force)

    # 赤色のマテリアル
    material_dict = {}
    material_dict['default'] = my_blender.create_material('red_text', my_srt.hex_to_rgba(args.color))

    # フォント
    FONT_PATH = os.path.expanduser("~/Library/Fonts/BIZUDGothic-Bold.ttf")
    font = bpy.data.fonts.load(FONT_PATH)

    item_list = my_srt.read_srt_file(args.srtfile)
    for idx, item in enumerate(item_list):
        extra_info = item['time_info'].get('json', {})

        materail_name = extra_info.get('color', 'default')
        if materail_name not in material_dict.keys():
            color = my_srt.hex_to_rgba(materail_name)
            material_dict[materail_name] = my_blender.create_material(materail_name, color)

        # テキスト追加
        txt = "\n".join(item['lines'])
        txt_obj = my_blender.add_text(txt, 1.5, 0.2, font, material_dict[materail_name])
        txt_obj = my_blender.convert_to_mesh(txt_obj)
        # 中心に移動
        loc = extra_info.get('location', [args.locx, args.locy, args.locz])
        txt_obj.location = loc

        # rigid body追加
        my_blender.add_to_rigid_body(txt_obj)
        # アニメーション追加
        start_sec = item['time_info']['start'].total_seconds()
        end_sec = item['time_info']['end'].total_seconds()
        my_blender.animate_obj(txt_obj, start_sec, end_sec)

        if "strength" in extra_info.keys():
            my_blender.animate_force(force, start_sec, extra_info['strength'])

    # グリーンバック
    if args.greenback:
        my_blender.setup_greenback_worlds()

    # 3Dビューポートの初期化
    my_blender.initialize_3dviewport()

    # with bpy.context.temp_override(point_cache=bpy.context.scene.rigidbody_world.point_cache):
    #     bpy.ops.ptcache.bake(bake=True)

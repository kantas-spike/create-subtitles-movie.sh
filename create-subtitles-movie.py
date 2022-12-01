import bpy
import sys
import os
import argparse

if __name__ == "__main__":
    print("hello!!")

    MOVIE_SEC = 60
    FRAME_RATE = 30
    PARTS_DIR = "~/spike/45_sagyoudai/parts"

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
    my_blender.setup_output(args.fps, args.sec)

    # Rigid Body Worldの設定
    my_blender.setup_rigid_body_world(args.sec)

    # roomを追加
    my_blender.append_collection(os.path.expanduser(os.path.join(PARTS_DIR, "room.blend")), "room")
    # 正面の壁を非表示に
    bpy.context.scene.objects["f_wall"].hide_viewport = True
    bpy.context.scene.objects["f_wall"].hide_render = True

    # 既存のカメラとライトを削除する
    for obj in [o for o in bpy.data.objects if o.name in ['Camera', 'Light']]:
        bpy.data.objects.remove(obj)
    # 実験ルーム用のカメラとライトを配置する
    my_blender.append_collection(os.path.expanduser(os.path.join(PARTS_DIR, "camera_and_lights.blend")),
                                 "camera_and_lights")

    # 渦追加
    my_blender.add_vortex(1.0)

    # 赤色のマテリアル
    material = my_blender.create_material('red_text', (1, 0, 0, 1))

    # フォント
    FONT_PATH = os.path.expanduser("~/Library/Fonts/BIZUDGothic-Bold.ttf")
    font = bpy.data.fonts.load(FONT_PATH)

    item_list = my_srt.read_srt_file(args.srtfile)
    for idx, item in enumerate(item_list):
        # print(item)
        # テキスト追加
        txt = "\n".join(item['lines'])
        txt_obj = my_blender.add_text(txt, 1.5, 0.2, font, material)
        txt_obj = my_blender.convert_to_mesh(txt_obj)
        # 中心に移動
        if idx == 0:
            txt_obj.location = (0, -1, 0)  # 最初は渦の力が弱いので前にすすめておく
        else:
            txt_obj.location = (0, 0, 0)
        # rigid body追加
        my_blender.add_to_rigid_body(txt_obj)
        # アニメーション追加
        start_sec = item['time_info'][0].total_seconds()
        end_sec = item['time_info'][1].total_seconds()
        my_blender.animate_obj(txt_obj, start_sec, end_sec)

    # 3Dビューポートの初期化
    my_blender.initialize_3dviewport()

    # with bpy.context.temp_override(point_cache=bpy.context.scene.rigidbody_world.point_cache):
    #     bpy.ops.ptcache.bake(bake=True)

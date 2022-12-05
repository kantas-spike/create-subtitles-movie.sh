import bpy
import sys
import os
import argparse
import pprint


def print_config(config, name=None):
    label = "config"
    if name:
        label = name

    print(f"{label}: {{")
    for a in [a for a in dir(config) if not a.startswith("__")]:
        print(f"  {a}:", pprint.pformat(getattr(config, a)))
    print("}\n")


def update_config(config, args):
    print_config(config, "etc/config.py")

    # 出力設定
    config.output["movie_sec"] = args.sec
    config.output["frame_rate"] = args.fps
    config.output["resolution_percentage"] = args.percentage

    # 色
    config.text["color"] = args.color
    config.text["initial_location"][0] = args.locx
    config.text["initial_location"][1] = args.locy
    config.text["initial_location"][2] = args.locz

    # 渦
    config.vortex["strength"] = args.force

    # その他
    config.room["show_wall"] = args.wall
    config.world["use_green_screen"] = args.greenback

    print("args: ", pprint.pformat(args))
    print_config(config, "merged config")


if __name__ == "__main__":
    # モジュールのパス追加
    module_dir = os.path.dirname(__file__)
    etc_dir = os.path.abspath(os.path.join(module_dir, "../etc"))
    sys.path += [module_dir, etc_dir]
    import config

    # 引数の解析
    script_args = []
    if "--" in sys.argv:
        script_args = sys.argv[sys.argv.index("--") + 1 :]

    parser = argparse.ArgumentParser(prog="create-subtitles-movie.py", description="指定された字幕ファイルの内容をムービーに変換する")
    parser.add_argument("srtfile", metavar="SRT_FILE", type=str, help="SubRip形式の字幕ファイルのパス")
    parser.add_argument(
        "-s",
        "--sec",
        metavar="MOVIE_SEC",
        type=int,
        default=config.output["movie_sec"],
        help=f"作成するムービーの長さ(秒). デフォルト値: {config.output['movie_sec']}",
    )
    parser.add_argument(
        "-r",
        "--fps",
        metavar="FRAME_RATE",
        type=int,
        default=config.output["frame_rate"],
        help=f"フレームレート(fps). デフォルト値: {config.output['frame_rate']}",
    )
    parser.add_argument(
        "-p",
        "--percentage",
        metavar="RESOLUTION_PERCENTAGE",
        type=int,
        default=config.output["resolution_percentage"],
        help=f"解像度のパーセンテージ. デフォルト値: {config.output['resolution_percentage']}",
    )
    parser.add_argument(
        "-c",
        "--color",
        metavar="TEXT_COLOR",
        type=str,
        default=config.text["color"],
        help=f"デフォルトの文字色. デフォルト値: {config.text['color']}",
    )
    parser.add_argument(
        "-x",
        "--locx",
        metavar="INITIAL_LOC_X",
        type=float,
        default=config.text["initial_location"][0],
        help=f"テキストのX座標の表示位置. デフォルト値: {config.text['initial_location'][0]}",
    )
    parser.add_argument(
        "-y",
        "--locy",
        metavar="INITIAL_LOC_Y",
        type=float,
        default=config.text["initial_location"][1],
        help=f"テキストのY座標の表示位置. デフォルト値: {config.text['initial_location'][1]}",
    )
    parser.add_argument(
        "-z",
        "--locz",
        metavar="INITIAL_LOC_Z",
        type=float,
        default=config.text["initial_location"][2],
        help=f"テキストのZ座標の表示位置. デフォルト値: {config.text['initial_location'][2]}",
    )
    parser.add_argument(
        "-f",
        "--force",
        metavar="VORTEX_FORCE",
        type=float,
        default=config.vortex["strength"],
        help=f"渦の強さ. デフォルト値: {config.vortex['strength']}",
    )
    parser.add_argument(
        "-w",
        "--wall",
        action="store_true",
        default=config.room["show_wall"],
        help=f"部屋の壁を表示する. デフォルト値: {config.room['show_wall']}",
    )
    parser.add_argument(
        "-g",
        "--greenback",
        action="store_true",
        default=config.world["use_green_screen"],
        help=f"グリーンバックを使用する. デフォルト値: {config.world['use_green_screen']}",
    )

    args = parser.parse_args(script_args)
    update_config(config, args)

    import my_blender
    import my_srt

    # 最初の手順
    my_blender.initailize_blender()

    # 出力の設定
    my_blender.setup_output(config.output)

    # Rigid Body Worldの設定
    my_blender.setup_rigid_body_world(config.output["movie_sec"])

    asset_path = os.path.expanduser(config.assets["parts_dir"])
    if not os.path.isabs(asset_path):
        asset_path = os.path.abspath(os.path.join(module_dir, asset_path))
        print(asset_path)

    # roomを追加
    my_blender.append_collection(os.path.join(asset_path, "room.blend"), "room")

    # 壁を非表示に
    hidden_walls = ["f_wall"]
    if not config.room["show_wall"]:
        hidden_walls = ["f_wall", "b_wall", "l_wall", "r_wall", "floor", "ceil"]

    for w in hidden_walls:
        bpy.context.scene.objects[w].hide_viewport = True
        bpy.context.scene.objects[w].hide_render = True

    # 既存のカメラとライトを削除する
    for obj in [o for o in bpy.data.objects if o.name in ["Camera", "Light"]]:
        bpy.data.objects.remove(obj)
    # 実験ルーム用のカメラとライトを配置する
    my_blender.append_collection(os.path.join(asset_path, "camera_and_lights.blend"), "camera_and_lights")

    # 渦追加
    force = my_blender.add_vortex(config.vortex)

    # 赤色のマテリアル
    material_dict = {}
    material_dict["default"] = my_blender.create_material("red_text", my_srt.hex_to_rgba(config.text["color"]))

    # フォント
    font = bpy.data.fonts.load(os.path.expanduser(config.text["font_path"]))

    item_list = my_srt.read_srt_file(args.srtfile)
    for idx, item in enumerate(item_list):
        extra_info = item["time_info"].get("json", {})

        materail_name = extra_info.get("color", "default")
        if materail_name not in material_dict.keys():
            color = my_srt.hex_to_rgba(materail_name)
            material_dict[materail_name] = my_blender.create_material(materail_name, color)

        # テキスト追加
        txt = "\n".join(item["lines"])
        txt_obj = my_blender.add_text(txt, 1.5, 0.2, font, material_dict[materail_name])
        txt_obj = my_blender.convert_to_mesh(txt_obj)
        # 中心に移動
        txt_obj.location = extra_info.get("location", config.text["initial_location"])

        # rigid body追加
        my_blender.add_to_rigid_body(txt_obj)
        # アニメーション追加
        start_sec = item["time_info"]["start"].total_seconds()
        end_sec = item["time_info"]["end"].total_seconds()
        my_blender.animate_obj(txt_obj, start_sec, end_sec)

        if "strength" in extra_info.keys():
            my_blender.animate_force(force, start_sec, extra_info["strength"])

    # グリーンバック
    if config.world["use_green_screen"]:
        my_blender.setup_greenback_worlds()

    # 3Dビューポートの初期化
    my_blender.initialize_3dviewport()

    # with bpy.context.temp_override(point_cache=bpy.context.scene.rigidbody_world.point_cache):
    #     bpy.ops.ptcache.bake(bake=True)

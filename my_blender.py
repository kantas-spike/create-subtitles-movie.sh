import bpy
import os
import math


def initailize_blender():
    # 最初の手順
    #  Blenderを起動して、Generalを選択します
    #   スプラッシュスクリーンを非表示に
    #   https://blender.stackexchange.com/questions/5208/prevent-splash-screen-from-being-shown-when-using-a-script
    #   ただし、設定が変更されてしまうため、今後、スプラッシュスクリーンが常に非表示になる
    bpy.context.preferences.view.show_splash = False

    #   なにもしなくてもGeneralになるので、コメントアウト
    # bpy.ops.wm.read_homefile(app_template="")  # Generalを選択

    #  立方体は不要なので削除します
    cube = bpy.data.objects['Cube']
    if cube is not None:
        bpy.data.objects.remove(cube)


def setup_output(fps, movie_sec):
    # 出力の設定
    #  フレームレートに30
    preset_path = bpy.utils.preset_find(
        str(fps), bpy.utils.preset_paths("framerate")[0])
    bpy.ops.script.execute_preset(
        filepath=preset_path, menu_idname="RENDER_MT_framerate_presets")
    #   上記は以下を実行する
    #   bpy.context.scene.render.fps = 30
    #   bpy.context.scene.render.fps_base = 1

    #  フレームレンジに30秒 (30×30=900)
    bpy.context.scene.frame_end = bpy.context.scene.render.fps * movie_sec
    #  ファイルフォーマットにFFmpeg
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    #  エンコーディングにMPEG-4
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    # Output
    bpy.context.scene.render.filepath = os.path.abspath(".") + "/"


def setup_rigid_body_world(movie_sec, gravity=0):
    # Rigid Body Worldの設定
    #  Rigid Body Worldがなければ作成
    if bpy.context.scene.rigidbody_world is None:
        bpy.ops.rigidbody.world_add()
    #  Cacheに30秒 (30×30=900)
    bpy.context.scene.rigidbody_world.point_cache.frame_end = bpy.context.scene.render.fps * movie_sec
    #  Gravityに0
    bpy.context.scene.rigidbody_world.effector_weights.gravity = gravity


def append_collection(blend_file_path, object_name):
    # コレクション追加
    inner_dir = "Collection"
    bpy.ops.wm.append(
        filepath=os.path.join(blend_file_path, inner_dir, object_name),
        directory=os.path.join(blend_file_path, inner_dir),
        filename=object_name)


def add_vortex(strength):
    #  渦追加
    bpy.ops.object.effector_add(
        type='VORTEX', enter_editmode=False, align='WORLD')
    bpy.context.object.field.shape = 'POINT'
    bpy.context.object.field.strength = strength
    bpy.context.object.field.seed = 1
    bpy.context.object.field.noise = 3
    bpy.context.object.field.noise = 0
    bpy.context.object.field.use_absorption = False
    # bpy.context.object.rotation_euler = [math.radians(x) for x in [0, 65, 15]]
    bpy.context.object.rotation_euler = [math.radians(x) for x in [40, 80, 35]]
    # bpy.context.object.location = (-5, -1.5, -4)
    bpy.context.object.location = (-5, 1, -1.5)


def create_material(name, base_color):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs[0].default_value = base_color
    return m


def add_text(text, size, extrude, font, material):
    bpy.ops.object.text_add()
    txt_obj = bpy.context.object

    # フォント設定
    txt_obj.data.font = font
    # 文言設定
    txt_obj.data.body = text
    txt_obj.data.size = size
    # 厚み
    txt_obj.data.extrude = extrude

    # オブジェクトを回転
    txt_obj.rotation_euler[0] = math.radians(90)
    # マテリアル設定
    txt_obj.active_material = material

    return txt_obj


def convert_to_mesh(obj):
    org_obj = bpy.context.view_layer.objects.active
    bpy.context.view_layer.objects.active = obj
    # メッシュに変更
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
    bpy.context.view_layer.objects.active = org_obj
    return obj


def add_to_rigid_body(obj):
    org_obj = bpy.context.view_layer.objects.active
    bpy.context.view_layer.objects.active = obj

    if not hasattr(obj, 'rigidbody'):
        bpy.ops.rigidbody.object_add()

    obj.rigid_body.angular_damping = 0.8
    obj.rigid_body.friction = 0
    obj.rigid_body.restitution = 1
    bpy.context.view_layer.objects.active = org_obj
    return obj


def initialize_3dviewport():
    a = [a for a in bpy.context.screen.areas if a.type == 'VIEW_3D'][0]
    r = [r for r in a.regions if r.type == 'WINDOW'][0]
    with bpy.context.temp_override(area=a, region=r):
        # すべて選択解除
        bpy.ops.object.select_all(action='DESELECT')
        # 正面からのビューに切り替え
        bpy.ops.view3d.view_axis(type='FRONT')
        bpy.ops.view3d.view_all(center=False)
        # カメラからのビューに切り替え
        bpy.ops.view3d.view_camera()
        # ビューポートシェーディングをRenderedに
        bpy.context.space_data.shading.type = 'RENDERED'


def animate_obj(obj, start_sec=0, end_sec=None):
    show_obj(obj, start_sec)

    if end_sec is not None:
        hide_obj(obj, end_sec)


def show_obj(obj, sec):
    # 初期設定
    #  物理シミュレーションを無効化
    obj.rigid_body.enabled = False
    #  オブジェクトを非表示に
    obj.hide_viewport = True
    obj.hide_render = True
    #  すべての文字を同じ位置に配置するので、配置時点での衝突を回避するため、衝突グループに所属させない
    obj.rigid_body.collision_collections[0] = False

    #  フレームの位置を指定秒に移動
    target_frame = int(sec * bpy.context.scene.render.fps)
    # キーフレームの登録
    insert_keyframes(obj, target_frame)

    # 次フレーム
    #  物理シミュレーションを有効化
    obj.rigid_body.enabled = True
    #  オブジェクトを表示
    obj.hide_viewport = False
    obj.hide_render = False

    #  フレーム位置を1つすすめる
    target_frame += 1
    # キーフレームの登録
    insert_keyframes(obj, target_frame)

    # 初期段階での衝突回避用
    target_frame += bpy.context.scene.render.fps * 2
    #  壁と同じ衝突グループに追加
    obj.rigid_body.collision_collections[0] = True
    # キーフレームの登録
    insert_keyframes(obj, target_frame)


def hide_obj(obj, sec):
    target_frame = int(sec * bpy.context.scene.render.fps)

    #  物理シミュレーションを無効化
    obj.rigid_body.enabled = False
    #  オブジェクトを非表示に
    obj.hide_viewport = True
    obj.hide_render = True
    #  すべての文字を同じ位置に配置するので、配置時点での衝突を回避するため、衝突グループに所属させない
    obj.rigid_body.collision_collections[0] = False

    # キーフレームの登録
    insert_keyframes(obj, target_frame)


def insert_keyframes(obj, frame):
    for k in ["rigid_body.enabled", "hide_viewport", "hide_render"]:
        obj.keyframe_insert(data_path=k, frame=frame)

    obj.keyframe_insert(data_path="rigid_body.collision_collections", frame=frame, index=0)

import streamlit as st
import numpy as np
import math
import random
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont

st.title("🔥 视频防盗神器：动态游走水印 MVP")

# 上传视频
video_file = st.file_uploader("上传视频", type=["mp4", "mov"])

# 水印文字
text = st.text_input("输入水印文字", "@MongoIT女")

# 模式选择
mode = st.selectbox("选择水印模式", [
    "蛇形游走",
    "随机漂浮",
    "边界巡航"
])

# 字体（Windows安全路径）
FONT_PATH = "C:/Windows/Fonts/arial.ttf"

# =========================
# 生成文字图层（核心）
# =========================
def make_text_image(txt, font_size, color):
    img = Image.new("RGBA", (800, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, font_size)
    draw.text((10, 10), txt, font=font, fill=color)
    return np.array(img)

# =========================
# 位置函数（核心）
# =========================
def get_position(mode, t, W, H, duration):
    if mode == "蛇形游走":
        x = int(W * (t / duration))
        y = int(H / 2 + (H / 4) * math.sin(t * 3))
    
    elif mode == "随机漂浮":
        # 每秒换一次位置（避免闪烁过强）
        seed = int(t)
        random.seed(seed)
        x = random.randint(0, W - 200)
        y = random.randint(0, H - 100)

    elif mode == "边界巡航":
        perimeter = 2 * (W + H)
        pos = (t / duration) * perimeter

        if pos < W:
            x, y = pos, 0
        elif pos < W + H:
            x, y = W, pos - W
        elif pos < 2 * W + H:
            x, y = 2 * W + H - pos, H
        else:
            x, y = 0, perimeter - pos

    else:
        x, y = 50, 50

    return int(x), int(y)

# =========================
# 主处理逻辑
# =========================
if video_file and text:

    if st.button("🚀 开始生成防盗视频"):
        
        with open("input.mp4", "wb") as f:
            f.write(video_file.read())

        clip = VideoFileClip("input.mp4")
        W, H = clip.size
        duration = clip.duration

        font_size = int(H / 18)
        watermark_img = make_text_image(text, font_size, (255, 0, 0, 180))

        base_txt_clip = ImageClip(watermark_img).set_duration(duration)

        # 动态位置函数
        def dynamic_pos(t):
            return get_position(mode, t, W, H, duration)

        # 关键：不断更新位置
        moving_clip = base_txt_clip.set_position(dynamic_pos)

        final = CompositeVideoClip([clip, moving_clip])

        output = "output_watermark.mp4"
        final.write_videofile(output, codec="libx264", audio_codec="aac")

        st.success("生成完成！")
        st.video(output)
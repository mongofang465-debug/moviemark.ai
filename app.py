import streamlit as st
import tempfile
import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

st.title("🔥 视频防盗神器：动态滚动水印")

# 上传视频
video_file = st.file_uploader("上传视频", type=["mp4", "mov"])
# 用户输入水印文字
watermark_text = st.text_input("输入水印文字", "@MongoIT女")

# 水印模式选择
mode = st.selectbox("选择水印模式", ["蛇形游走", "随机漂浮", "边界巡航"])

# 字体路径（云端可用系统字体，Linux通常 /usr/share/fonts）
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

if video_file and watermark_text:
    if st.button("生成视频"):

        # 临时保存上传文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_input:
            tmp_input.write(video_file.read())
            input_path = tmp_input.name

        output_path = "output_watermark.mp4"

        # ===============================
        # 根据选择模式生成不同 ffmpeg drawtext 公式
        # ===============================
        if mode == "蛇形游走":
            # x轴匀速移动，y轴正弦波
            vf_expr = f"drawtext=text='{watermark_text}':fontcolor=red:fontsize=48:x='mod(50*t\\, w-text_w)':y='h/2+50*sin(t*2)':shadowcolor=black:shadowx=2:shadowy=2"
        elif mode == "随机漂浮":
            # 每秒随机位置
            vf_expr = f"drawtext=text='{watermark_text}':fontcolor=red:fontsize=48:x='random(1)* (w-text_w)':y='random(1)*(h-text_h)':shadowcolor=black:shadowx=2:shadowy=2"
        elif mode == "边界巡航":
            # 沿视频边框移动
            vf_expr = f"drawtext=text='{watermark_text}':fontcolor=red:fontsize=48:x='if(lt(mod(t*100\\,2*w+h)\\,w),mod(t*100\\,w),if(lt(mod(t*100\\,2*w+h)\\,w+h),w,2*w+h-mod(t*100\\,2*w+h)))':y='if(lt(mod(t*100\\,2*w+h)\\,w),0,if(lt(mod(t*100\\,2*w+h)\\,w+h),mod(t*100\\,h),h))':shadowcolor=black:shadowx=2:shadowy=2"
        else:
            vf_expr = f"drawtext=text='{watermark_text}':fontcolor=red:fontsize=48:x=50:y=50:shadowcolor=black:shadowx=2:shadowy=2"

        # 执行 ffmpeg 命令
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vf", vf_expr,
            "-codec:a", "copy",
            output_path
        ]

        try:
            subprocess.run(cmd, check=True)
            st.success("生成完成！")
            st.video(output_path)
        except subprocess.CalledProcessError:
            st.error("生成视频失败，请确认 ffmpeg 在环境中可用。")

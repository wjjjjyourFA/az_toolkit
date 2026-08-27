import subprocess
import os

def convert_to_h264_ffmpeg(input_file, output_file, width=None, height=None, fps=None):
    """
    使用 FFmpeg 转码 H.264，参数尽量和你的 C++ 命令一致。
    """
    cmd = [
        "ffmpeg",
        "-y",  # 覆盖输出
        "-i", input_file,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        "-crf", "26",
    ]

    # 可选设置关键帧间隔
    if fps:
        g = int(fps * 2)
        cmd += ["-g", str(g), "-keyint_min", str(g)]
        cmd += ["-x264-params", "scenecut=0"]

    # 保留原分辨率或指定
    if width and height:
        cmd += ["-s", f"{width}x{height}"]

    # 输出 MP4 并加速播放和支持片段化
    cmd += ["-movflags", "+faststart+frag_keyframe+empty_moov", output_file]

    print("Running FFmpeg command:")
    print(" ".join(cmd))

    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    root = f"/media/neousys/US203/2025-12-26/video102/video"
    base_name = f"11-52-13"
    output = f"/home/neousys/workspace/result/2025-12-26/102"
    
    file = os.path.join(root, base_name)
    input_files = [f"{file}.avi", f"{file}.mp4"]
    for input_file in input_files:
        if not os.path.exists(input_file):
            continue  # 文件不存在就跳过

        output_file = os.path.join(output, f"{base_name}_h264.mp4")

        # 可选：获取原视频信息
        # 这里假设你想用原分辨率和帧率
        convert_to_h264_ffmpeg(input_file, output_file)

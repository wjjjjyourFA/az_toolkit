import time


def show_status_message(message: str, duration: float = 2.0):
    """显示状态消息（使用英文避免显示问题）"""
    # 将中文消息转换为英文，避免显示问题
    english_messages = {
        "半自动模式：点击标注框记录关键点": "Semi-Auto: Click boxes to record keypoints",
        "关键点不足，未生成标注": "Not enough keypoints",
        "插值完成": "Interpolation completed",
        "已清除所有标注": "All annotations cleared",
        "当前帧无标注": "No annotations in current frame",
        "标注已保存": "Annotations saved"
    }

    # 检查是否有对应的英文消息
    display_message = message
    for chinese, english in english_messages.items():
        if chinese in message:
            display_message = english
            break

    status_message = display_message
    status_message_time = time.time()
    status_display_duration = duration
    print(message)  # 控制台仍显示原始消息

    return status_message, status_message_time, status_display_duration


def clear_status_message() -> str:
    """清除状态消息"""
    return ""

import re


def preprocess_text(text):

    if not text:
        return ""

    # Chuyển toàn bộ về chữ thường
    text = text.lower()

    # Xóa email
    text = re.sub(
        r'\S+@\S+',
        ' ',
        text
    )

    # Xóa URL
    text = re.sub(
        r'http\S+|www\S+',
        ' ',
        text
    )

    # Thay ký tự đặc biệt bằng khoảng trắng
    # Giữ lại +, #, . vì có các skill như C++, C#, .NET
    text = re.sub(
        r'[^a-zA-Z0-9+#.\s]',
        ' ',
        text
    )

    # Xóa khoảng trắng dư
    text = re.sub(
        r'\s+',
        ' ',
        text
    ).strip()

    return text

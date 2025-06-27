import os
import cv2
import numpy as np
from PIL import Image

# Histogram Eşitleme (R, G, B ayrı ayrı)
def apply_histogram_equalization(img_pil):
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    channels = cv2.split(img_cv)
    eq_channels = [cv2.equalizeHist(c) for c in channels]
    eq_img = cv2.merge(eq_channels)
    return Image.fromarray(cv2.cvtColor(eq_img, cv2.COLOR_BGR2RGB))

# Canny edge mask (kenar bölgelerini dışlama)
def get_edge_mask(img_pil):
    gray = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    mask = cv2.bitwise_not(edges)
    return mask // 255  # 0 (kenar) veya 1 (gizlemeye uygun)

# Bit-Plane Görselleştirme (0–7 bit düzeylerini çıkar)
def extract_bit_planes(image_path, output_dir):
    img = Image.open(image_path).convert("L")
    img_np = np.array(img)
    os.makedirs(output_dir, exist_ok=True)
    bitplane_paths = []

    for bit in range(8):
        bit_plane = ((img_np >> bit) & 1) * 255
        bit_img = Image.fromarray(np.uint8(bit_plane))
        path = os.path.join(output_dir, f"bitplane_{bit}.png")
        bit_img.save(path)
        bitplane_paths.append(path)

    return bitplane_paths

# Encode: mesajı görsele göm
def encode_message(image_path, message, output_path):
    try:
        img = Image.open(image_path).convert("RGB")
        mask = get_edge_mask(img)  # Histogram eşitleme app.py içinde yapılmalı

        message_bytes = message.encode("utf-8")
        binary_message = ''.join(format(byte, '08b') for byte in message_bytes)
        binary_message += '1111111111111110'  # 16-bit mesaj sonu işareti

        pixels = list(img.getdata())
        width, height = img.size
        total_bits_needed = len(binary_message)
        bit_index = 0
        used_bits = 0
        encoded_pixels = []

        for i, (r, g, b) in enumerate(pixels):
            x = i % width
            y = i // width

            if y >= mask.shape[0] or x >= mask.shape[1] or mask[y][x] == 0:
                encoded_pixels.append((r, g, b))
                continue

            new_r, new_g, new_b = r, g, b
            for channel_index in range(3):
                if bit_index >= total_bits_needed:
                    break
                bit = int(binary_message[bit_index])
                if channel_index == 0:
                    new_r = (r & ~1) | bit
                elif channel_index == 1:
                    new_g = (g & ~1) | bit
                elif channel_index == 2:
                    new_b = (b & ~1) | bit
                bit_index += 1
                used_bits += 1

            encoded_pixels.append((new_r, new_g, new_b))

        if bit_index < total_bits_needed:
            raise ValueError("Mesaj çok uzun veya kenarsız alan yetersiz!")

        img.putdata(encoded_pixels)
        img.save(output_path, format="PNG")

        return {
            "status": "success",
            "message": "Mesaj başarıyla gizlendi.",
            "used_pixels": used_bits // 3,
            "message_length": len(message),
            "total_pixels": len(pixels),
            "bit_used_ratio": round((used_bits / (len(pixels) * 3)) * 100, 2)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Decode: mesajı çöz
def decode_message(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        pixels = list(img.getdata())

        binary_message = ""
        for pixel in pixels:
            for value in pixel[:3]:
                binary_message += str(value & 1)

        if '1111111111111110' not in binary_message:
            return {
                "status": "error",
                "message": "Mesaj sonlandırıcısı bulunamadı! Görselde mesaj olmayabilir."
            }

        message_bits = binary_message.split('1111111111111110')[0]
        byte_array = bytearray()
        for i in range(0, len(message_bits), 8):
            byte = message_bits[i:i+8]
            if len(byte) == 8:
                byte_array.append(int(byte, 2))

        message = byte_array.decode("utf-8")

        return {
            "status": "success",
            "message": message
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

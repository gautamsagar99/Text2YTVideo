import os
import cv2
import numpy as np
import base64

os.makedirs("input_text", exist_ok=True)
os.makedirs("output_video", exist_ok=True)
os.makedirs("input_video", exist_ok=True)
os.makedirs("output_text", exist_ok=True)
os.makedirs("metadata", exist_ok=True)

def encode_file_to_video():
    for filename in os.listdir("input_text"):
        filepath = os.path.join("input_text", filename)

        # Read file bytes
        with open(filepath, "rb") as f:
            byte_data = f.read()

        # Convert bytes to Base64 string
        b64_str = base64.b64encode(byte_data).decode('ascii')

        # Convert Base64 string to bits
        binary_str = ''.join(format(ord(c), '08b') for c in b64_str)

        width, height = 256, 256
        bits_per_frame = width * height
        total_frames = (len(binary_str) + bits_per_frame - 1) // bits_per_frame

        frames = []
        for i in range(total_frames):
            chunk = binary_str[i * bits_per_frame : (i + 1) * bits_per_frame]
            chunk = chunk.ljust(bits_per_frame, '0')
            arr = np.array([255 if bit == '1' else 0 for bit in chunk], dtype=np.uint8).reshape((height, width))
            frame = cv2.merge([arr, arr, arr])
            frames.append(frame)

        output_video_name = f"{filename}_video.avi"
        output_path = os.path.join("output_video", output_video_name)
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        out = cv2.VideoWriter(output_path, fourcc, 1, (width, height))

        for frame in frames:
            out.write(frame)
        out.release()

        # Save metadata with original filename
        meta_path = os.path.join("metadata", f"{filename}_video.meta")
        with open(meta_path, "w", encoding="utf-8") as meta_file:
            meta_file.write(filename)

        print(f"✅ Encoded '{filename}' → '{output_path}'")
        print(f"   Metadata saved → '{meta_path}'")

def decode_video_to_file():
    for filename in os.listdir("input_video"):
        if not filename.endswith(".avi"):
            continue
        filepath = os.path.join("input_video", filename)

        meta_filename = filename.rsplit('.',1)[0] + ".meta"
        meta_path = os.path.join("metadata", meta_filename)
        if not os.path.isfile(meta_path):
            print(f"❌ Metadata file not found for '{filename}', skipping.")
            continue
        with open(meta_path, "r", encoding="utf-8") as meta_file:
            orig_filename = meta_file.read().strip()

        cap = cv2.VideoCapture(filepath)
        binary_str = ''

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            bits = ''.join('1' if px == 255 else '0' for px in binary.flatten())
            binary_str += bits
        cap.release()

        # Convert bits back to Base64 string
        chars = [binary_str[i:i+8] for i in range(0, len(binary_str), 8)]
        b64_chars = []
        for c in chars:
            if len(c) < 8:
                continue
            val = int(c, 2)
            if val == 0:
                continue
            b64_chars.append(chr(val))
        b64_str = ''.join(b64_chars)

        try:
            byte_data = base64.b64decode(b64_str)
        except Exception as e:
            print(f"❌ Base64 decode error for '{filename}': {e}")
            continue

        output_path = os.path.join("output_text", orig_filename)
        with open(output_path, "wb") as f:
            f.write(byte_data)

        print(f"✅ Decoded '{filename}' → '{output_path}'")

if __name__ == "__main__":
    mode = input("Encode or decode files? (encode/decode): ").strip().lower()
    if mode == "encode":
        encode_file_to_video()
    elif mode == "decode":
        decode_video_to_file()
    else:
        print("❌ Invalid option. Please type 'encode' or 'decode'.")

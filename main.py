import os
import cv2
import numpy as np

# Ensure folders exist
os.makedirs("input_text", exist_ok=True)
os.makedirs("output_video", exist_ok=True)
os.makedirs("input_video", exist_ok=True)
os.makedirs("output_text", exist_ok=True)

def encode_text_to_video():
    for filename in os.listdir("input_text"):
        if filename.lower().endswith(".txt"):
            filepath = os.path.join("input_text", filename)

            with open(filepath, "r", encoding="utf-8") as f:
                text_data = f.read()

            # Convert text to binary string
            binary_str = ''.join(format(ord(c), '08b') for c in text_data)

            # Parameters for binary frame
            width, height = 256, 256  # 256x256 = 65536 bits per frame
            bits_per_frame = width * height
            total_frames = (len(binary_str) + bits_per_frame - 1) // bits_per_frame

            frames = []
            for i in range(total_frames):
                chunk = binary_str[i * bits_per_frame : (i + 1) * bits_per_frame]
                # Pad chunk to full frame size
                chunk = chunk.ljust(bits_per_frame, '0')
                arr = np.array([255 if bit == '1' else 0 for bit in chunk], dtype=np.uint8).reshape((height, width))
                frame = cv2.merge([arr, arr, arr])  # make it 3-channel
                frames.append(frame)

            # Save as video with original filename in output
            output_video_name = f"{filename}_video.mp4"
            output_path = os.path.join("output_video", output_video_name)
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(output_path, fourcc, 1, (width, height))

            for frame in frames:
                out.write(frame)

            out.release()
            print(f"✅ Encoded '{filename}' → '{output_path}' (text as binary video)")

def decode_video_to_text():
    for filename in os.listdir("input_video"):
        if filename.lower().endswith(".mp4"):
            filepath = os.path.join("input_video", filename)

            cap = cv2.VideoCapture(filepath)
            binary_str = ''

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                # Convert frame to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Threshold to get binary
                _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
                # Flatten and convert to bits
                bits = ''.join(['1' if px == 255 else '0' for px in binary.flatten()])
                binary_str += bits

            cap.release()

            # Convert binary string to text
            chars = [binary_str[i:i+8] for i in range(0, len(binary_str), 8)]
            text = ''
            for c in chars:
                if set(c) <= {'0', '1'} and len(c) == 8:
                    val = int(c, 2)
                    if val == 0:
                        continue  # skip padding
                    text += chr(val)

            # Save decoded text with original video filename
            output_text_name = f"{filename}_decoded.txt"
            output_path = os.path.join("output_text", output_text_name)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"✅ Decoded '{filename}' → '{output_path}' (binary video to text)")

if __name__ == "__main__":
    mode = input("Do you want to encode text to binary video or decode binary video to text? (encode/decode): ").strip().lower()

    if mode == "encode":
        encode_text_to_video()
    elif mode == "decode":
        decode_video_to_text()
    else:
        print("❌ Invalid option. Please type 'encode' or 'decode'.")

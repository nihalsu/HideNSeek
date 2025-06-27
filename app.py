from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
from steganography import encode_message, decode_message, extract_bit_planes, apply_histogram_equalization
import os
import uuid
from PIL import Image
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return filename.lower().endswith(".png")

@app.route("/encode", methods=["POST"])
def encode():
    if "image" not in request.files or "message" not in request.form:
        return jsonify({"status": "error", "message": "Lütfen hem resim hem mesaj gönderin."}), 400

    image = request.files["image"]
    message = request.form["message"]
    apply_histogram = request.form.get("histogram") == "1"

    if not allowed_file(image.filename):
        return jsonify({"status": "error", "message": "Sadece .png formatı destekleniyor."}), 400

    # Benzersiz ID oluştur
    image_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{image_id}.png")
    output_path = os.path.join(OUTPUT_FOLDER, f"encoded_{image_id}.png")
    preview_path = os.path.join(OUTPUT_FOLDER, f"preview_{image_id}.png")
    bitplane_dir = os.path.join(OUTPUT_FOLDER, "bitplanes", image_id)

    # Görseli kaydet
    image.save(input_path)

    # Histogram eşitleme uygulanacaksa burada yap
    img = Image.open(input_path).convert("RGB")
    if apply_histogram:
        img = apply_histogram_equalization(img)
    img.save(input_path)  # Gömme işlemi bu güncellenmiş görüntüye uygulanacak

    # Gömme işlemi
    result = encode_message(input_path, message, output_path)

    if result["status"] == "error":
        return jsonify(result), 500

    # Bit-plane görsellerini üret
    bitplane_paths = extract_bit_planes(output_path, bitplane_dir)
    bitplane_urls = [
        f"http://localhost:5000/download/bitplanes/{image_id}/bitplane_{i}.png"
        for i in range(8)
    ]

    # Önizleme oluştur
    try:
        img = Image.open(output_path)
        img.thumbnail((300, 300))
        img.save(preview_path, format="PNG")
    except Exception as e:
        return jsonify({"status": "error", "message": "Önizleme oluşturulamadı."}), 500

    return jsonify({
        "status": "success",
        "message": "Mesaj başarıyla gizlendi.",
        "download_url": f"http://localhost:5000/download/{os.path.basename(output_path)}",
        "preview_url": f"http://localhost:5000/download/{os.path.basename(preview_path)}",
        "message_length": result.get("message_length"),
        "used_pixels": result.get("used_pixels"),
        "total_pixels": result.get("total_pixels"),
        "bit_used_ratio": result.get("bit_used_ratio"),
        "bitplanes": bitplane_urls
    })

@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

@app.route("/download/bitplanes/<image_id>/<filename>")
def download_bitplane(image_id, filename):
    path = os.path.join(OUTPUT_FOLDER, "bitplanes", image_id, filename)
    return send_file(path, as_attachment=False)

@app.route("/decode", methods=["POST"])
def decode():
    if "image" not in request.files:
        return jsonify({"error": "Resim dosyası eksik."}), 400

    image = request.files["image"]
    if not allowed_file(image.filename):
        return jsonify({"error": "Sadece .png formatı destekleniyor."}), 400

    image_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"decode_{image_id}.png")
    image.save(input_path)

    try:
        result = decode_message(input_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": "Mesaj çözülemedi."}), 500

if __name__ == "__main__":
    app.run(debug=True)

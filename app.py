from flask import Flask, jsonify, render_template, request

from generator import generate_copy_pack

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    transcript_text = request.form.get("transcriptText", "")
    media_file = request.files.get("mediaFile")

    if media_file and not transcript_text:
        transcript_text = f"Uploaded file: {media_file.filename}"

    result = generate_copy_pack(request.form, transcript_text)
    return jsonify(result)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
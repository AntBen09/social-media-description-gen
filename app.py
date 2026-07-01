from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    direction = request.form.get("direction", "")
    platform = request.form.get("platform", "")
    transcript_text = request.form.get("transcriptText", "")
    media_file = request.files.get("mediaFile")

    print("---- New submission ----")
    print("Direction:", direction)
    print("Platform:", platform)
    print("Transcript text provided:", bool(transcript_text))
    print("Media file provided:", media_file.filename if media_file else None)

    return jsonify({"status": "received"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
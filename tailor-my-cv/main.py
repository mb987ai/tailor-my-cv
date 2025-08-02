from flask import Flask, render_template, request, send_file
import os
from io import BytesIO
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    resume_text = ""
    job_text = ""

    resume_file = request.files.get("resume_file")
    job_file = request.files.get("job_file")
    resume_input = request.form.get("resume_textarea")
    job_input = request.form.get("job_textarea")

    if resume_file and resume_file.filename != "":
        resume_text = resume_file.read().decode("utf-8", errors="ignore")
    elif resume_input:
        resume_text = resume_input

    if job_file and job_file.filename != "":
        job_text = job_file.read().decode("utf-8", errors="ignore")
    elif job_input:
        job_text = job_input

    if not resume_text or not job_text:
        return render_template("result.html", error="❌ Please provide both resume and job description!")

    prompt = f"""
You are a professional resume editor and cover letter writer.

Please take the resume and job description provided below and do the following:
1. Rewrite the resume to better align with the job description while keeping it human-like.
2. Generate a cover letter that is tailored to the job description using a natural, warm tone.

Resume:
{resume_text}

Job Description:
{job_text}
    """

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        result_text = response.choices[0].message.content
        return render_template("result.html", result=result_text)
    except Exception as e:
        return render_template("result.html", error=f"❌ An error occurred: {e}")

@app.route("/download", methods=["POST"])
def download():
    content = request.form.get("download_content", "")
    if not content:
        return render_template("result.html", error="❌ No content provided for download.")

    buffer = BytesIO()
    buffer.write(content.encode("utf-8"))
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Tailored_Resume_and_Cover_Letter.docx", mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

if __name__ == "__main__":
    app.run(debug=True)
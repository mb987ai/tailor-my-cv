from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"  # Fast + efficient


def call_groq_api(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{
            "role": "user",
            "content": prompt
        }],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"{response.status_code}: {response.text}")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        resume = request.form.get("resume") or ""
        job_desc = request.form.get("jobdesc") or ""
        tone = request.form.get("tone", "Human-like")

        if not resume or not job_desc:
            return render_template(
                "index.html",
                error="Please provide both resume and job description.")

        # Prompts
        resume_prompt = f"""You are a professional resume editor. Rewrite this resume to better match the job description. Make it concise, compelling, and human-like in tone ({tone}). Resume:\n{resume}\n\nJob Description:\n{job_desc}"""
        cover_letter_prompt = f"""Write a personalized, human-like cover letter for the following resume and job description. Make it specific and engaging. Tone: {tone}\n\nResume:\n{resume}\n\nJob Description:\n{job_desc}"""

        try:
            tailored_resume = call_groq_api(resume_prompt)
            cover_letter = call_groq_api(cover_letter_prompt)
            return render_template("result.html",
                                   resume=tailored_resume,
                                   cover_letter=cover_letter)
        except Exception as e:
            return render_template("index.html",
                                   error=f"Something went wrong: {str(e)}")

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)

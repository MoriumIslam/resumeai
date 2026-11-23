from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename

from utils.preprocess import clean_text
from utils.pdf_extractor import extract_text_from_pdf
from utils.predictor import predict_category, vectorizer
from utils.similarity import get_similarity
# from utils.llm_feedback import generate_feedback  # optional

from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

app = Flask(__name__)
# UPLOAD_FOLDER from config is already an absolute path
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

print(f"[APP INIT] Upload folder configured: {app.config['UPLOAD_FOLDER']}")
print(f"[APP INIT] Upload folder exists: {os.path.exists(app.config['UPLOAD_FOLDER'])}")

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
print(f"[APP INIT] Upload folder created/verified")


# 🔹 Load sample job descriptions
def load_sample_jobs():
    try:
        with open("data/sample_jobs.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""


# 🔹 Home Page
@app.route("/")
def home():
    jobs = load_sample_jobs()
    return render_template("index.html", jobs=jobs)


# 🔹 Analyze Route
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        # Check if file is in request
        if 'resume' not in request.files:
            return "Error: No file part in the request"

        file = request.files['resume']
        job_desc = request.form.get('job_desc', '')

        # Check if file was selected
        if file.filename == "":
            return "Error: No file selected for uploading"
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            return f"Error: Invalid file type '{file.filename}'. Only PDF files are allowed"

        # Validate job description
        if not job_desc or not job_desc.strip():
            return "Error: Please provide a job description"

        # Create a safe filename
        filename = secure_filename(file.filename)
        if not filename:
            # Fallback for filenames that result in empty strings after secure_filename
            filename = "resume.pdf"
        else:
            # Ensure it ends with .pdf
            if not filename.endswith('.pdf'):
                filename += '.pdf'
        
        # Create the full file path
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        filepath = os.path.abspath(filepath)
        
        # Verify filepath is within upload folder (security check)
        upload_folder_abs = os.path.abspath(app.config['UPLOAD_FOLDER'])
        if not filepath.startswith(upload_folder_abs):
            return "Error: Invalid file path"
        
        print(f"\n=== FILE UPLOAD DEBUG ===")
        print(f"Original filename: {file.filename}")
        print(f"Secured filename: {filename}")
        print(f"Upload folder: {upload_folder_abs}")
        print(f"Target filepath: {filepath}")
        print(f"Upload folder exists: {os.path.exists(upload_folder_abs)}")
        print(f"Is upload folder a directory: {os.path.isdir(upload_folder_abs)}")
        
        # Save the file
        try:
            file.save(filepath)
            print(f"File saved successfully")
        except Exception as save_error:
            print(f"File save error: {save_error}")
            return f"Error: Failed to save file - {str(save_error)}"
        
        # Verify file was saved
        if not os.path.exists(filepath):
            return f"Error: File was not saved properly to {filepath}"
        
        if not os.path.isfile(filepath):
            return f"Error: Path {filepath} exists but is not a file (might be a directory)"
        
        print(f"File verified - exists: {os.path.exists(filepath)}, is file: {os.path.isfile(filepath)}")
        print(f"File size: {os.path.getsize(filepath)} bytes")

        # Extract resume text
        try:
            resume_text = extract_text_from_pdf(filepath)
        except ValueError as e:
            print(f"PDF extraction error: {str(e)}")
            return f"Error: {str(e)}"
        except Exception as e:
            print(f"Unexpected PDF extraction error: {str(e)}")
            return f"Error: Could not extract text from PDF - {str(e)}"

        if not resume_text or not resume_text.strip():
            return "Error: Could not extract text from PDF"

        # Clean text
        try:
            cleaned_resume = clean_text(resume_text)
            cleaned_job = clean_text(job_desc)
        except Exception as e:
            print(f"Text cleaning error: {str(e)}")
            return f"Error: Failed to process text - {str(e)}"

        # Predict category
        try:
            category, resume_vec = predict_category(cleaned_resume)
        except Exception as e:
            print(f"Prediction error: {str(e)}")
            return f"Error: Failed to analyze resume - {str(e)}"

        # Job vector
        try:
            job_vec = vectorizer.transform([cleaned_job])
        except Exception as e:
            print(f"Vectorization error: {str(e)}")
            return f"Error: Failed to process job description - {str(e)}"

        # Similarity score
        try:
            score = get_similarity(resume_vec, job_vec)
        except Exception as e:
            print(f"Similarity error: {str(e)}")
            return f"Error: Failed to calculate match score - {str(e)}"

        # Candidate level
        if score > 0.7:
            level = "Strong"
        elif score > 0.4:
            level = "Moderate"
        else:
            level = "Weak"

        print(f"=== ANALYSIS COMPLETE ===")
        print(f"Category: {category}, Score: {score}, Level: {level}\n")

        return render_template(
            "result.html",
            category=category,
            score=round(score * 100, 2),
            level=level,
        )
    
    except Exception as e:
        print(f"Unexpected error in analyze: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error: An unexpected error occurred - {str(e)}"


# 🔹 Run App
if __name__ == "__main__":
    app.run(debug=True)
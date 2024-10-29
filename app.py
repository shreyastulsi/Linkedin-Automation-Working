import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from LLM_logic import create_db_from_pdf, extract_experience_examples, optimize_all_sections, integrate_seo_optimization  # Import your logic

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check if the uploaded file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if a file was submitted
        if 'file' not in request.files:
            return "No file part in the request", 400

        file = request.files['file']

        if file.filename == '':
            return "No selected file", 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)  # Save the file

            # Redirect to results page with the filename in the URL
            return redirect(url_for('results', filename=filename))

    return render_template('upload.html')

@app.route('/results/<filename>')
def results(filename):
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Extract sections and experience examples
    db, sections = create_db_from_pdf(pdf_path)
    example_experience = extract_experience_examples("/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/Linkedin-Automation/Experience-Examples-PDF.pdf")

    # Generate optimized LinkedIn content
    optimized_content = optimize_all_sections(sections, example_experience)
    # optimized_content = integrate_seo_optimization(optimized_content)

    # Render the results page with optimized content
    return render_template('results.html', content=optimized_content)

if __name__ == '__main__':
    # Create the uploads folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Run the Flask app
    app.run(debug=True)

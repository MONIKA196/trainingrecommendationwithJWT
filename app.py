from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
import mysql.connector
import os
import json
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
import pytesseract
import random
import base64
import requests
# from dotenv import load_dotenv # Uncomment if utilizing .env
# load_dotenv()

app = Flask(__name__)

# --- Configuration ---
app.secret_key = 'your_secret_key_here'

# MySQL Configuration (Update these with your MySQL Workbench credentials)
# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'moni@@naga17N5'  # Change this to your MySQL password
app.config['MYSQL_DB'] = 'training_db'

# Gemini Configuration
app.config['GEMINI_API_KEY'] = 'AIzaSyBJgQ-A-MDnloAaj4kmknOG9BMBh7v2IrI' # User provided Gemini API Key

def get_db():
    if 'db' not in g or not g.db.is_connected():
        try:
            print(f"Attempting to connect to database at {app.config['MYSQL_HOST']}...")
            g.db = mysql.connector.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD'],
                database=app.config['MYSQL_DB'],
                connect_timeout=10
            )
            print("Connection successful within request context.")
        except mysql.connector.Error as err:
            print(f"Database Connection Error: {err}")
            return None
    return g.db


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Upload Folder for OCR
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Simulation Helpers (Mock LLM / OCR) ---

def mock_llm_roadmap(goal_course, current_level):
    """Simulates an LLM generating a learning roadmap."""
    days = []
    topics = [
        "Introduction to " + goal_course,
        "Core Concepts of " + goal_course,
        "Advanced implementation",
        "Project work",
        "Final Assessment"
    ]
    for i, topic in enumerate(topics, 1):
        days.append({
            "day": f"Day {i}",
            "title": topic,
            "description": f"Learn the fundamentals of {topic} suitable for {current_level} level.",
            "resources": ["Video Tutorial", "Documentation Link"]
        })
    return days

# --- NLP & OCR Helpers ---

def mock_ocr_questions(text):
    """Fallback: Simulates generating questions if OCR text is too short."""
    questions = [
        {
            "question": f"Based on the upload '{text[:15]}...', what is critical?",
            "options": ["Analysis", "Design", "Implementation", "Testing"],
            "answer": "Analysis"
        },
        {
            "question": "What is implied by the content?",
            "options": ["Growth", "Stability", "Decline", "None of above"],
            "answer": "Growth"
        }
    ]
    return questions

def get_tesseract_path():
    """Tries to find tesseract executable."""
    # Common default locations for Windows
    paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\LENOVO\AppData\Local\Tesseract-OCR\tesseract.exe"
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return None

def extract_text_from_image(image_path):
    """Extracts text using Pytesseract."""
    try:
        tesseract_cmd = get_tesseract_path()
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        text = pytesseract.image_to_string(Image.open(image_path))
        return text.strip()
    except Exception as e:
        print(f"OCR Error: {e}")
        return "Error: Could not extract text. Ensure Tesseract-OCR is installed and added to PATH."

def generate_questions_from_text(text):
    """Generates simple fill-in-the-blank questions from text."""
    if not text or len(text) < 50:
        return mock_ocr_questions(text) # Fallback if text is too short

    questions = []
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
    
    # Get all words for distractors
    all_words = [w for w in text.split() if len(w) > 4 and w.isalnum()]
    
    # Generate up to 5 questions
    for i, sentence in enumerate(sentences[:5]):
        words = sentence.split()
        if len(words) < 5: continue
        
        # Pick a random word as the answer (simple heuristic: long words are usually interesting)
        candidates = [w for w in words if len(w) > 4]
        if not candidates: continue
        
        answer = random.choice(candidates)
        question_text = sentence.replace(answer, "_______", 1)
        
        # Generate options
        distractors = random.sample(all_words, min(3, len(all_words)))
        options = distractors + [answer]
        random.shuffle(options)
        
        # Ensure unique options
        options = list(set(options))
        if len(options) < 4:
            options = options + ["None of the above", "All of the above"][:4-len(options)]
            
        questions.append({
            "question": f"Fill in the blank: {question_text}",
            "options": options,
            "answer": answer
        })
    
    
    if not questions:
         return mock_ocr_questions(text)
         
    return questions

def analyze_image_with_gemini(image_path):
    """Uses Gemini 1.5 Flash REST API to extract text and generate key points directly from the image."""
    api_key = app.config.get('GEMINI_API_KEY')
    if not api_key or api_key == 'YOUR_GEMINI_API_KEY':
        return None

    try:
        # 1. Read and encode the image
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # 2. Prepare the payload
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        print(f"DEBUG: Using Gemini 2.5 REST API with model: gemini-2.5-flash")
        
        prompt = """
        You are an expert academic assistant. Analyze the provided image and perform two tasks:
        1. **Text Extraction**: Extract every single piece of readable text from the image.
        2. **Insightful Summary**: Identify the most critical 'Important Key Points' from the extracted text.
           - Provide 5 to 10 high-quality bullet points.
        
        Return the response ONLY as a JSON object. 
        Strictly follow this structure:
        {
            "extracted_text": "...",
            "key_points": [
                "Point 1...",
                "Point 2..."
            ]
        }
        """

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": encoded_image
                        }
                    }
                ]
            }]
        }

        # 3. Call the API
        headers = {'Content-Type': 'application/json'}
        print(f"Sending request to Gemini API for image: {image_path}")
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        print(f"Gemini API Response Status: {response.status_code}")

        # 4. Parse the AI response
        if 'candidates' in response_data and len(response_data['candidates']) > 0:
            text_response = response_data['candidates'][0]['content']['parts'][0]['text']
            
            # Robust JSON cleaning
            txt = text_response.strip()
            # Remove markdown code blocks if the AI added them
            if txt.startswith("```"):
                txt = txt.split("```")[1]
                if txt.startswith("json"):
                    txt = txt[4:]
            
            try:
                # Find JSON bounds
                start = txt.find("{")
                end = txt.rfind("}") + 1
                if start != -1 and end != -1:
                    txt = txt[start:end]
                    return json.loads(txt)
            except Exception as parse_err:
                print(f"JSON Parsing failed: {parse_err}")
                return {
                    "extracted_text": txt[:500],
                    "key_points": ["AI output was not in correct format, but text was found."]
                }
        
        print(f"API Error Response: {response_data}")
        return None
        
    except Exception as e:
        print(f"Gemini REST Critical Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_questions_with_gemini_text_only(text):
    """REST version of text-only generation."""
    api_key = app.config.get('GEMINI_API_KEY')
    if not api_key or api_key == 'YOUR_GEMINI_API_KEY':
        return None

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        prompt = f"""
        Based on the following text, generate 3-5 multiple-choice questions.
        Return the response strictly as a VALID JSON Array of objects.
        Each object must have the following keys:
        - "question": The question string.
        - "options": A list of 4 distinct options.
        - "answer": The correct option string.
        
        Text: {text[:4000]}
        """

        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload)
        response_data = response.json()
        
        if 'candidates' in response_data:
            txt = response_data['candidates'][0]['content']['parts'][0]['text']
            txt = txt.replace('```json', '').replace('```', '').strip()
            return json.loads(txt)
        return None
    except Exception as e:
        print(f"Gemini Text REST Error: {e}")
        return None

def generate_mcq_questions(topic):
    """Generates mock MCQ questions based on topic."""
    # Randomly select or generate questions
    dummy_questions = [
        {
            "id": 1,
            "question": f"What is the primary function of {topic}?",
            "options": ["Processing", "Storage", "Networking", "Display"],
            "correct": "Processing"
        },
        {
            "id": 2,
            "question": f"Which language is often used with {topic}?",
            "options": ["Python", "HTML", "SQL", "All of the above"],
            "correct": "All of the above"
        },
        {
            "id": 3,
            "question": f"Is {topic} scalable?",
            "options": ["Yes", "No", "Maybe", "Only vertically"],
            "correct": "Yes"
        }
    ]
    return dummy_questions

# --- Routes ---

@app.route('/')
def home():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        if db is None:
            msg = 'Database connection failed. Please contact administrator.'
            return render_template('auth/login.html', msg=msg)
            
        cursor = db.cursor(dictionary=True)
        # We only query by username now
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        # Verify the hash
        if account and check_password_hash(account['password_hash'], password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['role'] = account['role']
            return redirect(url_for('dashboard'))
        else:
            msg = 'Incorrect username or password!'
    return render_template('auth/login.html', msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'role' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role'] # 'student' or 'trainer'
        
        db = get_db()
        if db is None:
            msg = 'Database connection failed. Please contact administrator.'
            return render_template('auth/register.html', msg=msg)
            
        cursor = db.cursor(dictionary=True)
        # Check if username OR email already exists
        cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, email))
        account = cursor.fetchone()
        
        if account:
            if account['username'] == username:
                msg = 'Username already exists!'
            else:
                msg = 'Email already registered!'
        else:
            # Hash the password before saving
            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)', 
                           (username, email, hashed_password, role))
            db.commit()
            
            # If student, create profile entry
            user_id = cursor.lastrowid
            if role == 'student':
                cursor.execute('INSERT INTO student_profiles (user_id) VALUES (%s)', (user_id,))
                db.commit()
            
            # Auto-login after registration
            session['loggedin'] = True
            session['id'] = user_id
            session['username'] = username
            session['role'] = role
            
            return redirect(url_for('dashboard'))
    return render_template('auth/register.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        cursor = get_db().cursor(dictionary=True)
        if session['role'] == 'student':
            # Create a default profile if it doesn't exist
            cursor.execute('SELECT * FROM student_profiles WHERE user_id = %s', (session['id'],))
            profile = cursor.fetchone()
            if not profile:
                 cursor.execute('INSERT INTO student_profiles (user_id) VALUES (%s)', (session['id'],))
                 get_db().commit()
                 cursor.execute('SELECT * FROM student_profiles WHERE user_id = %s', (session['id'],))
                 profile = cursor.fetchone()

            return render_template('dashboard/student.html', username=session['username'], profile=profile)
        else:
            # Trainer View: Fetch all students
            cursor.execute('SELECT users.id, users.username, users.email, student_profiles.current_course, student_profiles.goal_course FROM users JOIN student_profiles ON users.id = student_profiles.user_id WHERE users.role = "student"')
            students = cursor.fetchall()
            
            # Fetch recent MCQ results for all students (mock query for now)
            cursor.execute('SELECT users.username, mcq_results.topic, mcq_results.score FROM mcq_results JOIN users ON mcq_results.user_id = users.id ORDER BY test_date DESC LIMIT 5')
            results = cursor.fetchall()
            
            return render_template('dashboard/trainer.html', username=session['username'], students=students, results=results)
    return redirect(url_for('login'))

# Student Features

@app.route('/recommendation', methods=['GET', 'POST'])
def recommendation():
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    roadmap = None
    if request.method == 'POST':
        current_course = request.form.get('current_course')
        current_level = request.form.get('current_level')
        goal_course = request.form.get('goal_course')
        
        # Save to profile
        cursor = get_db().cursor(dictionary=True)
        cursor.execute('UPDATE student_profiles SET current_course=%s, current_level=%s, goal_course=%s WHERE user_id=%s',
                       (current_course, current_level, goal_course, session['id']))
        get_db().commit()
        
        # Generate Roadmap
        roadmap = mock_llm_roadmap(goal_course, current_level)
        
        # Save recommendation to DB
        cursor.execute('INSERT INTO training_recommendations (user_id, course_name, roadmap_json) VALUES (%s, %s, %s)', 
                       (session['id'], goal_course, json.dumps(roadmap)))
        get_db().commit()
        
    return render_template('features/recommendation.html', roadmap=roadmap)

@app.route('/ocr', methods=['GET', 'POST'])
def ocr_generator():
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    key_points = []
    extracted_text = None
    
    cursor = get_db().cursor(dictionary=True)
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 1. Try Gemini Vision (Image -> Text + Key Points)
        gemini_result = analyze_image_with_gemini(filepath)
        
        if gemini_result:
            extracted_text = gemini_result.get('extracted_text', 'Text extracted by AI')
            key_points = gemini_result.get('key_points', [])
            if not key_points:
                 key_points = ["AI extracted text but couldn't identify specific key points. See raw text below."]
        else:
             # If AI Vision fails
             print("Gemini Vision failed. Attempting Tesseract fallback...")
             flash("Advanced AI analysis paused. Using local OCR engine...")
             extracted_text = extract_text_from_image(filepath)
             
             if "Error:" not in extracted_text and len(extracted_text.strip()) > 10:
                  # Use heuristic fallback for points: split by newlines, filter meaningful lines
                  lines = [line.strip() for line in extracted_text.split('\n') if len(line.strip()) > 30]
                  if not lines:
                      # If no long lines, try splitting by dots
                      lines = [line.strip() for line in extracted_text.split('.') if len(line.strip()) > 20]
                  
                  key_points = lines[:8] if lines else ["Text found but it looks too fragmented to extract points."]
             else:
                  extracted_text = "Analysis Failed: The image might be too blurry or contains no readable text."
                  key_points = ["Could not identify accurate points. Please ensure the image is well-lit and the text is clear."]
        
        # Save to DB - ensure we save as JSON
        cursor.execute('INSERT INTO ocr_uploads (user_id, image_filename, generated_text, generated_questions) VALUES (%s, %s, %s, %s)',
                       (session['id'], filename, extracted_text, json.dumps(key_points)))
        get_db().commit()
    else:
        # GET request: Load the most recent upload if it exists
        cursor.execute('SELECT generated_text, generated_questions FROM ocr_uploads WHERE user_id = %s ORDER BY upload_date DESC LIMIT 1', (session['id'],))
        row = cursor.fetchone()
        if row:
            extracted_text = row['generated_text']
            try:
                key_points = json.loads(row['generated_questions'])
            except:
                key_points = []
        
    return render_template('features/ocr.html', key_points=key_points, extracted_text=extracted_text)

@app.route('/mcq', methods=['GET', 'POST'])
def mcq_test():
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'topic' in request.form:
            topic = request.form['topic']
            questions = generate_mcq_questions(topic)
            return render_template('features/mcq.html', questions=questions, topic=topic)
        
        if 'submit_test' in request.form:
            # Calculate Score
            score = 0
            total = 0
            topic = request.form.get('topic_hidden')
            
            # Re-generate questions to check answers (in real app, store in session/db to persist)
            original_questions = generate_mcq_questions(topic)
            
            for q in original_questions:
                total += 1
                user_ans = request.form.get(f'q_{q["id"]}')
                if user_ans == q['correct']:
                    score += 1
            
            # Save Score
            cursor = get_db().cursor(dictionary=True)
            cursor.execute('INSERT INTO mcq_results (user_id, topic, score, total_questions) VALUES (%s, %s, %s, %s)',
                           (session['id'], topic, score, total))
            get_db().commit()
            
            return render_template('features/mcq_result.html', score=score, total=total, topic=topic)

    return render_template('features/mcq.html')

@app.route('/profile')
def profile():
    if 'loggedin' not in session: return redirect(url_for('login'))
    
    cursor = get_db().cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
    user = cursor.fetchone()
    
    if session['role'] == 'student':
        cursor.execute('SELECT * FROM student_profiles WHERE user_id = %s', (session['id'],))
        details = cursor.fetchone()
    else:
        details = {}
        
    return render_template('features/profile.html', user=user, details=details)

@app.route('/about')
def about():
    if 'loggedin' not in session: return redirect(url_for('login'))
    return render_template('about.html')

if __name__ == '__main__':
    # Test database connection on startup
    try:
        test_conn = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        print("Connected to MySQL successfully!")
        test_conn.close()
    except Exception as e:
        print(f"CRITICAL: Could not connect to database: {e}")
        
    print("--- SERVER RESTARTED - SECURE VERSION V3 ---")
    app.run(debug=True)

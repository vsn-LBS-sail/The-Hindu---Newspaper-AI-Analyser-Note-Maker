from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, Article, Quiz, QuizResponse, Mains, MainsResponse
from ai_utils import generate_upsc_notes, generate_quiz, generate_mains_questions, evaluate_mains_answer
from scraper import fetch_daily_articles, extract_article_content
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hindu_upsc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ================= AUTHENTICATION =================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check email and password.', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if exists
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash('User already exists', 'danger')
            return redirect(url_for('register'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created! Pls login', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ================= CORE ROUTES =================

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    articles = Article.query.filter_by(user_id=current_user.id).order_by(Article.created_at.desc()).all()
    stats = {
        'total_notes': len(articles),
        # You can expand stats as needed
    }
    quiz_scores = {qr.quiz_id: qr for qr in current_user.quiz_responses}
    return render_template('dashboard.html', articles=articles, stats=stats, quiz_scores=quiz_scores)

@app.route('/fetch', methods=['GET', 'POST'])
@login_required
def fetch_news():
    """Page to select a date and see articles"""
    articles = []
    selected_date = None
    if request.method == 'POST':
        date_str = request.form.get('date') # Format YYYY-MM-DD
        if date_str:
            y, m, d = map(int, date_str.split('-'))
            res = fetch_daily_articles(y, m, d)
            if res.get('success'):
                articles = res['articles']
            else:
                flash(res.get('error'), 'danger')
            selected_date = date_str
            
    return render_template('fetch.html', articles=articles, selected_date=selected_date)

@app.route('/api/analyze', methods=['POST'])
@login_required
def analyze_article():
    data = request.json
    url = data.get('url')
    
    if not url:
         return jsonify({'success': False, 'error': 'No URL provided'}), 400
         
    # Check if user already extracted it
    existing = Article.query.filter_by(user_id=current_user.id, url=url).first()
    if existing:
         return jsonify({'success': True, 'article_id': existing.id, 'message': 'Already saved'})
         
    # Extract text
    extraction = extract_article_content(url)
    if not extraction.get('success'):
         return jsonify(extraction), 400
         
    text = extraction['text']
    title = extraction['title']
    
    # Analyze with AI (Notes ONLY!)
    ai_notes = generate_upsc_notes(text, title)
    
    if not ai_notes.get('success'):
        return jsonify({'success': False, 'error': 'AI Note Gen Failed: ' + ai_notes.get('error','')}), 500
        
    # Inject the actual top image from the Hindu directly into the notes JSON payload!
    if extraction.get('image_url'):
        ai_notes['data']['image_url'] = extraction['image_url']
        
    # Save to db
    new_article = Article(
        user_id=current_user.id,
        url=url,
        title=title,
        content=text,
        upsc_notes=json.dumps(ai_notes['data']),
        gs_papers=",".join(ai_notes['data'].get('gs_papers', []))
    )
    db.session.add(new_article)
    db.session.commit()
    return jsonify({'success': True, 'article_id': new_article.id, 'message': 'Successfully analyzed and saved'})

@app.route('/api/generate_quiz/<int:article_id>', methods=['POST'])
@login_required
def api_generate_quiz(article_id):
    article = Article.query.get_or_404(article_id)
    if article.user_id != current_user.id:
         return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    if article.quiz:
         return jsonify({'success': True, 'message': 'Quiz already exists'})
         
    ai_quiz = generate_quiz(article.content, article.title)
    if ai_quiz.get('success'):
        new_quiz = Quiz(
            article_id=article.id,
            questions=json.dumps(ai_quiz['questions'])
        )
        db.session.add(new_quiz)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Failed to generate quiz: ' + ai_quiz.get('error', '')}), 500

@app.route('/api/generate_mains/<int:article_id>', methods=['POST'])
@login_required
def api_generate_mains(article_id):
    article = Article.query.get_or_404(article_id)
    if article.user_id != current_user.id:
         return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    if article.mains:
         return jsonify({'success': True, 'message': 'Mains already exists'})
         
    ai_mains = generate_mains_questions(article.content, article.title)
    if ai_mains.get('success'):
        new_mains = Mains(
            article_id=article.id,
            questions=json.dumps(ai_mains['mains_questions'])
        )
        db.session.add(new_mains)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Failed to generate Mains questions: ' + ai_mains.get('error', '')}), 500


@app.route('/notes/<int:article_id>')
@login_required
def view_notes(article_id):
    article = Article.query.filter_by(id=article_id, user_id=current_user.id).first_or_404()
    notes_data = json.loads(article.upsc_notes)
    return render_template('notes.html', article=article, notes=notes_data)

@app.route('/quiz/<int:article_id>', methods=['GET'])
@login_required
def take_quiz(article_id):
    article = Article.query.filter_by(id=article_id, user_id=current_user.id).first_or_404()
    if not article.quiz:
         flash("No quiz available for this article.", "warning")
         return redirect(url_for('view_notes', article_id=article.id))
         
    questions = json.loads(article.quiz.questions)
    return render_template('quiz.html', article=article, quiz=article.quiz, questions=questions)

@app.route('/quiz/submit', methods=['POST'])
@login_required
def submit_quiz():
    data = request.json
    quiz_id = data.get('quiz_id')
    user_answers = data.get('answers') # dict of q_id: chosen_idx
    
    quiz = Quiz.query.get(quiz_id)
    if not quiz or quiz.article.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Invalid access'}), 403
        
    questions = json.loads(quiz.questions)
    score = 0
    total = len(questions)
    
    for q in questions:
        q_id = str(q['id'])
        if q_id in user_answers and user_answers[q_id] == q['correct']:
            score += 1
            
    response = QuizResponse(
        user_id=current_user.id,
        quiz_id=quiz.id,
        user_answers=json.dumps(user_answers),
        score=score,
        total=total
    )
    db.session.add(response)
    db.session.commit()
    
    return jsonify({'success': True, 'score': score, 'total': total, 'percentage': int((score/total)*100)})

@app.route('/mains/<int:article_id>', methods=['GET'])
@login_required
def practice_mains(article_id):
    article = Article.query.filter_by(id=article_id, user_id=current_user.id).first_or_404()
    if not article.mains:
         flash("No mains questions available for this article.", "warning")
         return redirect(url_for('view_notes', article_id=article.id))
         
    questions = json.loads(article.mains.questions)
    responses = MainsResponse.query.filter_by(user_id=current_user.id, mains_id=article.mains.id).all()
    past_attempts = {str(r.question_id): {'score': r.score, 'feedback': r.feedback, 'answer': r.user_answer} for r in responses}
    
    return render_template('mains.html', article=article, mains=article.mains, questions=questions, past_attempts=past_attempts)

@app.route('/api/evaluate_mains', methods=['POST'])
@login_required
def submit_mains_evaluation():
    data = request.json
    mains_id = data.get('mains_id')
    question_id = data.get('question_id')
    user_answer = data.get('answer')
    
    if not user_answer or len(user_answer.strip()) < 10:
        return jsonify({'success': False, 'error': 'Answer is too short!'}), 400
    
    mains_entry = Mains.query.get(mains_id)
    if not mains_entry or mains_entry.article.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Invalid access'}), 403
        
    questions = json.loads(mains_entry.questions)
    
    # Find the specific question string and model answer
    target_q = next((q for q in questions if str(q['id']) == str(question_id)), None)
    if not target_q:
        return jsonify({'success': False, 'error': 'Question not found'}), 404
        
    question_text = target_q['question']
    model_answer = target_q['model_answer']
    
    # Send to AI
    eval_result = evaluate_mains_answer(question_text, model_answer, user_answer)
    if not eval_result.get('success'):
         return jsonify(eval_result), 500
         
    # Save to DB
    score = eval_result['evaluation'].get('score', 0)
    feedback = eval_result['evaluation'].get('feedback', '')
    
    new_response = MainsResponse(
        user_id=current_user.id,
        mains_id=mains_entry.id,
        question_id=int(question_id),
        user_answer=user_answer,
        score=score,
        feedback=feedback
    )
    db.session.add(new_response)
    db.session.commit()
    
    return jsonify({'success': True, 'score': score, 'feedback': feedback})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    articles = db.relationship('Article', backref='user', lazy=True)
    quiz_responses = db.relationship('QuizResponse', backref='user', lazy=True)
    mains_responses = db.relationship('MainsResponse', backref='user', lazy=True)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    url = db.Column(db.String(500)) # Not unique anymore because different users can save the same article
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    upsc_notes = db.Column(db.Text) # AI generated notes
    gs_papers = db.Column(db.String(100))  # Comma-separated: GS1,GS2
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    quiz = db.relationship('Quiz', backref='article', uselist=False, cascade='all, delete-orphan')
    mains = db.relationship('Mains', backref='article', uselist=False, cascade='all, delete-orphan')

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    questions = db.Column(db.Text)  # JSON array of AI generated questions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    responses = db.relationship('QuizResponse', backref='quiz', cascade='all, delete-orphan')

class QuizResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_answers = db.Column(db.Text)  # JSON dictionary mapping
    score = db.Column(db.Integer)
    total = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Mains(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    questions = db.Column(db.Text)  # JSON array of AI generated questions and model answers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    responses = db.relationship('MainsResponse', backref='mains', cascade='all, delete-orphan')

class MainsResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mains_id = db.Column(db.Integer, db.ForeignKey('mains.id'), nullable=False)
    question_id = db.Column(db.Integer, nullable=False)
    user_answer = db.Column(db.Text)
    score = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


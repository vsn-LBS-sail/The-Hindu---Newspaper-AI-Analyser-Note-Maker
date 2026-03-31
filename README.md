# InsightGS  - The Hindu Analyzer

## Overview
InsightGS is an AI-powered web application designed to help UPSC aspirants efficiently analyze current affairs from newspapers like The Hindu. It automates the process of extracting relevant information, generating structured notes, classifying content into General Studies (GS) categories, and creating quizzes and mains questions for effective preparation.
The system integrates web scraping, Natural Language Processing (NLP), and full-stack web development to transform unstructured news articles into structured, exam-oriented learning material.

Problem Statement
UPSC aspirants face difficulty in extracting relevant information from lengthy newspaper articles and organizing it according to the syllabus. Manual note-making is time-consuming, and there is a lack of tools that combine analysis with revision and self-assessment.
InsightGS solves this by automating article analysis, note generation, and quiz-based learning.

## Features
1. User Authentication (Register/Login)
2. Automatic Article Fetching from The Hindu
3. AI-Based Note Generation
4. GS Classification (GS-I to GS-IV)
5. Quiz Generation (MCQs)
6. Mains Question Generation
7. Quiz Evaluation with Scores
8. AI-Based Mains Answer Evaluation with Feedback
9. Dashboard for tracking notes and performance

## Tech Stack

1. Frontend:
     HTML
     CSS
     JavaScript
   
2. Backend:
     Python (Flask)
     Flask-Login
     Flask-Bcrypt
   
3. Database:
     SQLite (SQLAlchemy ORM)
     AI & Processing:
     NLP-based utilities
     JSON-based structured outputs
   
4. Other Tools:
     BeautifulSoup (Web Scraping)
     Requests
     Pandas (optional data handling)
   
## System Architecture

The system follows a modular architecture:
Article Fetching → Content Extraction → Preprocessing → AI Analysis → Storage → User Interaction

It consists of:
      1. Data Source Layer (Web Scraping)
      2. Processing Layer
      3. AI Analysis Layer
      4. Application Layer (Flask Backend)
      5. Database Layer (SQLite)
      6. Frontend Interface
      
# Usage
Register or log in to the application
Select a date to fetch articles
Choose an article to analyze
View AI-generated notes and GS classification
Generate and attempt quizzes
Practice mains questions and get AI-based feedback
Track progress on the dashboard

# Screenshots :

### Homepage
<img width="1425" height="909" alt="Screenshot 2026-03-31 125622" src="https://github.com/user-attachments/assets/a8ad00fa-2860-4661-88f1-0dcfe97652b4" />

### This page appears after the user selects a specific date and clicks on ‘Fetch News’, displaying the corresponding articles.
<img width="1292" height="901" alt="Screenshot 2026-03-31 125727" src="https://github.com/user-attachments/assets/ce1545ba-43dd-43fe-8e1a-9406be4851a9" />

### When an article is selected for analysis, this loading screen is displayed. It is designed to motivate aspirants by presenting positive and inspiring quotes.
<img width="1234" height="794" alt="Screenshot 2026-03-31 125747" src="https://github.com/user-attachments/assets/d23b708c-231b-49d8-8d61-d51898488095" />

### The below two is the Analysed notes page.
<img width="1280" height="909" alt="Screenshot 2026-03-31 125805" src="https://github.com/user-attachments/assets/c923efd6-d655-42a4-b57b-615b5678878e" />
<img width="1217" height="911" alt="Screenshot 2026-03-31 125822" src="https://github.com/user-attachments/assets/7b60fc8f-0dba-444f-a9d1-62c5cf4a7c40" />

### The following three images represent the screens displayed when the user selects ‘Generate MCQs’ (for Prelims) and ‘Generate Mains Test’ (for Mains).
<img width="1261" height="909" alt="Screenshot 2026-03-31 130003" src="https://github.com/user-attachments/assets/f2dbf482-3370-4ec4-a5e1-77d57ff00889" />
<img width="1247" height="915" alt="Screenshot 2026-03-31 130045" src="https://github.com/user-attachments/assets/62343cfe-35c8-4d42-a7b7-588d8eb1662f" />
<img width="982" height="742" alt="Screenshot 2026-03-31 130115" src="https://github.com/user-attachments/assets/795e4cf8-406e-4587-83fa-390f18b1752a" />


## Testing
Module testing for each component
Integration testing for complete workflow
Input validation and error handling
Output verification for notes, quizzes, and evaluation

## Future Enhancements
1. Support for multiple news sources
2. AI-generated video summaries of articles
3. Advanced NLP models (BERT, Transformers)
5. Personalized recommendations
6. Mobile application development
   

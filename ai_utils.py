import os
import json
import time
import re
import google.generativeai as genai
from dotenv import load_dotenv, dotenv_values

load_dotenv(override=True)

def retry_generate(model, prompt, max_retries=3):
    last_err = None
    for attempt in range(max_retries):
        try:
            return model.generate_content(prompt)
        except Exception as e:
            last_err = e
            err_str = str(e)
            if '429' in err_str:
                match = re.search(r'retry in (\d+\.?\d*)s', err_str)
                wait_time = float(match.group(1)) + 1 if match else 15.0
                    
                print(f"[{attempt+1}/{max_retries}] Quota Exceeded. API requested wait of {wait_time}s. Pausing thread...")
                time.sleep(wait_time)
            else:
                raise e
    return {'success': False, 'error': f"Failed after {max_retries} attempts. Last error: {str(last_err)}"}

def setup_gemini():
    config = dotenv_values(".env")
    api_key = config.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return False
    genai.configure(api_key=api_key)
    return True

def generate_upsc_notes(text, title):
    if not setup_gemini():
        return {'success': False, 'error': 'API key not configured'}
        
    try:
        note_schema = {
            "type": "OBJECT",
            "properties": {
                "gs_papers": {"type": "ARRAY", "items": {"type": "STRING"}},
                "topics": {"type": "ARRAY", "items": {"type": "STRING"}},
                "summary": {"type": "STRING"}
            },
            "required": ["gs_papers", "topics", "summary"]
        }
        
        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json", "response_schema": note_schema})
        prompt = f"""
As an expert UPSC educator, read the article titled '{title}' and generate highly concise, fact-dense notes specifically drawn from the article's core content. Do NOT give generic descriptions of the UPSC syllabus; focus EXCLUSIVELY on what the news article actually says and extract the most relevant data.

Focus specifically on:
1. Core Context: A brief 2-sentence summary of the actual news event.
2. Key Facts, Data, & Terminology: Extract specific numbers, new terms, or hard facts mentioned in the text.
3. Core Arguments (if an editorial): What is the specific author arguing?
4. UPSC Application: In 1-2 concise bullet points, how can an aspirant use this specific news in the exam (e.g., as a direct example in GS-2, or a case study for Ethics/Essay).

Format the output strictly according to the requested JSON schema. The `summary` field MUST be a well-structured markdown string using headers like `## Context`, `## Key Takeaways`, `## Key Data/Facts`, and `## UPSC Application`. Use bullet points extensively.

Article Text:
{text[:8000]} # Limit to avoid context length issues, though gemini can handle more
"""
        response = retry_generate(model, prompt)
        if isinstance(response, dict):
            return response
        result_text = response.text.strip()
        data = json.loads(result_text)
        return {'success': True, 'data': data}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def generate_quiz(text, title):
    if not setup_gemini():
        return {'success': False, 'error': 'API key not configured'}
        
    try:
        quiz_schema = {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "id": {"type": "INTEGER"},
                    "question": {"type": "STRING"},
                    "options": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "correct": {"type": "INTEGER"},
                    "explanation": {"type": "STRING"}
                },
                "required": ["id", "question", "options", "correct", "explanation"]
            }
        }
        
        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json", "response_schema": quiz_schema})
        prompt = f"""
Based on the article '{title}', generate high-quality Multiple Choice Questions (MCQs) in the standard UPSC Civil Services Preliminary examination format. The questions should test conceptual clarity and factual understanding, not just trivial details.
Generate ALL possible high-quality questions that can be reasonably derived from the core facts of this article. Do NOT artificially limit it to 5 questions; if the text is dense, generate more. If it's brief, generate fewer.

Format the output strictly according to the requested JSON array schema.

Article Text:
{text[:8000]}
"""
        response = retry_generate(model, prompt)
        if isinstance(response, dict):
            return response
        result_text = response.text.strip()
        questions = json.loads(result_text)
        return {'success': True, 'questions': questions}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def generate_mains_questions(text, title):
    if not setup_gemini():
        return {'success': False, 'error': 'API key not configured'}
        
    try:
        mains_schema = {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "id": {"type": "INTEGER"},
                    "question": {"type": "STRING"},
                    "model_answer": {"type": "STRING"}
                },
                "required": ["id", "question", "model_answer"]
            }
        }
        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json", "response_schema": mains_schema})
        prompt = f"""
Based strictly on the article '{title}', formulate 1 or 2 highly analytical Subjective Questions in the exact pattern of the UPSC Civil Services Mains Examination (Previous Year Questions format). 

For each formulated question, provide a comprehensive "Model Answer" structure. The Model Answer must:
- Be written in well-structured markdown (Introduction, Body Paragraphs with headers/bullets, and a solid Conclusion).
- Directly utilize data, arguments, and terminology explicitly mentioned in the text.

Article Text:
{text[:8000]}
"""
        response = retry_generate(model, prompt)
        if isinstance(response, dict):
            return response
        mains_data = json.loads(response.text.strip())
        return {'success': True, 'mains_questions': mains_data}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def evaluate_mains_answer(question, model_answer, user_answer):
    if not setup_gemini():
        return {'success': False, 'error': 'API key not configured'}
        
    try:
        eval_schema = {
            "type": "OBJECT",
            "properties": {
                "score": {"type": "INTEGER", "description": "Score out of 10"},
                "feedback": {"type": "STRING", "description": "Constructive markdown feedback"}
            },
            "required": ["score", "feedback"]
        }
        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json", "response_schema": eval_schema})
        prompt = f"""
You are an expert UPSC Mains examiner. Please evaluate the Aspirant's Answer against the Official Model Answer below for the given question. 

Question: {question}

Official Model Answer Reference:
{model_answer}

Aspirant's Answer:
{user_answer}

Provide a strict, critical evaluation. 
1. Assign a Score strictly out of 10. (Do not be overly generous; a score of 7-8 is excellent, 4-6 is average).
2. Provide constructive Feedback formatted as Markdown. Highlight exactly what they missed from the Model Answer and what they did well. Limit feedback to 3 concise but actionable paragraphs.
"""
        response = retry_generate(model, prompt)
        if isinstance(response, dict):
            return response
        evaluation = json.loads(response.text.strip())
        return {'success': True, 'evaluation': evaluation}
    except Exception as e:
        return {'success': False, 'error': str(e)}

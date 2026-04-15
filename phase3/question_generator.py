import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

def _extract_json_array(raw_text: str) -> str:
    """
    Extract the first valid JSON array substring from model output.
    Handles markdown fences and surrounding commentary text.
    """
    text = raw_text.strip()

    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end < start:
        raise ValueError("LLM output does not contain a JSON array.")
    return text[start:end + 1]

def _normalize_answer(value):
    if isinstance(value, int):
        if 0 <= value <= 3:
            return chr(ord("A") + value)
        if 1 <= value <= 4:
            return chr(ord("A") + value - 1)
    if not isinstance(value, str):
        return None

    cleaned = value.strip().upper()
    if cleaned in {"A", "B", "C", "D"}:
        return cleaned
    if cleaned and cleaned[0] in {"A", "B", "C", "D"}:
        return cleaned[0]
    return None

def _to_int_difficulty(value):
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None

def _normalize_question(item: dict):
    """
    Normalize common key variants into required schema.
    Returns None if required fields are still invalid.
    """
    if not isinstance(item, dict):
        return None

    question_text = item.get("question") or item.get("q")
    options = item.get("options") or item.get("choices")
    correct = item.get("correct_answer")
    if correct is None:
        correct = item.get("correct")
    if correct is None:
        correct = item.get("answer")
    difficulty = item.get("difficulty")
    if difficulty is None:
        difficulty = item.get("level")

    if not isinstance(question_text, str) or not question_text.strip():
        return None
    if not isinstance(options, list) or len(options) != 4:
        return None
    if not all(isinstance(opt, str) and opt.strip() for opt in options):
        return None

    normalized_correct = _normalize_answer(correct)
    normalized_difficulty = _to_int_difficulty(difficulty)
    if normalized_correct is None or normalized_difficulty not in {1, 2, 3}:
        return None

    return {
        "question": question_text.strip(),
        "options": [opt.strip() for opt in options],
        "correct_answer": normalized_correct,
        "difficulty": normalized_difficulty,
    }

def generate_questions(retrieved_chunks, num_questions=5):
    """
    Takes a list of retrieved chunks, feeds them into Gemini 1.5 Flash,
    and returns a structured list of dictionaries representing MCQs.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_key_here":
        raise ValueError("GEMINI_API_KEY is missing or invalid in the .env file")
        
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.2
    )

    context_text = "\\n\\n".join([f"Page {doc.metadata.get('page', '?')}:\\n{doc.page_content}" for doc in retrieved_chunks])
    
    prompt = PromptTemplate.from_template('''
You are an expert educator. Given the following specific context extracted from a student's textbook or notes, generate {num_questions} Multiple Choice Questions (MCQs) that test understanding of this material.

Context:
{context}

Format your output STRICTLY as a JSON list of dictionaries. Do not include any markdown formatting like ```json or any other text before/after the JSON. 
Each dictionary MUST have these exact keys:
- "question": The actual question text.
- "options": A list of exactly 4 strings, representing the options (e.g. ["A) ...", "B) ...", "C) ...", "D) ..."]).
- "correct_answer": The exact string of the correct option (e.g. "A").
- "difficulty": An integer representing difficulty: 1 (easy), 2 (medium), or 3 (hard).

Example Output:
[
  {{
    "question": "What is the capital of France?",
    "options": ["A) Berlin", "B) Madrid", "C) Paris", "D) Rome"],
    "correct_answer": "C",
    "difficulty": 1
  }}
]
''')

    chain = prompt | llm
    
    response = chain.invoke({
        "num_questions": num_questions,
        "context": context_text
    })

    output_text = response.content.strip()

    try:
        json_array_text = _extract_json_array(output_text)
        parsed = json.loads(json_array_text)
    except json.JSONDecodeError as e:
        print("Failed to parse JSON from LLM output. Raw Output:\n", output_text)
        raise ValueError("LLM returned invalid JSON for questions.") from e
    except ValueError as e:
        print("Failed to extract JSON from LLM output. Raw Output:\n", output_text)
        raise

    if not isinstance(parsed, list):
        raise ValueError("LLM question output must be a JSON list.")

    normalized_questions = []
    for idx, raw_q in enumerate(parsed):
        normalized = _normalize_question(raw_q)
        if normalized is None:
            print(f"Skipping invalid question at index {idx}: {raw_q}")
            continue
        normalized_questions.append(normalized)

    if not normalized_questions:
        raise ValueError("No valid questions generated from LLM output.")

    return normalized_questions

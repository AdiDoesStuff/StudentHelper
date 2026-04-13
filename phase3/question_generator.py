import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

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
        model="gemini-2.5-flash",
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

    # Basic cleanup in case the LLM outputs ```json ... ``` markdown
    output_text = response.content.strip()
    if output_text.startswith("```json"):
        output_text = output_text[7:]
    if output_text.startswith("```"):
        output_text = output_text[3:]
    if output_text.endswith("```"):
        output_text = output_text[:-3]
    output_text = output_text.strip()

    try:
        questions = json.loads(output_text)
        return questions
    except json.JSONDecodeError as e:
        print("Failed to parse JSON from LLM output. Raw Output:\\n", output_text)
        raise e

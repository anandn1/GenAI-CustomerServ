import os
import pandas as pd
from dotenv import load_dotenv
from langchain.vectorstores import Pinecone
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langdetect import detect, LangDetectException
from langchain.chat_models import ChatOpenAI

# Import all the new templates from your updated file
# This assumes your directory structure is `.../backend/utils/prompt_templates.py`
# and you run the script from the project's root directory.
from backend.utils import prompt_templates

# --- INITIALIZATION ---
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

llm = ChatOpenAI(
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="deepseek/deepseek-r1-0528-qwen3-8b",  # Correct model name
    temperature=0.1,
    max_tokens=4000,
    model_kwargs={
        "headers": {
            
        }
    }
)

embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

try:
    # Make sure to replace "..." with your actual Pinecone index name if it's not loaded from env
    vectorstore = Pinecone.from_existing_index(
        index_name=PINECONE_INDEX,
        embedding=embedding
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
except Exception as e:
    print(f"Error connecting to Pinecone: {e}. RAG functionality will be disabled.")
    retriever = None


# --- CONVERSATIONAL RAG CHAIN DEFINITION ---
def create_conversational_chain(retriever):
    if not retriever: return None
    history_aware_retriever = create_history_aware_retriever(llm, retriever, prompt_templates.history_rephrase_template)
    question_answer_chain = create_stuff_documents_chain(llm, prompt_templates.conversational_rag_template)
    return create_retrieval_chain(history_aware_retriever, question_answer_chain)


conversational_rag_chain = create_conversational_chain(retriever)


# --- HELPER FUNCTIONS ---
def detect_language(text: str) -> str:
    try:
        return detect(text)
    except LangDetectException:
        return 'en'


def translate_text(text: str, target_lang: str) -> str:
    prompt = f"Translate the following text to {target_lang}:\n\n{text}"
    return llm.invoke(prompt).content.strip()


def is_off_topic(query: str) -> bool:
    """Uses the LLM to quickly determine if a query is off-topic."""
    prompt = f"""You are a topic classifier. Your only job is to determine if the user's query is related to Walmart, its products, or customer service. Respond with 'RELATED' if it is, and 'OFF_TOPIC' if it is not. Query: "{query}" """
    response = llm.invoke(prompt).content.strip().upper()
    return "OFF_TOPIC" in response


# --- ROUTER LOGIC ---
def prompt_router(query: str):
    """Selects the best prompt template based on the query."""
    query_lower = query.lower()

    if is_off_topic(query):
        return prompt_templates.safety_guardrail_template, "guardrail"

    sentiment_prompt = f"Analyze the sentiment of the following query. Is the user angry, frustrated, or demanding a person? Respond 'ESCALATE' if so, otherwise 'STANDARD'. Query: \"{query}\""
    sentiment = llm.invoke(sentiment_prompt).content.strip().upper()
    if "ESCALATE" in sentiment:
        return prompt_templates.empathetic_deescalation_template, "escalation"

    if any(k in query_lower for k in ['vs', 'compare', 'difference between']):
        return prompt_templates.product_comparison_template, "comparison_rag"
    if any(k in query_lower for k in ['how to', 'steps to', 'guide me']):
        return prompt_templates.step_by_step_guide_template, "guide_rag"

    return prompt_templates.conversational_rag_template, "standard_rag"


# --- CORE LOGIC FUNCTION ---
def get_smart_answer(query: str, chat_history: list):
    """Analyzes the query using a router and directs it to the appropriate chain."""
    chosen_prompt, category = prompt_router(query)

    if category in ["guardrail", "escalation"]:
        chain = chosen_prompt | llm | StrOutputParser()
        response_text = chain.invoke({"question": query})
        new_chat_history = chat_history + [HumanMessage(content=query), AIMessage(content=response_text)]
        return response_text, [], category, new_chat_history

    if category in ["standard_rag", "comparison_rag", "guide_rag"]:
        if not conversational_rag_chain:
            return "RAG chain is not initialized.", [], "error", chat_history

        original_lang = detect_language(query)
        query_en = translate_text(query, 'en') if original_lang != 'en' else query

        # For these RAG-based tasks, we use the main conversational chain.
        # Its detailed system prompt is robust enough to handle comparisons and guides well.
        result = conversational_rag_chain.invoke({"input": query_en, "chat_history": chat_history})
        answer = result["answer"]
        sources = result.get("context", [])

        if original_lang != 'en':
            answer = translate_text(answer, original_lang)

        new_chat_history = chat_history + [HumanMessage(content=query), AIMessage(content=answer)]
        return answer, sources, category, new_chat_history

    return "I'm not sure how to handle that request.", [], "error", chat_history


# --- ADVANCED EVALUATION & MAIN EXECUTION (Restored from your original code) ---

def evaluate_with_llm(prompt: str, response: str, criteria: str) -> (bool, str):
    """
    Uses an LLM to evaluate if a response meets specific criteria.
    Returns a tuple of (is_pass: bool, justification: str).
    """
    evaluator_prompt = f"""
    You are an evaluation expert assessing an AI assistant's response.

    User Prompt: "{prompt}"
    AI Response: "{response}"
    Evaluation Criteria: "{criteria}"

    Based on the criteria, did the AI response pass?
    1. Analyze the user prompt and the AI's response.
    2. Compare the response against the evaluation criteria.
    3. Provide a brief justification for your decision.
    4. Conclude with 'PASS' on a new line if it passed, or 'FAIL' if it did not.
    """
    evaluation = llm.invoke(evaluator_prompt).content.strip()
    is_pass = evaluation.endswith("PASS")
    justification = evaluation.replace("PASS", "").replace("FAIL", "").strip()
    return is_pass, justification


def run_all_tests(test_file_path: str):
    """
    Loads and runs test cases, managing history for each conversational thread.
    """
    try:
        test_cases_df = pd.read_csv(test_file_path)
    except FileNotFoundError:
        print(f"Error: Test file not found at {test_file_path}")
        return

    results = []
    chat_histories = {}

    for index, row in test_cases_df.iterrows():
        case_id = row['id']
        prompt = row['prompt']
        category = row['category']
        criteria = row['evaluation_criteria']
        # Use a 'conversation_id' column in your CSV to test follow-ups
        convo_id = row.get('conversation_id', case_id)

        current_history = chat_histories.get(convo_id, [])

        print(f"--- Running Test Case #{case_id} (Convo: {convo_id}, Category: {category}) ---")
        print(f"Prompt: {prompt}")

        # Get the answer from our intelligent router
        response, _, _, new_history = get_smart_answer(prompt, current_history)
        chat_histories[convo_id] = new_history

        print(f"Response: {response}")
        passed, justification = evaluate_with_llm(prompt, response, criteria)

        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"Status: {status}\nJustification: {justification}\n")

        results.append({"ID": case_id, "Category": category, "Passed": passed})

    # Reporting
    report_df = pd.DataFrame(results)
    summary = report_df.groupby('Category')['Passed'].agg(['sum', 'count']).reset_index()
    summary.rename(columns={'sum': 'Passed', 'count': 'Total'}, inplace=True)
    summary['Pass Rate'] = (summary['Passed'] / summary['Total'] * 100).map('{:.1f}%'.format)
    print("--- 📊 Test Summary Report ---\n", summary.to_string(index=False))


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Option 1: Run your test suite
    # To test conversational flow, ensure your CSV has a 'conversation_id' column
    # for related prompts.
    # print("--- Running Test Suite ---")
    # run_all_tests("test_cases.csv")

    # Option 2: Run in interactive mode
    print("\n--- Interactive Mode ---")
    print("AI: Hello! I'm Wally, your Walmart support assistant. How can I help? (Type 'exit' to quit)")
    chat_history = []
    while True:
        user_query = input("You: ")
        if user_query.lower() == 'exit':
            break

        answer, sources, category, chat_history = get_smart_answer(user_query, chat_history)
        print(f"AI (via '{category}'): {answer}")
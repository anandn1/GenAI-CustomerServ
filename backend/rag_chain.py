import os
import time
import pandas as pd
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone.vectorstores import Pinecone as PineconeVectorStore
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langdetect import detect, LangDetectException
import json
import re
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor
import sys

# Import all templates
from backend.utils import prompt_templates

# --- INITIALIZATION ---
load_dotenv()

# Initialize Pinecone client
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Configure index
if not pc.has_index(os.getenv("PINECONE_INDEX")):
    pc.create_index(
        name=os.getenv("PINECONE_INDEX"),
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

# Initialize components
index = pc.Index(os.getenv("PINECONE_INDEX"))
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Configure LLM with optimized settings
llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="deepseek/deepseek-r1-0528-qwen3-8b",
    temperature=0.1,
    max_tokens=2000,  # Reduced for faster responses
    request_timeout=30,  # Add timeout
    max_retries=2,  # Reduce retries
    default_headers={}
)

# Initialize vectorstore
try:
    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=os.getenv("PINECONE_INDEX"),
        embedding=embedding,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})  # Reduced k for faster retrieval
except Exception as e:
    print(f"Error connecting to Pinecone: {e}. RAG functionality will be disabled.")
    retriever = None


# --- OPTIMIZED QUERY PROCESSING ---
class OptimizedQueryProcessor:
    def __init__(self):
        # Pre-compile regex patterns for better performance
        self.whitespace_pattern = re.compile(r'\s+')
        self.abbreviation_patterns = self._compile_abbreviation_patterns()

        # Cache for intent detection to avoid repeated LLM calls
        self.intent_cache = {}

    def _compile_abbreviation_patterns(self):
        """Pre-compile regex patterns for abbreviations"""
        abbreviations = {
            'refund': 'return',
            'exchange': 'return',
            'swap': 'return',
            'hrs': 'hours',
            'phone': 'contact',
            'call': 'contact',
        }

        patterns = {}
        for abbrev, full in abbreviations.items():
            patterns[abbrev] = re.compile(r'\b' + re.escape(abbrev) + r'\b', re.IGNORECASE)

        return patterns

    def normalize_query(self, query: str) -> str:
        """Fast query normalization with cached patterns"""
        # Remove extra whitespace
        normalized = self.whitespace_pattern.sub(' ', query.strip())

        # Apply abbreviation replacements
        for abbrev, pattern in self.abbreviation_patterns.items():
            normalized = pattern.sub(abbrev, normalized)

        return normalized

    def get_basic_intent(self, query: str) -> dict:
        """Fast, rule-based intent detection without LLM calls"""
        query_lower = query.lower()

        # Define keyword patterns for common intents
        intent_patterns = {
            "return": ["return", "refund", "exchange", "bring back", "send back", "give back"],
            "hours": ["hours", "open", "close", "time", "when"],
            "location": ["where", "address", "location", "find", "directions"],
            "contact": ["phone", "call", "contact", "speak", "talk"],
            "price": ["price", "cost", "how much", "expensive", "cheap"],
            "comparison": ["vs", "versus", "compare", "difference", "better", "or"],
            "availability": ["available", "stock", "in store", "do you have", "carry"],
            "how_to": ["how", "steps", "guide", "process", "way to"]
        }

        # Check for negative sentiment keywords
        negative_keywords = ["angry", "mad", "frustrated", "terrible", "awful", "worst", "hate", "horrible"]
        sentiment = "negative" if any(word in query_lower for word in negative_keywords) else "neutral"

        # Find matching intent
        primary_intent = "general_inquiry"
        for intent, keywords in intent_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                primary_intent = intent
                break

        return {
            "primary_intent": primary_intent,
            "sentiment": sentiment,
            "urgency": "high" if sentiment == "negative" else "medium",
            "topic_category": "walmart_related"
        }

    def enhance_query_for_retrieval(self, query: str, intent_data: dict) -> str:
        """Fast query enhancement with pre-defined mappings"""
        enhanced_query = query

        # Simple synonym addition based on intent
        intent_synonyms = {
            "return": " refund exchange policy",
            "hours": " store hours opening closing time",
            "location": " address store location",
            "contact": " phone number customer service",
            "price": " cost pricing how much",
        }

        primary_intent = intent_data.get("primary_intent", "")
        if primary_intent in intent_synonyms:
            enhanced_query += intent_synonyms[primary_intent]

        return enhanced_query


# --- OPTIMIZED ROUTER ---
class FastRouter:
    def __init__(self):
        # Pre-define topic keywords to avoid LLM calls
        self.walmart_keywords = {
            "walmart", "store", "product", "price", "return", "refund", "exchange",
            "hours", "location", "contact", "customer service", "shopping", "buy",
            "purchase", "order", "delivery", "pickup", "pharmacy", "vision center",
            "auto center", "grocery", "electronics", "clothing", "home", "garden"
        }

        # Cache for off-topic detection
        self.topic_cache = {}

    def is_off_topic_fast(self, query: str) -> bool:
        """Fast off-topic detection without LLM calls"""
        query_lower = query.lower()

        # Check cache first
        if query_lower in self.topic_cache:
            return self.topic_cache[query_lower]

        # Check if query contains Walmart-related terms
        is_related = any(keyword in query_lower for keyword in self.walmart_keywords)

        # Cache result
        self.topic_cache[query_lower] = not is_related
        return not is_related

    def select_prompt_template(self, query: str, intent_data: dict) -> tuple:
        """Fast template selection based on rules"""

        # Check if off-topic using fast method
        if self.is_off_topic_fast(query):
            return prompt_templates.safety_guardrail_template, "guardrail"

        # Check sentiment for escalation
        sentiment = intent_data.get("sentiment", "neutral").lower()
        if sentiment == "negative":
            return prompt_templates.empathetic_deescalation_template, "escalation"

        # Route based on primary intent
        primary_intent = intent_data.get("primary_intent", "").lower()

        intent_routing = {
            "comparison": (prompt_templates.product_comparison_template, "comparison_rag"),
            "how_to": (prompt_templates.step_by_step_guide_template, "guide_rag"),
            "hours": (prompt_templates.store_info_template, "store_info_rag"),
            "location": (prompt_templates.store_info_template, "store_info_rag"),
            "contact": (prompt_templates.store_info_template, "store_info_rag"),
            "return": (prompt_templates.return_policy_template, "return_rag"),
        }

        if primary_intent in intent_routing:
            return intent_routing[primary_intent]

        # Default to conversational RAG
        return prompt_templates.enhanced_conversational_rag_template, "standard_rag"


# --- INITIALIZE OPTIMIZED COMPONENTS ---
query_processor = OptimizedQueryProcessor()
fast_router = FastRouter()


# --- CONVERSATIONAL RAG CHAIN ---
def create_conversational_chain(retriever):
    if not retriever:
        return None
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, prompt_templates.history_rephrase_template
    )
    question_answer_chain = create_stuff_documents_chain(
        llm, prompt_templates.enhanced_conversational_rag_template
    )
    return create_retrieval_chain(history_aware_retriever, question_answer_chain)


conversational_rag_chain = create_conversational_chain(retriever)


# --- OPTIMIZED HELPER FUNCTIONS ---
def detect_language_fast(text: str) -> str:
    """Fast language detection with caching"""
    if not hasattr(detect_language_fast, "cache"):
        detect_language_fast.cache = {}

    text_key = text[:50]  # Use first 50 chars as key
    if text_key in detect_language_fast.cache:
        return detect_language_fast.cache[text_key]

    try:
        lang = detect(text)
        detect_language_fast.cache[text_key] = lang
        return lang
    except LangDetectException:
        return 'en'


def translate_text_fast(text: str, target_lang: str) -> str:
    """Fast translation with caching"""
    if not hasattr(translate_text_fast, "cache"):
        translate_text_fast.cache = {}

    cache_key = f"{text[:100]}_{target_lang}"
    if cache_key in translate_text_fast.cache:
        return translate_text_fast.cache[cache_key]

    prompt = f"Translate to {target_lang}: {text}"
    try:
        result = llm.invoke(prompt).content.strip()
        translate_text_fast.cache[cache_key] = result
        return result
    except Exception:
        return text  # Return original if translation fails


# --- OPTIMIZED CORE LOGIC ---
def get_smart_answer(query: str, chat_history: list):
    """Optimized query processing with minimal LLM calls"""

    try:
        # Step 1: Fast query normalization
        normalized_query = query_processor.normalize_query(query)

        # Step 2: Fast intent detection (no LLM call)
        intent_data = query_processor.get_basic_intent(normalized_query)

        # Step 3: Fast template selection
        chosen_prompt, category = fast_router.select_prompt_template(normalized_query, intent_data)

        # Step 4: Handle non-RAG categories
        if category in ["guardrail", "escalation"]:
            chain = chosen_prompt | llm | StrOutputParser()
            response_text = chain.invoke({"question": query})
            new_chat_history = chat_history + [HumanMessage(content=query), AIMessage(content=response_text)]
            return response_text, [], category, new_chat_history

        # Step 5: Handle RAG-based categories
        if category.endswith("_rag"):
            if not conversational_rag_chain:
                return "I'm currently unable to access my knowledge base. Please try again.", [], "error", chat_history

            # Fast language detection
            original_lang = detect_language_fast(query)
            query_en = translate_text_fast(query, 'en') if original_lang != 'en' else query

            # Fast query enhancement
            enhanced_query = query_processor.enhance_query_for_retrieval(query_en, intent_data)

            # RAG chain invocation
            result = conversational_rag_chain.invoke({
                "input": enhanced_query,
                "chat_history": chat_history
            })
            answer = result["answer"]
            sources = result.get("context", [])

            # Fast translation back if needed
            if original_lang != 'en':
                answer = translate_text_fast(answer, original_lang)

            new_chat_history = chat_history + [HumanMessage(content=query), AIMessage(content=answer)]
            return answer, sources, category, new_chat_history

        return "I'm not sure how to help with that.", [], "error", chat_history

    except Exception as e:
        print(f"Error in get_smart_answer: {e}")
        return "I encountered an error. Please try again.", [], "error", chat_history


# --- ASYNC MAIN EXECUTION FOR BETTER RESPONSIVENESS ---
class AsyncChatInterface:
    def __init__(self):
        self.chat_history = []
        self.processing = False

    def display_thinking(self):
        """Show thinking indicator"""
        print("AI: Thinking...", end="", flush=True)

    def clear_thinking(self):
        """Clear thinking indicator"""
        print("\r" + " " * 20 + "\r", end="", flush=True)

    def process_query_async(self, query):
        """Process query asynchronously"""
        self.processing = True
        self.display_thinking()

        try:
            answer, sources, category, self.chat_history = get_smart_answer(query, self.chat_history)

            self.clear_thinking()
            print(f"AI: {answer}")

            # Optional: Show debug info
            if os.getenv("DEBUG_MODE", "false").lower() == "true":
                intent_data = query_processor.get_basic_intent(query)
                print(f"[DEBUG] Intent: {intent_data.get('primary_intent')}, Category: {category}")

        except Exception as e:
            self.clear_thinking()
            print(f"AI: I encountered an error: {e}")
        finally:
            self.processing = False

    def run_interactive(self):
        """Run interactive mode with better responsiveness"""
        print("\n--- Interactive Mode ---")
        print("AI: Hello! I'm Wally, your Walmart support assistant. How can I help? (Type 'exit' to quit)")

        while True:
            try:
                # Show prompt immediately
                user_query = input("You: ")

                if user_query.lower() == 'exit':
                    break

                if not user_query.strip():
                    continue

                # Process query
                self.process_query_async(user_query)

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue


# --- EVALUATION FUNCTIONS (SIMPLIFIED) ---
def evaluate_with_llm(prompt: str, response: str, criteria: str) -> tuple:
    """Simplified evaluation"""
    evaluator_prompt = f"""
    Evaluate if this response meets the criteria:

    User: "{prompt}"
    AI: "{response}"
    Criteria: "{criteria}"

    Respond with 'PASS' or 'FAIL' and brief reason.
    """

    try:
        evaluation = llm.invoke(evaluator_prompt).content.strip()
        is_pass = "PASS" in evaluation.upper()
        return is_pass, evaluation
    except Exception as e:
        return False, f"Evaluation error: {e}"


def run_all_tests(test_file_path: str):
    """Optimized test runner"""
    try:
        test_cases_df = pd.read_csv(test_file_path)
        print(f"Running {len(test_cases_df)} test cases...")
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
        convo_id = row.get('conversation_id', case_id)

        current_history = chat_histories.get(convo_id, [])

        print(f"Test {case_id}/{len(test_cases_df)}: ", end="", flush=True)

        # Get response
        response, _, detected_category, new_history = get_smart_answer(prompt, current_history)
        chat_histories[convo_id] = new_history

        # Quick evaluation
        passed, justification = evaluate_with_llm(prompt, response, criteria)

        status = "✅" if passed else "❌"
        print(f"{status}")

        results.append({"ID": case_id, "Category": category, "Passed": passed})

    # Quick summary
    report_df = pd.DataFrame(results)
    total_passed = report_df['Passed'].sum()
    total_tests = len(report_df)
    print(f"\nResults: {total_passed}/{total_tests} passed ({total_passed / total_tests * 100:.1f}%)")


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Use the async interface for better responsiveness
    chat_interface = AsyncChatInterface()
    chat_interface.run_interactive()
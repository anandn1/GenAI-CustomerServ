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
from typing import List, Dict, Tuple, Optional

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
    max_tokens=2000,
    request_timeout=30,
    max_retries=2,
    default_headers={}
)

# Initialize vectorstore
try:
    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=os.getenv("PINECONE_INDEX"),
        embedding=embedding,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})  # Increased for better context
except Exception as e:
    print(f"Error connecting to Pinecone: {e}. RAG functionality will be disabled.")
    retriever = None


# --- ENHANCED CHAT HISTORY MANAGER ---
class ChatHistoryManager:
    def __init__(self, max_history_length: int = 10):
        self.max_history_length = max_history_length

    def format_chat_history(self, chat_history: List) -> str:
        """Format chat history for prompt inclusion"""
        if not chat_history:
            return "No previous conversation."

        formatted_history = []
        for i in range(0, len(chat_history), 2):
            if i + 1 < len(chat_history):
                human_msg = chat_history[i]
                ai_msg = chat_history[i + 1]
                formatted_history.append(f"Human: {human_msg.content}")
                formatted_history.append(f"Assistant: {ai_msg.content}")

        return "\n".join(formatted_history)

    def truncate_history(self, chat_history: List) -> List:
        """Keep only the most recent conversations to prevent context overflow"""
        if len(chat_history) > self.max_history_length * 2:  # *2 because each exchange is 2 messages
            return chat_history[-(self.max_history_length * 2):]
        return chat_history

    def extract_context_from_history(self, chat_history: List, current_query: str) -> str:
        """Extract relevant context from chat history for follow-up questions"""
        if not chat_history:
            return current_query

        # Get the last few exchanges for context
        recent_history = chat_history[-6:] if len(chat_history) > 6 else chat_history

        # Check if current query is likely a follow-up
        follow_up_indicators = [
            "that", "it", "this", "they", "them", "what about", "how about",
            "and", "also", "too", "same", "similar", "like that", "as well"
        ]

        query_lower = current_query.lower()
        is_follow_up = any(indicator in query_lower for indicator in follow_up_indicators)

        if is_follow_up and recent_history:
            # Extract the last topic discussed
            last_ai_response = ""
            for msg in reversed(recent_history):
                if isinstance(msg, AIMessage):
                    last_ai_response = msg.content
                    break

            # Add context to the query
            if last_ai_response:
                return f"Previous context: {last_ai_response[:200]}...\n\nCurrent question: {current_query}"

        return current_query


# --- OPTIMIZED QUERY PROCESSOR ---
class OptimizedQueryProcessor:
    def __init__(self):
        self.whitespace_pattern = re.compile(r'\s+')
        self.abbreviation_patterns = self._compile_abbreviation_patterns()
        self.intent_cache = {}
        self.chat_history_manager = ChatHistoryManager()

    def _compile_abbreviation_patterns(self):
        """Pre-compile regex patterns for abbreviations"""
        abbreviations = {
            'refund': 'return',
            'exchange': 'return',
            'swap': 'return',
            'hrs': 'hours',
            'phone': 'contact',
            'call': 'contact',
            'thx': 'thanks',
            'u': 'you',
            'ur': 'your',
            'w/': 'with',
            'info': 'information'
        }

        patterns = {}
        for abbrev, full in abbreviations.items():
            patterns[full] = re.compile(r'\b' + re.escape(abbrev) + r'\b', re.IGNORECASE)

        return patterns

    def normalize_query(self, query: str) -> str:
        """Fast query normalization with cached patterns"""
        # Remove extra whitespace
        normalized = self.whitespace_pattern.sub(' ', query.strip())

        # Apply abbreviation replacements
        for replacement, pattern in self.abbreviation_patterns.items():
            normalized = pattern.sub(replacement, normalized)

        return normalized

    def detect_follow_up_type(self, query: str, chat_history: List) -> Dict:
        """Detect if this is a follow-up question and what type"""
        query_lower = query.lower()

        follow_up_patterns = {
            "clarification": ["what do you mean", "can you explain", "i don't understand", "clarify"],
            "additional_info": ["what about", "how about", "and", "also", "tell me more"],
            "comparison": ["vs", "versus", "compared to", "difference", "better", "or"],
            "related_question": ["that", "it", "this", "they", "them", "same", "similar"],
            "continuation": ["next", "then", "after that", "what happens", "continue"]
        }

        for follow_up_type, patterns in follow_up_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                return {
                    "is_follow_up": True,
                    "follow_up_type": follow_up_type,
                    "needs_context": True
                }

        return {"is_follow_up": False, "follow_up_type": None, "needs_context": False}

    def get_enhanced_intent(self, query: str, chat_history: List) -> dict:
        """Enhanced intent detection with conversation context"""
        query_lower = query.lower()

        # Check if this is a follow-up
        follow_up_info = self.detect_follow_up_type(query, chat_history)

        # Define keyword patterns for common intents
        intent_patterns = {
            "return": ["return", "refund", "exchange", "bring back", "send back", "give back"],
            "hours": ["hours", "open", "close", "time", "when"],
            "location": ["where", "address", "location", "find", "directions"],
            "contact": ["phone", "call", "contact", "speak", "talk"],
            "price": ["price", "cost", "how much", "expensive", "cheap"],
            "comparison": ["vs", "versus", "compare", "difference", "better", "or"],
            "availability": ["available", "stock", "in store", "do you have", "carry"],
            "how_to": ["how", "steps", "guide", "process", "way to"],
            "product_info": ["product", "item", "specification", "details", "features"],
            "service_info": ["service", "department", "pharmacy", "vision", "auto"]
        }

        # Check for negative sentiment keywords
        negative_keywords = ["angry", "mad", "frustrated", "terrible", "awful", "worst", "hate", "horrible",
                             "disappointed"]
        urgent_keywords = ["urgent", "asap", "immediately", "emergency", "now", "quick"]

        sentiment = "negative" if any(word in query_lower for word in negative_keywords) else "neutral"
        urgency = "high" if any(
            word in query_lower for word in urgent_keywords) or sentiment == "negative" else "medium"

        # Find matching intent
        primary_intent = "general_inquiry"
        for intent, keywords in intent_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                primary_intent = intent
                break

        # If it's a follow-up, try to infer intent from context
        if follow_up_info["is_follow_up"] and chat_history:
            # Look at the last AI response to understand context
            for msg in reversed(chat_history):
                if isinstance(msg, AIMessage):
                    last_response = msg.content.lower()
                    for intent, keywords in intent_patterns.items():
                        if any(keyword in last_response for keyword in keywords):
                            primary_intent = intent
                            break
                    break

        return {
            "primary_intent": primary_intent,
            "sentiment": sentiment,
            "urgency": urgency,
            "topic_category": "walmart_related",
            "is_follow_up": follow_up_info["is_follow_up"],
            "follow_up_type": follow_up_info["follow_up_type"],
            "needs_context": follow_up_info["needs_context"]
        }

    def enhance_query_for_retrieval(self, query: str, intent_data: dict, chat_history: List) -> str:
        """Enhanced query enhancement with conversation context"""
        enhanced_query = query

        # Add context if it's a follow-up question
        if intent_data.get("needs_context", False):
            enhanced_query = self.chat_history_manager.extract_context_from_history(
                chat_history, query
            )

        # Add intent-specific synonyms
        intent_synonyms = {
            "return": " refund exchange policy process steps requirements",
            "hours": " store hours opening closing time schedule",
            "location": " address store location directions",
            "contact": " phone number customer service support",
            "price": " cost pricing how much money",
            "product_info": " product details specifications features",
            "service_info": " service department available"
        }

        primary_intent = intent_data.get("primary_intent", "")
        if primary_intent in intent_synonyms:
            enhanced_query += intent_synonyms[primary_intent]

        return enhanced_query


# --- ENHANCED ROUTER ---
class EnhancedRouter:
    def __init__(self):
        self.walmart_keywords = {
            "walmart", "store", "product", "price", "return", "refund", "exchange",
            "hours", "location", "contact", "customer service", "shopping", "buy",
            "purchase", "order", "delivery", "pickup", "pharmacy", "vision center",
            "auto center", "grocery", "electronics", "clothing", "home", "garden",
            "great value", "equate", "ozark trail", "supercenter", "neighborhood market"
        }
        self.topic_cache = {}

    def is_off_topic_fast(self, query: str, chat_history: List) -> bool:
        """Enhanced off-topic detection with conversation context"""
        query_lower = query.lower()

        # Check cache first
        if query_lower in self.topic_cache:
            return self.topic_cache[query_lower]

        # Check if query contains Walmart-related terms
        is_related = any(keyword in query_lower for keyword in self.walmart_keywords)

        # If not obviously related, check if it's a follow-up to a Walmart conversation
        if not is_related and chat_history:
            # Check the last few messages for Walmart context
            recent_messages = chat_history[-4:] if len(chat_history) > 4 else chat_history
            for msg in recent_messages:
                if isinstance(msg, (HumanMessage, AIMessage)):
                    msg_lower = msg.content.lower()
                    if any(keyword in msg_lower for keyword in self.walmart_keywords):
                        is_related = True
                        break

        # Cache result
        self.topic_cache[query_lower] = not is_related
        return not is_related

    def select_prompt_template(self, query: str, intent_data: dict, chat_history: List) -> tuple:
        """Enhanced template selection with conversation context"""

        # Check if off-topic using enhanced method
        if self.is_off_topic_fast(query, chat_history):
            return prompt_templates.safety_guardrail_template, "guardrail"

        # Check sentiment for escalation
        sentiment = intent_data.get("sentiment", "neutral").lower()
        if sentiment == "negative":
            return prompt_templates.empathetic_deescalation_template, "escalation"

        # Handle follow-up questions
        if intent_data.get("is_follow_up", False):
            follow_up_type = intent_data.get("follow_up_type", "")

            if follow_up_type == "comparison":
                return prompt_templates.product_comparison_template, "comparison_rag"
            elif follow_up_type == "clarification":
                return prompt_templates.clarification_template, "clarification_rag"
            elif follow_up_type in ["additional_info", "related_question", "continuation"]:
                return prompt_templates.enhanced_conversational_rag_template, "followup_rag"

        # Route based on primary intent
        primary_intent = intent_data.get("primary_intent", "").lower()

        intent_routing = {
            "comparison": (prompt_templates.product_comparison_template, "comparison_rag"),
            "how_to": (prompt_templates.step_by_step_guide_template, "guide_rag"),
            "hours": (prompt_templates.store_info_template, "store_info_rag"),
            "location": (prompt_templates.store_info_template, "store_info_rag"),
            "contact": (prompt_templates.store_info_template, "store_info_rag"),
            "return": (prompt_templates.return_policy_template, "return_rag"),
            "service_info": (prompt_templates.store_info_template, "store_info_rag"),
            "product_info": (prompt_templates.enhanced_conversational_rag_template, "product_rag"),
        }

        if primary_intent in intent_routing:
            return intent_routing[primary_intent]

        # Default to conversational RAG
        return prompt_templates.enhanced_conversational_rag_template, "standard_rag"


# --- INITIALIZE ENHANCED COMPONENTS ---
query_processor = OptimizedQueryProcessor()
enhanced_router = EnhancedRouter()


# --- ENHANCED CONVERSATIONAL RAG CHAIN ---
def create_enhanced_conversational_chain(retriever):
    """Create RAG chain with better history handling"""
    if not retriever:
        return None

    # Enhanced history-aware retriever
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, prompt_templates.history_rephrase_template
    )

    # Enhanced question-answer chain
    question_answer_chain = create_stuff_documents_chain(
        llm, prompt_templates.enhanced_conversational_rag_template
    )

    return create_retrieval_chain(history_aware_retriever, question_answer_chain)


conversational_rag_chain = create_enhanced_conversational_chain(retriever)


# --- OPTIMIZED HELPER FUNCTIONS ---
def detect_language_fast(text: str) -> str:
    """Fast language detection with caching"""
    if not hasattr(detect_language_fast, "cache"):
        detect_language_fast.cache = {}

    text_key = text[:50]
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
        return text


# --- ENHANCED CORE LOGIC ---
def get_smart_answer(query: str, chat_history: list):
    """Enhanced query processing with proper conversation handling"""

    try:
        # Step 1: Truncate chat history to prevent context overflow
        chat_history = query_processor.chat_history_manager.truncate_history(chat_history)

        # Step 2: Normalize query
        normalized_query = query_processor.normalize_query(query)

        # Step 3: Enhanced intent detection with conversation context
        intent_data = query_processor.get_enhanced_intent(normalized_query, chat_history)

        # Step 4: Enhanced template selection
        chosen_prompt, category = enhanced_router.select_prompt_template(
            normalized_query, intent_data, chat_history
        )

        # Step 5: Handle non-RAG categories
        if category in ["guardrail", "escalation"]:
            chain = chosen_prompt | llm | StrOutputParser()
            response_text = chain.invoke({"question": query})
            new_chat_history = chat_history + [HumanMessage(content=query), AIMessage(content=response_text)]
            return response_text, [], category, new_chat_history

        # Step 6: Handle RAG-based categories with enhanced context
        if category.endswith("_rag"):
            if not conversational_rag_chain:
                return "I'm currently unable to access my knowledge base. Please try again.", [], "error", chat_history

            # Language detection
            original_lang = detect_language_fast(query)
            query_en = translate_text_fast(query, 'en') if original_lang != 'en' else query

            # Enhanced query enhancement with conversation context
            enhanced_query = query_processor.enhance_query_for_retrieval(
                query_en, intent_data, chat_history
            )

            # Prepare chat history for the chain
            formatted_history = query_processor.chat_history_manager.format_chat_history(chat_history)

            # RAG chain invocation with enhanced context
            result = conversational_rag_chain.invoke({
                "input": enhanced_query,
                "chat_history": formatted_history
            })

            answer = result["answer"]
            sources = result.get("context", [])

            # Handle follow-up context
            if intent_data.get("is_follow_up", False):
                follow_up_type = intent_data.get("follow_up_type", "")
                if follow_up_type == "clarification":
                    answer = f"To clarify: {answer}"
                elif follow_up_type == "additional_info":
                    answer = f"Additionally: {answer}"

            # Translate back if needed
            if original_lang != 'en':
                answer = translate_text_fast(answer, original_lang)

            new_chat_history = chat_history + [HumanMessage(content=query), AIMessage(content=answer)]
            return answer, sources, category, new_chat_history

        return "I'm not sure how to help with that.", [], "error", chat_history

    except Exception as e:
        print(f"Error in get_smart_answer: {e}")
        return "I encountered an error. Please try again.", [], "error", chat_history


# --- ENHANCED ASYNC CHAT INTERFACE ---
class EnhancedChatInterface:
    def __init__(self):
        self.chat_history = []
        self.processing = False
        self.conversation_summary = ""

    def display_thinking(self):
        """Show thinking indicator"""
        print("AI: Thinking...", end="", flush=True)

    def clear_thinking(self):
        """Clear thinking indicator"""
        print("\r" + " " * 20 + "\r", end="", flush=True)

    def show_conversation_context(self):
        """Show brief conversation context"""
        if len(self.chat_history) > 0:
            print(f"\n[Conversation length: {len(self.chat_history) // 2} exchanges]")

    def process_query_async(self, query):
        """Enhanced query processing with better context handling"""
        self.processing = True
        self.display_thinking()

        try:
            answer, sources, category, self.chat_history = get_smart_answer(query, self.chat_history)

            self.clear_thinking()
            print(f"AI: {answer}")

            # Show debug info if enabled
            if os.getenv("DEBUG_MODE", "false").lower() == "true":
                intent_data = query_processor.get_enhanced_intent(query, self.chat_history[:-2])
                print(f"[DEBUG] Intent: {intent_data.get('primary_intent')}, Category: {category}")
                print(
                    f"[DEBUG] Follow-up: {intent_data.get('is_follow_up')}, Type: {intent_data.get('follow_up_type')}")
                if sources:
                    print(f"[DEBUG] Sources: {len(sources)} documents retrieved")

        except Exception as e:
            self.clear_thinking()
            print(f"AI: I encountered an error: {e}")
        finally:
            self.processing = False

    def reset_conversation(self):
        """Reset the conversation"""
        self.chat_history = []
        self.conversation_summary = ""
        print("\n[Conversation reset]")

    def run_interactive(self):
        """Enhanced interactive mode"""
        print("\n--- Enhanced Interactive Mode ---")
        print("AI: Hello! I'm Wally, your Walmart support assistant.")
        print("I can help with products, returns, store information, and more.")
        print("I'll remember our conversation context for follow-up questions.")
        print("Commands: 'exit' to quit, 'reset' to start fresh, 'history' to see conversation length")
        print("How can I help you today?")

        while True:
            try:
                user_query = input("\nYou: ")

                if user_query.lower() == 'exit':
                    print("AI: Thank you for using Walmart support! Have a great day!")
                    break
                elif user_query.lower() == 'reset':
                    self.reset_conversation()
                    continue
                elif user_query.lower() == 'history':
                    self.show_conversation_context()
                    continue

                if not user_query.strip():
                    continue

                self.process_query_async(user_query)

            except KeyboardInterrupt:
                print("\n\nAI: Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue


# --- EVALUATION FUNCTIONS ---
def evaluate_with_llm(prompt: str, response: str, criteria: str) -> tuple:
    """Enhanced evaluation with context awareness"""
    evaluator_prompt = f"""
    Evaluate this customer service response:

    User: "{prompt}"
    AI: "{response}"
    Criteria: "{criteria}"

    Consider:
    1. Accuracy and helpfulness
    2. Appropriate tone for customer service
    3. Completeness of information
    4. Handling of follow-up context (if applicable)

    Respond with 'PASS' or 'FAIL' and brief reason.
    """

    try:
        evaluation = llm.invoke(evaluator_prompt).content.strip()
        is_pass = "PASS" in evaluation.upper()
        return is_pass, evaluation
    except Exception as e:
        return False, f"Evaluation error: {e}"


def run_enhanced_tests(test_file_path: str):
    """Enhanced test runner with conversation context"""
    try:
        test_cases_df = pd.read_csv(test_file_path)
        print(f"Running {len(test_cases_df)} test cases with conversation context...")
    except FileNotFoundError:
        print(f"Error: Test file not found at {test_file_path}")
        return

    results = []
    conversation_contexts = {}

    for index, row in test_cases_df.iterrows():
        case_id = row['id']
        prompt = row['prompt']
        category = row['category']
        criteria = row['evaluation_criteria']
        convo_id = row.get('conversation_id', case_id)

        # Maintain conversation context
        current_history = conversation_contexts.get(convo_id, [])

        print(f"Test {case_id}/{len(test_cases_df)}: ", end="", flush=True)

        # Get response with conversation context
        response, sources, detected_category, new_history = get_smart_answer(prompt, current_history)
        conversation_contexts[convo_id] = new_history

        # Evaluate response
        passed, justification = evaluate_with_llm(prompt, response, criteria)

        status = "✅" if passed else "❌"
        print(f"{status} ({detected_category})")

        results.append({
            "ID": case_id,
            "Category": category,
            "Detected": detected_category,
            "Passed": passed,
            "Conversation_Length": len(new_history) // 2
        })

    # Enhanced summary
    report_df = pd.DataFrame(results)
    total_passed = report_df['Passed'].sum()
    total_tests = len(report_df)

    print(f"\nResults Summary:")
    print(f"Overall: {total_passed}/{total_tests} passed ({total_passed / total_tests * 100:.1f}%)")
    print(f"Average conversation length: {report_df['Conversation_Length'].mean():.1f} exchanges")

    # Category breakdown
    category_stats = report_df.groupby('Category')['Passed'].agg(['count', 'sum']).reset_index()
    category_stats['Pass_Rate'] = (category_stats['sum'] / category_stats['count'] * 100).round(1)
    print("\nCategory Performance:")
    for _, row in category_stats.iterrows():
        print(f"  {row['Category']}: {row['sum']}/{row['count']} ({row['Pass_Rate']}%)")


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Use the enhanced interface
    chat_interface = EnhancedChatInterface()

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_file = sys.argv[2] if len(sys.argv) > 2 else "test_cases.csv"
        run_enhanced_tests(test_file)
    else:
        chat_interface.run_interactive()
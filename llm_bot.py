# llm_bot.py - MindMate AI Engine v2.0
# ✅ google-genai (new) | ✅ Streaming | ✅ Crisis Detection | ✅ Memory

import json
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from emotion_engine import EmotionAnalyzer
from crisis_engine import CrisisDetector
from memory_engine import LongTermMemory
load_dotenv()

# ==========================================
# Gemini Setup
# ==========================================
def get_client():
    # Attempt to load the API key explicitly from the environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Fail fast and explicitly if the API key is not found
    # This prevents silent fallbacks to rate-limited or compromised keys
    if not api_key:
        raise ValueError("CRITICAL ERROR: GEMINI_API_KEY is not set. Please ensure the .env file is present in the root directory and properly formatted.")
        
    # Initialize and return the Gemini client with the valid key
    return genai.Client(api_key=api_key)

MODEL = "gemini-3.1-flash-lite"

# Initialize the NLP emotion engine globally
try:
    print("Loading Local NLP Emotion Engine...")
    emotion_analyzer = EmotionAnalyzer()
except Exception as e:
    print(f"Failed to load Emotion Engine: {e}")
    emotion_analyzer = None

# Initialize the NLP crisis engine globally
try:
    print("Loading Local NLP Crisis Engine...")
    crisis_analyzer = CrisisDetector()
except Exception as e:
    print(f"Failed to load Crisis Engine: {e}")
    crisis_analyzer = None

# Initialize the Long-Term Vector Memory Engine globally
try:
    print("Initializing Long-Term Vector Memory (ChromaDB)...")
    memory_engine = LongTermMemory()
except Exception as e:
    print(f"Failed to load Long-Term Memory: {e}")
    memory_engine = None

# ==========================================
# Crisis Detection
# ==========================================
CRISIS_KEYWORDS = {
    "severe": [
        "عايز أموت", "نفسي أموت", "هقتل نفسي", "مش عايز أعيش",
        "هاذي نفسي", "تعبت من الحياة", "مش لاقي معنى للحياة",
        "أحسن لو متم", "مش قادر أكمل", "حياتي مش تسوى",
        "want to die", "kill myself", "end my life"
    ],
    "moderate": [
        "تعبت جداً", "مش قادر", "كل حاجة وحشة", "مفيش فايدة",
        "محدش فاهمني", "لوحدي تماماً", "زهقت من كل حاجة",
        "مش عارف أكمل", "حاسس بضياع تام"
    ],
    "mild": [
        "زهقت", "تعبان", "مش كويس", "حاسس بوحدة",
        "قلقان", "خايف", "محبطط", "مكتئب"
    ]
}

def detect_crisis_fast(text):
    """
    Hybrid detection approach: evaluates explicit rules first, 
    then utilizes the NLP model for semantic analysis.
    """
    text_lower = text.lower()
    
    # Layer 1: Rule-based exact keyword matching for guaranteed safety
    for level in ["severe", "moderate", "mild"]:
        for keyword in CRISIS_KEYWORDS[level]:
            if keyword in text_lower:
                print(f"Crisis Detected via Keywords: {level}")
                return level
                
    # Layer 2: Semantic analysis using the PyTorch-based NLP engine
    if crisis_analyzer:
        nlp_level = crisis_analyzer.analyze_risk_level(text)
        if nlp_level in ["severe", "moderate"]:
            print(f"Crisis Detected via NLP Model: {nlp_level}")
            return nlp_level
            
    return "none"

# ==========================================
# Memory Context
# ==========================================
def _build_memory_context(chat_history):
    if not chat_history:
        return "محادثة جديدة"
    recent_cutoff = 10
    if len(chat_history) <= recent_cutoff:
        lines = []
        for msg in chat_history:
            role = "المستخدم" if msg["role"] == "user" else "MindMate"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)
    else:
        old = chat_history[:-recent_cutoff]
        recent = chat_history[-recent_cutoff:]
        summary = f"[ملخص {len(old)} رسالة: "
        user_msgs = [m["content"][:50] for m in old if m["role"] == "user"]
        summary += " | ".join(user_msgs[-3:]) + "...]"
        lines = []
        for msg in recent:
            role = "المستخدم" if msg["role"] == "user" else "MindMate"
            lines.append(f"{role}: {msg['content']}")
        return summary + "\n" + "\n".join(lines)

# ==========================================
# Crisis Response
# ==========================================
def _generate_crisis_response(client, user_text, user_name, level):
    prompt = f"""
أنت MindMate، مساعد دعم نفسي متخصص.
المستخدم ({user_name}) في حالة أزمة نفسية. قال: "{user_text}"
اكتب رد دعم نفسي بالعربي المصري يشمل:
1. تعاطف عميق وصادق
2. تأكيد إن الشخص مش لوحده
3. نصيحة عملية فورية
4. خط نجدة الصحة النفسية المصري: 08008880700
الأسلوب: دافي وإنساني، مش طبي ومش رسمي.
"""
    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return "🆘 " + response.text
    except:
        return f"🆘 يا {user_name}، أنا سامعك وحاسس بيك. مش لوحدك. كلم خط نجدة الصحة النفسية: 08008880700 💙"

# ==========================================
# MAIN FUNCTION (Fallback)
# ==========================================
def process_message(user_text, current_data, chat_history=None, user_name="صديقي", user_id=1):
    client = get_client()
    crisis_level = detect_crisis_fast(user_text)

    # 1. save user message to long-term memory for future context and learning
    if memory_engine:
        memory_engine.save_message(client, user_id, "user", user_text)

    # 2. retrieve relevant long-term memories to enrich the context for the LLM response
    long_term_context = ""
    if memory_engine:
        long_term_context = memory_engine.retrieve_context(client, user_id, user_text, n_results=3)

    # 3. analyze user emotion using the local HuggingFace NLP model
    nlp_emotion = "غير محدد"
    if emotion_analyzer:
        analysis_result = emotion_analyzer.analyze_text(user_text)
        nlp_emotion = analysis_result.get("primary_emotion", "غير محدد")
        confidence = analysis_result.get("confidence", 0.0)
        print(f"NLP Emotion Detected (Fallback): {nlp_emotion} (Confidence: {confidence:.2f})")

    if crisis_level == "severe":
        crisis_reply = _generate_crisis_response(client, user_text, user_name, "severe")
        if memory_engine:
            memory_engine.save_message(client, user_id, "assistant", crisis_reply)
        return {
            "extracted_metrics": {},
            "mood": {"emoji": "😔", "color": "#FF000080", "category": "أزمة"},
            "reply": crisis_reply,
            "crisis_level": "severe"
        }

    labels_map = {
        "sleep_hours": "نوم", "study_hours": "مذاكرة",
        "screen_hours": "موبايل", "meal_count": "وجبات",
        "water_cups": "مياه", "social_hours": "تواصل",
        "exercise_minutes": "رياضة", "stress_level": "ضغط نفسي"
    }

    data_str = ", ".join([
        f"{labels_map.get(k, k)}: {v}"
        for k, v in current_data.items() if v is not None
    ]) or "لا يوجد بيانات بعد"

    # Identify which key metrics are still missing to prompt the user for them in a natural way
    missing_keys = [k for k, v in current_data.items() if v is None and k in labels_map]
    missing_str = " و ".join([labels_map[k] for k in missing_keys[:2]])
    
    # short term context
    short_term_context = _build_memory_context(chat_history)

    # 4. Construct the mega prompt with all context layers and instructions for the LLM to generate a comprehensive response
    mega_prompt = f"""
أنت MindMate، مساعد ذكي للدعم النفسي وتتبع العادات.
اسم المستخدم: {user_name}
بيانات اليوم: {data_str}
{"البيانات المطلوبة الآن: " + missing_str if missing_str else "البيانات اليومية مكتملة ✅"}

⏱️ سياق المحادثة القصير (آخر رسائل):
{short_term_context}

📚 ذكريات وسياقات مأخوذة من أسابيع مضت ذات صلة دلالية بكلام المستخدم الحالي:
{long_term_context if long_term_context else "لا توجد ذكريات سابقة مطابقة دلالياً."}

آخر رسالة من المستخدم: "{user_text}"

💡 تحليل المشاعر المستقل (NLP Engine): المستخدم يغلب عليه شعور بـ ({nlp_emotion}). استخدم هذه المعلومة لضبط نبرة ردك.

{"⚠️ المستخدم في حالة " + crisis_level + " - ابدأ بالدعم النفسي." if crisis_level != "none" else ""}

رد بـ JSON فقط بهذا الشكل:
{{
    "extracted_metrics": {{
        "sleep_hours": number أو null,
        "study_hours": number أو null,
        "screen_hours": number أو null,
        "meal_count": number أو null,
        "water_cups": number أو null,
        "social_hours": number أو null,
        "exercise_minutes": number أو null,
        "stress_level": number بين 1-10 أو null
    }},
    "mood": {{
        "emoji": "إيموجي",
        "color": "#hexcolor",
        "category": "كلمة بالعربي"
    }},
    "reply": "ردك بالعربي المصري الطبيعي"
}}

تعليمات أساسية للرد:
- عربي مصري طبيعي دافي مش رسمي (زي الصاحب).
{"- 🎯 هام جداً: في ردك، يجب أن تسأل المستخدم بشكل ودي وطبيعي جداً عن (" + missing_str + ") لكي تتمكن من تسجيلها في بيانات اليوم. ادمج السؤال في سياق الكلام." if missing_str else "- ممتاز، جميع البيانات مكتملة، اربط البيانات وقدم نصيحة عملية وذكية بناءً على حالته."}
- 3-8 جمل متدفقة مش نقاط.
- إيموجيز طبيعية.
"""

    try:
        response = client.models.generate_content(model=MODEL, contents=mega_prompt)
        content = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(content)
        clean_metrics = {k: v for k, v in result.get("extracted_metrics", {}).items() if v is not None}
        
        reply_text = result.get("reply", "معلش، مش فاهم قصدك. ممكن توضح؟")
        
        # 5. save the assistant's reply to long-term memory for future context and learning
        if memory_engine and reply_text:
            memory_engine.save_message(client, user_id, "assistant", reply_text)
            
        return {
            "extracted_metrics": clean_metrics,
            "mood": result.get("mood", {"emoji": "😐", "color": "#E0E0E080", "category": "طبيعي"}),
            "reply": reply_text,
            "crisis_level": crisis_level
        }
    except json.JSONDecodeError:
        try:
            reply_text = response.text
            if memory_engine and reply_text:
                memory_engine.save_message(client, user_id, "assistant", reply_text)
            return {
                "extracted_metrics": {},
                "mood": {"emoji": "😐", "color": "#E0E0E080", "category": "طبيعي"},
                "reply": reply_text,
                "crisis_level": crisis_level
            }
        except:
            pass
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return {
            "extracted_metrics": {},
            "mood": {"emoji": "😐", "color": "#E0E0E080", "category": "طبيعي"},
            "reply": f"في مشكلة: {str(e)}",
            "crisis_level": crisis_level
        }

# ==========================================
# STREAMING VERSION
# ==========================================
def process_message_stream(user_text, current_data, chat_history=None, user_name="صديقي", user_id=1):
    client = get_client()
    crisis_level = detect_crisis_fast(user_text)

    # 1. save user message to long-term memory for future context and learning
    if memory_engine:
        memory_engine.save_message(client, user_id, "user", user_text)

    # 2. retrieve context from long-term memory
    long_term_context = ""
    if memory_engine:
        long_term_context = memory_engine.retrieve_context(client, user_id, user_text, n_results=3)

    # 3. Analyze user emotion using the local HuggingFace NLP model
    nlp_emotion = "غير محدد"
    if emotion_analyzer:
        analysis_result = emotion_analyzer.analyze_text(user_text)
        nlp_emotion = analysis_result.get("primary_emotion", "غير محدد")
        confidence = analysis_result.get("confidence", 0.0)
        print(f"NLP Emotion Detected: {nlp_emotion} (Confidence: {confidence:.2f})")

    # Check for severe crises first (Fall-forward logic)
    if crisis_level == "severe":
        crisis_reply = _generate_crisis_response(client, user_text, user_name, "severe")
        if memory_engine:
            memory_engine.save_message(client, user_id, "assistant", crisis_reply)
        def crisis_stream():
            for word in crisis_reply.split(" "):
                yield word + " "
        return crisis_stream(), {}, {"emoji": "😔", "color": "#FF000080", "category": "أزمة"}, "severe"

    labels_map = {
        "sleep_hours": "نوم", "study_hours": "مذاكرة",
        "screen_hours": "موبايل", "meal_count": "وجبات",
        "water_cups": "مياه", "social_hours": "تواصل",
        "exercise_minutes": "رياضة", "stress_level": "ضغط نفسي"
    }

    data_str = ", ".join([
        f"{labels_map.get(k, k)}: {v}"
        for k, v in current_data.items() if v is not None
    ]) or "لا يوجد بيانات بعد"

    missing_keys = [k for k, v in current_data.items() if v is None and k in labels_map]
    missing_str = " و ".join([labels_map[k] for k in missing_keys[:2]])
    
    # short term context
    short_term_context = _build_memory_context(chat_history)

    extracted_metrics = {}
    mood = {"emoji": "😐", "color": "#E0E0E080", "category": "طبيعي"}

    # Data Extraction Meta Prompt
    try:
        meta_prompt = f"""
Extract data from: "{user_text}"
Return ONLY valid JSON, no markdown:
{{
    "extracted_metrics": {{
        "sleep_hours": number or null,
        "study_hours": number or null,
        "screen_hours": number or null,
        "meal_count": number or null,
        "water_cups": number or null,
        "social_hours": number or null,
        "exercise_minutes": number or null,
        "stress_level": number or null
    }},
    "mood": {{"emoji": "emoji", "color": "#hexcode", "category": "arabic word"}}
}}
"""
        meta_response = client.models.generate_content(
            model=MODEL,
            contents=meta_prompt,
            config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=200)
        )
        meta_content = meta_response.text.replace("```json", "").replace("```", "").strip()
        meta_data = json.loads(meta_content)
        extracted_metrics = {k: v for k, v in meta_data.get("extracted_metrics", {}).items() if v is not None}
        mood = meta_data.get("mood", mood)
    except:
        pass

    # 4. Construct the Main Reply Prompt with injected NLP & Memory context
    reply_prompt = f"""
أنت MindMate، صاحب ذكي ودافي بيتكلم عربي مصري.
اسم المستخدم: {user_name}
بيانات اليوم الحالية: {data_str}
{"البيانات الناقصة المطلوبة الآن: " + missing_str if missing_str else "البيانات مكتملة ✅"}

⏱️ سياق المحادثة القصير (آخر رسائل):
{short_term_context}

📚 ذكريات وسياقات مأخوذة من أسابيع مضت ذات صلة دلالية بكلام المستخدم الحالي:
{long_term_context if long_term_context else "لا توجد ذكريات سابقة مطابقة دلالياً."}

المستخدم قال: "{user_text}"

💡 تحليل المشاعر المستقل (NLP Engine): المستخدم يغلب عليه شعور بـ ({nlp_emotion}). استخدم هذه المعلومة لضبط نبرة ردك.

{"⚠️ المستخدم في حالة " + crisis_level + " - ابدأ بالدعم." if crisis_level != "none" else ""}

تعليمات للرد:
- الرد يكون طبيعي ودافي بالعربي المصري فقط.
{"- 🎯 هام جداً: اسأل المستخدم بأسلوب دردشة طبيعي عن (" + missing_str + ") لكي تكمل بيانات يومه، ادمج السؤال بذكاء في كلامك." if missing_str else "- ممتاز، جميع البيانات مكتملة، اربط البيانات وقدم نصيحة مفيدة."}
- لا تسأل عن كل شيء مرة واحدة، بل ركز على المطلوب حالياً.
- 3-8 جمل متدفقة مش نقاط.
"""

    # 5. Stream the final response and save to DB
    try:
        def stream_generator():
            full_assistant_reply = ""
            for chunk in client.models.generate_content_stream(model=MODEL, contents=reply_prompt):
                if chunk.text:
                    full_assistant_reply += chunk.text
                    yield chunk.text
            
            # حفظ رد المساعد في الذاكرة بعد اكتمال الـ Streaming
            if memory_engine and full_assistant_reply:
                memory_engine.save_message(client, user_id, "assistant", full_assistant_reply)
                
        return stream_generator(), extracted_metrics, mood, crisis_level
    except Exception:
        def error_stream():
            yield "معلش يا صديقي، في مشكلة. حاول تاني. 🙏"
        return error_stream(), extracted_metrics, mood, crisis_level
    
# ==========================================
# Weekly Report
# ==========================================
def generate_weekly_report(weekly_data):
    client = get_client()
    try:
        prompt = f"""
أنت MindMate، محلل نفسي ذكي.
بيانات المستخدم للأسبوع الماضي:
{json.dumps(weekly_data, ensure_ascii=False, indent=2)}

اكتب تقرير أسبوعي شامل بالعربي المصري:
1. 🌟 أبرز إنجازات الأسبوع
2. ⚠️ أكتر حاجتين محتاج تشتغل عليهم
3. 🔗 علاقات بين البيانات
4. 💡 3 نصايح عملية للأسبوع الجاي
5. 💪 جملة تحفيزية ختامية

الأسلوب: دافي وذكي، مش طبي ومش جاف.
"""
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text
    except:
        return "مش قادر أعمل التقرير دلوقتي، جرب تاني."

# ==========================================
# Backward Compatibility
# ==========================================
def extract_metrics_from_text(user_text):
    return process_message(user_text, {})["extracted_metrics"]

def analyze_mood_summary(user_text, current_data):
    return process_message(user_text, current_data)["mood"]

def generate_friend_response(user_text, current_data, chat_history=None, user_name="صديقي"):
    return process_message(user_text, current_data, chat_history, user_name)["reply"]
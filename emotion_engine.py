# emotion_engine.py
from transformers import pipeline
from deep_translator import GoogleTranslator

class EmotionAnalyzer:
    def __init__(self):
        print("Loading Emotion Model...")
        self.classifier = pipeline(
            "text-classification", 
            model="bhadresh-savani/distilbert-base-uncased-emotion", 
            return_all_scores=True
        )
        self.emotion_map = {
            'joy': 'سعادة 😄', 'sadness': 'حزن 😔', 'anger': 'غضب 😡',
            'fear': 'قلق/خوف 😨', 'love': 'حب ❤️', 'surprise': 'دهشة 😲'
        }

    def analyze_text(self, text):
        try:
            # ترجمة لحظية عشان الموديل يفهم العربي
            translated_text = GoogleTranslator(source='auto', target='en').translate(text)
            results = self.classifier(translated_text)
            sorted_emotions = sorted(results[0], key=lambda x: x['score'], reverse=True)
            
            primary_en = sorted_emotions[0]['label']
            
            return {
                "primary_emotion": self.emotion_map.get(primary_en, primary_en),
                "english_label": primary_en,
                "confidence": sorted_emotions[0]['score']
            }
        except Exception as e:
            return {"primary_emotion": "محايد", "english_label": "neutral", "confidence": 0}

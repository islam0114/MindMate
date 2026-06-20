# crisis_engine.py
import torch
from transformers import pipeline

class CrisisDetector:
    def __init__(self):
        """
        Initialize the Zero-Shot Classification pipeline for crisis detection.
        Uses a multilingual RoBERTa model to natively understand Arabic context
        without the strict need for translation steps.
        """
        print("Loading NLP Crisis Detection Model...")
        try:
            # Check for GPU availability to optimize inference speed using PyTorch
            self.device = 0 if torch.cuda.is_available() else -1
            
            # Load a robust multilingual zero-shot classifier
            self.classifier = pipeline(
                "zero-shot-classification",
                model="joeddav/xlm-roberta-large-xnli",
                device=self.device
            )
            
            # Define the target labels representing various mental health states
            self.candidate_labels = [
                "خطر انتحار أو إيذاء النفس", 
                "اكتئاب حاد وحزن شديد", 
                "إرهاق وضغط نفسي", 
                "حالة طبيعية ومستقرة"
            ]
        except Exception as e:
            print(f"Failed to load Crisis Model: {e}")
            self.classifier = None

    def analyze_risk_level(self, text):
        """
        Analyze the text against the candidate labels and determine the crisis level
        based on confidence thresholds.
        """
        if not self.classifier:
            return "unknown"

        try:
            # Perform zero-shot classification on the input text
            result = self.classifier(text, self.candidate_labels)
            
            top_label = result['labels'][0]
            top_score = result['scores'][0]
            
            # Map the highest scoring label to a specific crisis tier
            # Thresholds (e.g., 0.6) are applied to ensure high confidence before flagging
            if top_label == "خطر انتحار أو إيذاء النفس" and top_score > 0.60:
                return "severe"
            elif top_label == "اكتئاب حاد وحزن شديد" and top_score > 0.55:
                return "moderate"
            elif top_label == "إرهاق وضغط نفسي" and top_score > 0.50:
                return "mild"
            else:
                return "none"
                
        except Exception as e:
            print(f"Error during crisis classification inference: {e}")
            return "unknown"
# Importing the transformers library for sentiment analysis
from transformers import pipeline

class PsychologicalCompanion:
    
    # Psychological NLP Engine
    # This handles offline sentiment analysis using a quantized Hugging Face model (DistilBERT). This also includes a conversational response generator that provides emphathetic feedback to patients based on their emotional state, all while ensuring that no sensitive patient data is sent to the cloud.
    # This also fulfills CM3020 edge-native requirements by processing patient emotional data locally, ensuring 100% data privacy without relying on cloud-based APIs.
    
    
    def __init__(self):
        # This initializes a lightweight, pre-trained local neural network model and executes purely on the edge device's CPU after initial caching.
        self.classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    def analyze_sentiment_and_respond(self, patient_text):
        # Executes AI inference on patient audio transcripts and returns a classified sentiment label and an empathetic UI response.
        result = self.classifier(patient_text)[0]
        label = result['label']  # Returns 'POSITIVE' or 'NEGATIVE'
        confidence = result['score']

        # Dynamic behavioral routing based on the neural network's classification
        if label == "POSITIVE":
            return "Motivated", "That is wonderful! Feeling positive is a huge win, and your dedication is seriously paying off. What do you think helped you feel so good during today's session?"
            
        elif label == "NEGATIVE":
            # Lower confidence indicates mixed or conflicting emotional states
            if confidence < 0.80:
                return "Mixed", "Recovery is definitely a balancing act. Every single step counts, even on the confusing days. Are you feeling okay to finish up, or do you need to grab some water first?"
            else:
                # High confidence or negative sentiment triggers a safety/support pathway
                return "Needs Support", "I hear you. It is completely normal to feel drained during recovery, and I'm really proud of you for showing up today even though it was hard. How is your body feeling right now—any specific pain, or just general fatigue?"
import time
import re

class PsychologicalCompanion:
    def __init__(self):
        self.simulated_latency = 1.2 
        self.positive_keywords = ["good", "great", "better", "improving", "okay", "fine", "happy", "easy", "easier", "strong", "motivated", "progress", "confident"]
        self.negative_keywords = ["frustrated", "hard", "tired", "pain", "sad", "bad", "difficult", "tough", "exhausted", "weak", "struggling"]

    def _mock_slm_inference(self, text):
        words = re.findall(r'\b\w+\b', text.lower())
        
        found_positives = [w for w in words if w in self.positive_keywords]
        found_negatives = [w for w in words if w in self.negative_keywords]
        
        if found_negatives and not found_positives:
            primary_emotion = found_negatives[0]
            return "Needs Support", f"I hear you. It is completely normal to feel {primary_emotion} during recovery, and I'm really proud of you for showing up today even though it was hard. How is your body feeling right now—any specific pain, or just general fatigue?"
            
        elif found_positives and not found_negatives:
            primary_emotion = found_positives[0]
            return "Motivated", f"That is wonderful! Feeling {primary_emotion} is a huge win, and your dedication is seriously paying off. I love seeing this energy! What do you think helped you feel so good during today's session?"
            
        elif found_positives and found_negatives:
            return "Mixed", f"Recovery is definitely a balancing act. It makes total sense that you'd feel {found_negatives[0]} but also {found_positives[0]} at the same time. Every single step counts. Are you feeling okay to finish up, or do you need to grab some water first?"
            
        else:
            return "Neutral", "Thanks for sharing that with me. Checking in with yourself is just as important as the physical exercises, and I'm right here with you on this journey. How are your energy levels holding up as we wrap up for the day?"

    def analyze_sentiment_and_respond(self, patient_text):
        time.sleep(self.simulated_latency) 
        sentiment, response = self._mock_slm_inference(patient_text)
        return sentiment, response
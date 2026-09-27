# Importing unittest for testing the Psychological Companion module
import unittest
from psychology import PsychologicalCompanion

class TestPsychologicalCompanion(unittest.TestCase):
    def setUp(self):
        self.psych = PsychologicalCompanion()
        # Disabling latency to ensure CI/CD testing pipelines run instantly
        self.psych.simulated_latency = 0 

    def test_positive_reinforcement_routing(self):
        # Testing detection of purely positive clinical sentiment despite varied capitalization.
        texts = [
            "I AM FEELING GREAT TODAY!",
            "It is getting easier.",
            "motivated"
        ]
        for text in texts:
            sentiment, reply = self.psych.analyze_sentiment_and_respond(text)
            self.assertEqual(sentiment, "Motivated", f"Failed on input: {text}")

    def test_clinical_burnout_detection(self):
        # Testing detection of physical or emotional burnout for safety flagging.
        texts = [
            "My arm hurts, this is too hard.",
            "I am exhausted and frustrated.",
            "pain"
        ]
        for text in texts:
            sentiment, reply = self.psych.analyze_sentiment_and_respond(text)
            self.assertEqual(sentiment, "Needs Support", f"Failed on input: {text}")

    def test_mixed_emotional_state_resolution(self):
        # Advanced FSM NLP: Testing resolution when patient exhibits conflicting sentiments.
        # This contains both 'hard' (negative) and 'improving' (positive)
        complex_text = "It is really hard and hurts sometimes, but I know I am improving."
        sentiment, reply = self.psych.analyze_sentiment_and_respond(complex_text)
        
        self.assertEqual(sentiment, "Mixed")
        self.assertIn("hard", reply.lower())
        self.assertIn("improving", reply.lower())

    def test_noise_and_null_inputs(self):
        # Testing algorithm robustness against conversational noise and empty data.
        # Completely neutral/unrecognized words
        sentiment1, _ = self.psych.analyze_sentiment_and_respond("I ate an apple today.")
        self.assertEqual(sentiment1, "Neutral")
        
        # Extreme punctuation and whitespace stripping
        sentiment2, _ = self.psych.analyze_sentiment_and_respond("   ...   ")
        self.assertEqual(sentiment2, "Neutral")

if __name__ == '__main__':
    unittest.main()
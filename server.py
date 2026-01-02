from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import time
import logging

# --- Configuration & Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    USE_REAL_AI = True
    API_KEY = "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"
    PORT = 5000
    DEBUG = True

# --- Chatbot Engine ---
class MentalHealthChatbot:
    """
    A professional chatbot engine designed to provide empathetic responses 
    based on keyword mapping and heuristic mirroring.
    """
    
    PATTERNS = {
        "greeting": {
            "keywords": ["hello", "hi", "hey", "start"],
            "responses": [
                "Hello. I'm here to listen. How are you feeling today?",
                "Hi there. This is a safe space. What's on your mind?",
                "Welcome. I'm ready to support you. Where would you like to start?"
            ]
        },
        "anxiety": {
            "keywords": ["anxious", "worry", "panic", "scared", "nervous", "future", "apprehension", "tension", "unease", "fear", "terrified", "agitation", "restlessness", "fidgety", "nervousness", "stress", "pressure", "overwhelm", "apprehensive", "anxiety"],
            "responses": [
                "It sounds like you're carrying a lot of anxiety. Can you tell me what specifically is triggering these feelings?",
                "I hear your worry. Let's focus on the present moment. Have you tried the 4-7-8 breathing exercise?",
                "Anxiety can feel overwhelming, but it doesn't define you. What is one small thing you can control right now?"
            ]
        },
        "depression": {
            "keywords": ["sad", "depressed", "hopeless", "down", "cry", "lonely", "despair", "anguish", "misery", "sorrow", "gloom", "hopelessness", "disappointment", "letdown", "melancholy", "sadness", "sorrow", "melancholy", "pensive", "isolation", "solitude"],
            "responses": [
                "I'm sorry you're going through this darkness. You don't have to face it alone. How long have you been feeling this way?",
                "It takes courage to admit you're struggling. Be gentle with yourself. What does your body need right now?",
                "I hear that you're in pain. Sometimes just naming the feeling can help. Would you say you're feeling more 'empty' or 'heavy'?"
            ]
        },
        "crisis": {
            "keywords": ["suicide", "kill myself", "die", "end it", "hurt myself"],
            "responses": [
                "I'm very concerned about what you're saying. If you are in danger, please call emergency services (112 or 988) immediately. I am an AI and cannot physically help, but your life matters.",
                "Please reach out to a crisis hotline or a trusted person right now. You deserve support in this difficult moment."
            ]
        },
        "anger": {
            "keywords": ["rage", "fury", "wrath", "angry", "annoyed", "irritated", "aggravation", "bitterness", "resentment", "grudge", "frustration", "annoyance", "irritation", "aggravation"],
            "responses": [
                "I can hear the intensity in your words. It's okay to feel angry. What triggered this for you?",
                "Anger is often a protective emotion. What do you feel you need to protect right now?",
                "It sounds like you're feeling very frustrated. How can we channel this energy safely?"
            ]
        },
        "joy": {
            "keywords": ["happy", "joy", "delight", "pleasure", "elation", "exhilaration", "thrilled", "excited", "great", "better", "thanks", "happiness", "joy", "delight", "pleasure", "excitement", "enthusiasm", "elation"],
            "responses": [
                "I'm so glad to hear that! What do you think contributed to this positive feeling?",
                "That's wonderful! Savoring these moments is so important for our well-being.",
                "You're doing great. I'm happy to be part of your journey today."
            ]
        },
        "confusion": {
            "keywords": ["confusion", "uncertainty", "puzzled", "unsure", "indecision", "bewilderment", "perplexity", "puzzled", "uncertainty"],
            "responses": [
                "Feeling confused is a natural part of processing. Can you describe what feels unclear?",
                "Uncertainty can be heavy. What would one step toward clarity look like for you?",
                "It's okay not to have all the answers right now. Let's explore this together."
            ]
        },
        "admiration": {
            "keywords": ["admiration", "respectful", "appreciative", "awe", "wonder", "astonishment", "respectful", "appreciative", "astonishment"],
            "responses": [
                "Admiration is such a powerful, positive emotion. What or who has inspired you today?",
                "Feeling a sense of wonder can be very grounding. Can you tell me more about what amazed you?",
                "It's beautiful to feel that level of respect. How does it change your perspective?"
            ]
        },
        "boredom": {
            "keywords": ["boredom", "tedium", "monotony", "apathy", "indifference", "detachment", "tedium", "monotony", "indifference", "detachment"],
            "responses": [
                "Boredom is often a signal that we're looking for more engagement or meaning. What usually sparks your interest?",
                "When things feel monotonous, even a small change in routine can help. What's one thing you could do differently today?",
                "I hear that you're feeling a bit detached. Is there anything that still feels worth your attention?"
            ]
        },
        "calm": {
            "keywords": ["calm", "peaceful", "relaxed", "serenity", "tranquility", "relief", "comfort", "peace", "serenity", "tranquility", "alleviation"],
            "responses": [
                "That sounds like a very centered place to be. What helped you reach this state of calm?",
                "Peace is a precious thing. How does your body feel in this moment of relaxation?",
                "I'm glad you're feeling some relief. It's important to acknowledge these quiet moments."
            ]
        },
        "shame": {
            "keywords": ["shame", "humiliation", "embarrassment", "mortified", "self-conscious", "insecure", "awkward", "guilt", "remorse", "regret", "mortified", "humiliation", "embarrassment", "shame", "awkwardness", "remorse", "repentance", "contrition", "regretfulness"],
            "responses": [
                "Those feelings can be very heavy and isolating. Remember that everyone makes mistakes and feels awkward sometimes.",
                "It takes a lot of strength to talk about feeling ashamed. What would you say to a friend who felt this way?",
                "Guilt often points to our values. If you could rewind, what would you do differently, and how can you forgive yourself now?"
            ]
        },
        "curiosity": {
            "keywords": ["curiosity", "inquisitive", "interested", "fascination", "captivation", "intrigue", "engagement", "interest", "inquisitive"],
            "responses": [
                "Your curiosity is a great asset! What specifically is drawing your attention right now?",
                "It's wonderful to feel engaged with the world around you. What are you hoping to discover?",
                "Interest and intrigue are the first steps to learning. Tell me more about what's on your mind."
            ]
        },
        "longing": {
            "keywords": ["desire", "longing", "yearning", "lust", "passion", "zeal", "fervor", "lust", "passion", "zeal", "fervor"],
            "responses": [
                "Yearning for something can be both beautiful and painful. What is the core of this desire?",
                "Passion is a powerful motivator. How are you choosing to express this intensity?",
                "Longing often points to a deep need. What do you think you're truly searching for?"
            ]
        },
        "hurt": {
            "keywords": ["hurt", "pain", "offended", "betrayed", "abandoned", "alienation", "estrangement", "disconnection", "hurt", "pain", "offended", "alienation", "estrangement", "disconnection"],
            "responses": [
                "I hear that you're in pain, and I'm here with you. Can you tell me more about what happened?",
                "Feeling disconnected or betrayed is incredibly difficult. It's okay to feel hurt.",
                "Your feelings are valid. How can you show yourself some extra kindness while you're hurting?"
            ]
        },
        "empathy": {
            "keywords": ["empathy", "compassion", "understanding", "sympathy", "pity", "kindness", "compassion", "understanding", "sympathy", "pity", "compassion", "concern"],
            "responses": [
                "Your capacity for empathy is a beautiful gift. Who are you feeling this compassion for?",
                "It sounds like you're connecting deeply with someone else's experience. How does it affect your own mood?",
                "Being kind to others is wonderful, but remember to save some of that compassion for yourself too."
            ]
        },
        "pride": {
            "keywords": ["pride", "self-respect", "accomplishment", "empowered", "confident", "self-respect", "accomplishment"],
            "responses": [
                "You should be proud of what you've achieved! What was the hardest part of the journey?",
                "Confidence looks good on you. How does it feel to stand in your own strength?",
                "Self-respect is the foundation of mental health. I'm glad you're acknowledging your worth."
            ]
        },
        "love": {
            "keywords": ["love", "affection", "attachment", "fondness", "care", "adoration", "devotion", "fondness", "affection", "care"],
            "responses": [
                "Love and affection are what make life rich. Who or what are you feeling this for right now?",
                "It's beautiful to have that sense of attachment and care. How do you usually express these feelings?",
                "Fondness is a warm place to be. What do you appreciate most about this connection?"
            ]
        },
        "vulnerability": {
            "keywords": ["vulnerability", "exposure", "openness", "fragile", "exposure", "openness"],
            "responses": [
                "Being vulnerable is not a weakness; it's a profound form of courage. How does it feel to be this open?",
                "I hear that you're feeling a bit exposed. This is a safe space to explore those feelings.",
                "Openness allows for true connection. What are you hoping will come from this vulnerability?"
            ]
        },
        "nostalgia": {
            "keywords": ["nostalgia", "sentimentality", "reminiscence", "memory", "sentimentality", "reminiscence"],
            "responses": [
                "Nostalgia can be a bitter-sweet experience. What specific memory are you holding onto?",
                "Reflecting on the past can give us insights into our present. What makes that time feel so significant?",
                "It's okay to miss things. What parts of that 'then' would you like to bring into your 'now'?"
            ]
        },
        "amusement": {
            "keywords": ["amusement", "funny", "entertained", "humor", "fun", "laughter", "funny", "entertained"],
            "responses": [
                "I'm glad you found something funny! Laughter is great medicine. What tickled your fancy?",
                "It's good to keep a sense of humor. What's the story behind the fun?",
                "Amusement can really brighten a day. Tell me more about what's making you smile."
            ]
        },
        "disgust": {
            "keywords": ["disgust", "repulsion", "aversion", "disdain", "contempt", "scorn", "repulsion", "aversion"],
            "responses": [
                "Feeling a strong sense of aversion or disgust is often our mind's way of setting a boundary. What feels 'off' to you?",
                "It sounds like you're dealing with something quite repulsive. How are you managing that feeling?",
                "Disgust can be a very visceral emotion. What do you feel needs to be distanced from right now?"
            ]
        },
        "skepticism": {
            "keywords": ["skepticism", "doubt", "disbelief", "incredulity", "unsure", "doubt", "disbelief"],
            "responses": [
                "It's healthy to have a critical mind. What's making you feel skeletal or doubtful?",
                "Disbelief often happens when something doesn't align with our expectations. What feels 'not quite right'?",
                "Doubt is the first step toward deeper understanding. What questions are you weighing right now?"
            ]
        },
        "satisfaction": {
            "keywords": ["satisfaction", "contentment", "gratified", "fulfillment", "ease", "satisfaction", "contentment", "gratified", "fulfillment", "ease"],
            "responses": [
                "That sounds like a very fulfilling place to be. What brought you this sense of satisfaction?",
                "Contentment is a quiet kind of joy. How does it feel to simply 'be' right now?",
                "I'm glad you're feeling gratified. It's important to recognize when things are going well."
            ]
        },
        "trust": {
            "keywords": ["trust", "confidence", "faith"],
            "responses": [
                "Trust is the cornerstone of any strong relationship, including the one with yourself. Who or what are you leaning on right now?",
                "Having faith and confidence can move mountains. How has this trust shaped your recent decisions?",
                "It's powerful to trust in something. What makes this particular bond or belief feel so solid?"
            ]
        },
        "hope": {
            "keywords": ["hope", "optimism", "anticipation", "hopefulness", "positivity"],
            "responses": [
                "Hope is like a light in the distance. What are you most optimistic about right now?",
                "It's wonderful to feel that sense of anticipation and positivity. What's the best possible outcome you're imagining?",
                "Guiding yourself with hope is so important. What keeps your optimism alive?"
            ]
        },
        "inspiration": {
            "keywords": ["inspiration", "motivated", "stimulated", "eager"],
            "responses": [
                "That spark of inspiration is so valuable! What motivated or stimulated you recently?",
                "Eagerness and inspiration are great engines for change. What are you excited to start working on?",
                "It's amazing when we feel that drive. How can you capitalize on this motivated state?"
            ]
        },
        "surprise": {
            "keywords": ["surprise", "unexpected", "astonishment", "shock"],
            "responses": [
                "Surprises can catch us off guard, for better or worse. What was the unexpected event?",
                "Astonishment and shock can take a moment to process. How are you feeling now that the initial surprise has passed?",
                "The unexpected keeps life interesting, though it can be stressful too. How has this surprise changed your day?"
            ]
        },
        "impatience": {
            "keywords": ["impatience", "restlessness", "anxious_waiting"],
            "responses": [
                "Waiting can be one of the hardest things to do. What are you most eager to move past?",
                "Impatience often signals that we're ready for our next chapter. How can you find a bit of ease while you wait?",
                "I hear your restlessness. What do you feel is being held back right now?"
            ]
        }
    }

    FALLBACK_RESPONSES = [
        "I'm listening. Tell me more about that.",
        "How does that make you feel?",
        "I see. Go on.",
        "Can you help me understand what you mean by that?",
        "That sounds important. Why do you think that is?"
    ]

    @classmethod
    def get_response(cls, user_text: str) -> str:
        """Processes user input and returns an empathetic response."""
        text_lower = user_text.lower()

        # 1. Keyword Matching
        for category, data in cls.PATTERNS.items():
            if any(keyword in text_lower for keyword in data["keywords"]):
                return random.choice(data["responses"])

        # 2. Heuristic Mirroring (e.g., "I feel X")
        if len(user_text) > 10 and " feel " in text_lower:
            try:
                parts = text_lower.split(" feel ")
                feeling = parts[1].split()[0].strip('.,?!')
                return f"It sounds like those feelings of {feeling} are quite strong. Can you share more about why you're feeling that way?"
            except Exception:
                pass

        # 3. Fallback
        return random.choice(cls.FALLBACK_RESPONSES)

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handles incoming chat messages and provides AI or scripted responses."""
    try:
        data = request.json
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({"reply": "I'm here. You can say anything."}), 200

        # Simulate thinking time for a more human-like experience
        time.sleep(0.5)

        if Config.USE_REAL_AI and Config.API_KEY and not Config.API_KEY.startswith("hf_"):
            # Placeholder for future integration with actual LLM APIs
            # For now, we use the sophisticated scripted engine for stability
            response_text = MentalHealthChatbot.get_response(user_message)
        else:
            response_text = MentalHealthChatbot.get_response(user_message)

        return jsonify({"reply": response_text}), 200

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"reply": "I'm sorry, I'm having a bit of trouble processing that. Can you try again?"}), 500

if __name__ == '__main__':
    logger.info(f"MindMate Therapist Server starting on http://localhost:{Config.PORT}")
    app.run(debug=Config.DEBUG, port=Config.PORT)

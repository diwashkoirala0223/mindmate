from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import time

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for frontend

# --- Configuration ---
# To use a real AI (like Gemini, OpenAI), you would add your API Key here.
USE_REAL_AI = True
API_KEY = "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"

# --- Therapist Persona & Knowledge Base (Offline Mode) ---
# This simulates a therapist's responses when offline.
therapist_patterns = {
    "greeting": {
        "keywords": ["hello", "hi", "hey", "start"],
        "responses": [
            "Hello. I'm here to listen. How are you feeling today?",
            "Hi there. This is a safe space. What's on your mind?",
            "Welcome. I'm ready to support you. Where would you like to start?"
        ]
    },
    "anxiety": {
        "keywords": ["anxious", "worry", "panic", "scared", "nervous", "future"],
        "responses": [
            "It sounds like you're carrying a lot of anxiety. Can you tell me what specifically is triggering these feelings?",
            "I hear your worry. Let's focus on the present moment. Have you tried the 4-7-8 breathing exercise in the 'Breathing' tab?",
            "Anxiety can feel overwhelming, but it doesn't define you. What is one small thing you can control right now?"
        ]
    },
    "depression": {
        "keywords": ["sad", "depressed", "hopeless", "down", "cry", "lonely"],
        "responses": [
            "I'm sorry you're going through this darkness. You don't have to face it alone. How long have you been feeling this way?",
            "It takes courage to admit you're struggling. Be gentle with yourself. What does your body need right now—rest, water, or maybe just a deep breath?",
            "I hear that you're in pain. Sometimes just naming the feeling can help. Would you say you're feeling more 'anxious' or 'annoyed'?"
        ]
    },
    "crisis": {
        "keywords": ["suicide", "kill myself", "die", "end it", "hurt myself"],
        "responses": [
            "I'm very concerned about what you're saying. If you are in danger, please call emergency services (112 or 988) immediately. I am an AI and cannot physically help, but your life matters.",
            "Please reach out to a crisis hotline or a trusted person right now. You deserve support in this difficult moment."
        ]
    },
    "sleep": {
        "keywords": ["sleep", "insomnia", "tired", "awake"],
        "responses": [
            "Sleep struggles are often linked to a busy mind. Have you tried a 'body scan' meditation before bed?",
            "It's frustrating when rest won't come. Try to lower the lights and avoid screens. Would you like a sleep hygiene tip?"
        ]
    },
    "gratitude": {
        "keywords": ["happy", "good", "great", "better", "thanks"],
        "responses": [
            "I'm so glad to hear that! What do you think contributed to this positive feeling?",
            "That's wonderful. Holding onto these moments is key. Have you written this down in your journal yet?",
            "You're welcome. I'm proud of the steps you're taking."
        ]
    },
    "admiration": {
    "keywords": ["admiration", "respectful", "appreciative"],
    "responses": [
        "I see you admire something or someone. Can you share what it is?",
        "Admiration is a powerful feeling. What inspires you the most right now?",
        "Feeling appreciation can uplift you. Who or what are you thinking about?",
        "It's wonderful to feel respect and admiration. How does it make you feel internally?",
        "Let's explore this feeling of admiration together. What stands out to you?"
    ]
},
"adoration": {
    "keywords": ["adoration", "devotion", "fondness"],
    "responses": [
        "Feeling adoration is beautiful. Who or what do you feel this for?",
        "Devotion can be comforting. Can you describe why this matters to you?",
        "Fondness is warm. How does it influence your mood today?",
        "Adoration often brings joy. Can you reflect on this feeling?",
        "Let's dive into this sense of adoration. What stands out most?"
    ]
},
"agitation": {
    "keywords": ["agitation", "restlessness", "fidgety"],
    "responses": [
        "I notice you're feeling agitated. Can you describe what's causing it?",
        "Restlessness can be stressful. What could help you calm down?",
        "Feeling fidgety is normal sometimes. Have you tried grounding techniques?",
        "Agitation is a signal from your body. What does it want you to address?",
        "Let's explore this agitation. Can you identify the trigger?"
    ]
},
"amusement": {
    "keywords": ["amusement", "funny", "entertained"],
    "responses": [
        "I see something is amusing you. Can you share what made you laugh?",
        "Entertainment can be uplifting. What brought you joy today?",
        "Funny moments brighten our day. How did this make you feel?",
        "Amusement is a delightful feeling. Would you like to describe it?",
        "Let's explore why this amused you. What stands out?"
    ]
},
"awe": {
    "keywords": ["awe", "wonder", "astonishment"],
    "responses": [
        "Feeling awe is magical. What has amazed you recently?",
        "Wonder can open the mind. Can you describe what caused it?",
        "Astonishment can be thrilling. How did it impact you?",
        "Let's reflect on this sense of awe. What emotions arise?",
        "It's wonderful to feel amazed. What do you notice most?"
    ]
},
"boredom": {
    "keywords": ["boredom", "tedium", "monotony"],
    "responses": [
        "Feeling bored is normal. What’s been uninteresting for you?",
        "Tedium can be draining. How can you make this moment engaging?",
        "Monotony can feel heavy. Any small change that could uplift you?",
        "Let's explore your boredom. What would excite you?",
        "Boredom signals a need for stimulation. What sparks your interest?"
    ]
},
"calm": {
    "keywords": ["calm", "peaceful", "relaxed"],
    "responses": [
        "Feeling calm is wonderful. What helps you achieve this?",
        "Peace can be grounding. Can you describe this serene moment?",
        "Relaxation is a gift. How does your body feel in this calm state?",
        "Let's savor this calm. What contributed to it?",
        "Being peaceful is valuable. Can you reflect on what brought it?"
    ]
},
"confusion": {
    "keywords": ["confusion", "uncertainty", "puzzled"],
    "responses": [
        "Feeling confused is normal. Can you describe what’s unclear?",
        "Uncertainty can be stressful. What would help clarify things?",
        "Being puzzled is part of processing. Can you break it down?",
        "Let's explore your confusion. What do you notice first?",
        "It's okay to feel uncertain. How can you move forward?"
    ]
},
"contentment": {
    "keywords": ["contentment", "satisfaction", "gratified"],
    "responses": [
        "Feeling content is a wonderful state. What makes you feel this way?",
        "Satisfaction can uplift the soul. Can you describe the moment?",
        "Gratification often comes from small joys. What stands out?",
        "Let's reflect on your contentment. What brought it today?",
        "Contentment is precious. How does it affect your mood?"
    ]
},
"curiosity": {
    "keywords": ["curiosity", "inquisitive", "interested"],
    "responses": [
        "Curiosity is a spark for learning. What are you curious about?",
        "Being inquisitive can lead to growth. What questions do you have?",
        "Interest can guide exploration. What draws your attention?",
        "Let's explore your curiosity. What excites your mind?",
        "Curiosity is valuable. How can you satisfy it today?"
    ]
},
"desire": {
    "keywords": ["desire", "longing", "yearning"],
    "responses": [
        "Feeling desire is natural. What do you want most right now?",
        "Longing can be intense. Can you describe it more clearly?",
        "Yearning often signals a goal. What are you aiming for?",
        "Let's explore this desire. How does it influence your feelings?",
        "Desire can motivate. What steps could help you pursue it?"
    ]
},
"despair": {
    "keywords": ["despair", "hopelessness", "anguish"],
    "responses": [
        "Feeling despair is heavy. Can you share what’s causing it?",
        "Hopelessness can be overwhelming. What small step can you take?",
        "Anguish is hard. How are you coping right now?",
        "Let's explore this despair. What would bring some relief?",
        "It's okay to feel heavy emotions. Can we talk about them?"
    ]
},
"disappointment": {
    "keywords": ["disappointment", "letdown", "frustration"],
    "responses": [
        "I see you feel disappointed. What happened?",
        "A letdown can hurt. How did it affect you?",
        "Frustration is natural when expectations aren’t met. Can you share more?",
        "Let's reflect on this disappointment. How can you cope?",
        "Disappointment is valid. What can you do next?"
    ]
},
"disgust": {
    "keywords": ["disgust", "repulsion", "aversion"],
    "responses": [
        "Feeling disgust is natural. Can you explain what triggered it?",
        "Repulsion often signals boundaries. How do you feel physically?",
        "Aversion can guide your choices. What is it teaching you?",
        "Let's explore this feeling of disgust. What stands out?",
        "Disgust is valid. How might you respond to it constructively?"
    ]
},
"embarrassment": {
    "keywords": ["embarrassment", "shame", "awkward"],
    "responses": [
        "Feeling embarrassed is normal. Can you describe the situation?",
        "Awkward moments happen to everyone. How does this affect you?",
        "Shame can feel heavy. What would help you feel lighter?",
        "Let's explore your embarrassment. What did you learn?",
        "It's okay to feel awkward. Can you reflect on it positively?"
    ]
},
"empathy": {
    "keywords": ["empathy", "compassion", "understanding"],
    "responses": [
        "I notice your empathy. Who are you feeling it for?",
        "Compassion is powerful. Can you describe what moves you?",
        "Understanding others is valuable. How does it affect your emotions?",
        "Let's reflect on your empathy. What insights arise?",
        "Being compassionate is important. How do you practice it?"
    ]
},
"envy": {
    "keywords": ["envy", "jealousy", "covetous"],
    "responses": [
        "I see you feel envy. What is causing this feeling?",
        "Jealousy can be revealing. What does it show about your desires?",
        "Covetous feelings are normal. Can you explore why you feel this way?",
        "Let's examine this envy. How does it impact your actions?",
        "It's okay to feel jealous. How can you process it positively?"
    ]
},
"excitement": {
    "keywords": ["excitement", "thrilled", "eager"],
    "responses": [
        "Feeling excited is wonderful. What’s causing this joy?",
        "Thrill can be energizing. Can you describe it more?",
        "Eagerness often motivates action. What are you looking forward to?",
        "Let's explore this excitement. How does it affect your energy?",
        "It's great to feel thrilled. What stands out most?"
    ]
},
"fear": {
    "keywords": ["fear", "afraid", "terrified", "apprehensive"],
    "responses": [
        "Feeling fear is natural. Can you explain what frightens you?",
        "Being afraid is okay. How does it affect your thoughts?",
        "Terrified feelings can be intense. What would help you feel safe?",
        "Let's explore this fear. What triggers it?",
        "Fear is valid. How can you manage it right now?"
    ]
},
"frustration": {
    "keywords": ["frustration", "annoyance", "irritation"],
    "responses": [
        "I see you’re frustrated. What’s causing this?",
        "Annoyance is natural. How does it feel in your body?",
        "Irritation can signal unmet needs. Can you describe them?",
        "Let's explore your frustration. What can help relieve it?",
        "Feeling frustrated is okay. What’s one small step to improve it?"
    ]
},
"guilt": {
    "keywords": ["guilt", "remorse", "regret"],
    "responses": [
        "Feeling guilty is tough. Can you explain what happened?",
        "Remorse can guide reflection. How do you want to move forward?",
        "Regret is normal. What can you learn from this feeling?",
        "Let's explore this guilt. How does it affect you?",
        "It's okay to feel regret. How could you make amends or forgive yourself?"
    ]
},
"happiness": {
    "keywords": ["happiness", "joy", "delight", "pleasure"],
    "responses": [
        "Feeling happy is wonderful. What brought you this joy?",
        "Delight can energize your day. Can you describe it?",
        "Pleasure often comes from small moments. What stands out?",
        "Let's explore your happiness. How does it feel in your body?",
        "It's great to feel joy. Can you savor this moment?"
    ]
},
"hope": {
    "keywords": ["hope", "optimism", "anticipation"],
    "responses": [
        "I see you feel hopeful. What are you looking forward to?",
        "Optimism can lift your spirit. Can you describe it?",
        "Anticipation can be exciting. What awaits you?",
        "Let's reflect on this hope. How does it influence your mood?",
        "It's wonderful to feel hopeful. How can you nurture it?"
    ]
},
"humiliation": {
    "keywords": ["humiliation", "embarrassment", "mortified"],
    "responses": [
        "Feeling humiliated is painful. Can you describe the situation?",
        "Being embarrassed can weigh heavily. How does it affect you?",
        "Mortification is tough. What helps you cope?",
        "Let's explore this humiliation. What did you learn?",
        "It's okay to feel embarrassed. How might you recover gracefully?"
    ]
},
"hurt": {
    "keywords": ["hurt", "pain", "offended"],
    "responses": [
        "I notice you feel hurt. What caused this pain?",
        "Being offended can sting. Can you describe your feelings?",
        "Emotional pain is real. How does it affect you?",
        "Let's explore this hurt. What would help you feel better?",
        "Feeling hurt is valid. How can you care for yourself now?"
    ]
},
"impatience": {
    "keywords": ["impatience", "restlessness", "anxious_waiting"],
    "responses": [
        "Feeling impatient is normal. What's making you feel this way?",
        "Restlessness can signal something important. Can you describe it?",
        "Anxious waiting is tough. How can you calm yourself?",
        "Let's explore your impatience. What do you want to happen faster?",
        "Impatience is valid. Can you try a small grounding exercise?"
    ]
},
"inspiration": {
    "keywords": ["inspiration", "motivated", "stimulated"],
    "responses": [
        "Feeling inspired is energizing. What sparked this inspiration?",
        "Motivation can move you forward. How do you want to act on it?",
        "Being stimulated can be exciting. Can you describe what triggered it?",
        "Let's reflect on your inspiration. What stands out most?",
        "Inspiration is a gift. How can you nurture it further?"
    ]
},
"interest": {
    "keywords": ["interest", "curiosity", "engagement"],
    "responses": [
        "It's great to feel interested. What caught your attention?",
        "Curiosity is valuable. Can you describe what you want to learn?",
        "Engagement can be rewarding. How does it make you feel?",
        "Let's explore your interest. What draws you in?",
        "Feeling curious and engaged is wonderful. What excites you most?"
    ]
},
"jealousy": {
    "keywords": ["jealousy", "envy", "resentment"],
    "responses": [
        "I see you feel jealous. What's causing this feeling?",
        "Envy can teach us about our desires. Can you explore it?",
        "Resentment is natural. How does it affect you?",
        "Let's reflect on your jealousy. What triggers it?",
        "Feeling jealous is okay. How might you manage it positively?"
    ]
},
"joy": {
    "keywords": ["joy", "delight", "elation"],
    "responses": [
        "Feeling joyful is wonderful. What brought you this joy?",
        "Delight can uplift your day. Can you describe it?",
        "Elation is energizing. How does it feel in your body?",
        "Let's explore your joy. What stands out most?",
        "Joy is precious. Can you savor this moment fully?"
    ]
},
"loneliness": {
    "keywords": ["loneliness", "isolation", "solitude"],
    "responses": [
        "Feeling lonely is hard. Who could you reach out to right now?",
        "Isolation can weigh on you. How does it affect your mood?",
        "Solitude can be peaceful or heavy. How does it feel for you?",
        "Let's explore your loneliness. What would help you feel connected?",
        "It's okay to feel alone. How might you reach out today?"
    ]
},
"love": {
    "keywords": ["love", "affection", "attachment"],
    "responses": [
        "Feeling love is beautiful. Who or what do you feel this for?",
        "Affection can be warm. Can you describe how it shows?",
        "Attachment often brings comfort. How does it affect you?",
        "Let's explore your love. What stands out most?",
        "It's wonderful to feel love. How can you express it safely?"
    ]
},
"lust": {
    "keywords": ["lust", "desire", "passion"],
    "responses": [
        "Feeling lust is natural. Can you describe what attracts you?",
        "Desire can be intense. How does it make you feel internally?",
        "Passion is energizing. How might you channel it responsibly?",
        "Let's explore your lust. What is at the core of this feeling?",
        "It's okay to feel desire. How can you act on it safely?"
    ]
},
"melancholy": {
    "keywords": ["melancholy", "sadness", "pensive"],
    "responses": [
        "Feeling melancholy is normal. What's on your mind?",
        "Sadness can be reflective. How does it affect your body?",
        "Being pensive is part of processing emotions. Can you describe it?",
        "Let's explore your melancholy. What triggered it?",
        "It's okay to feel down. How might you care for yourself now?"
    ]
},
"nervousness": {
    "keywords": ["nervousness", "tension", "apprehension"],
    "responses": [
        "Feeling nervous is natural. What's causing this tension?",
        "Apprehension can teach you about your worries. Can you explore it?",
        "Nervousness often comes before change. How does it affect you?",
        "Let's reflect on your tension. What might help ease it?",
        "It's okay to feel nervous. How can you ground yourself?"
    ]
},
"nostalgia": {
    "keywords": ["nostalgia", "sentimentality", "reminiscence"],
    "responses": [
        "Feeling nostalgic is common. What memory comes to mind?",
        "Sentimentality can bring warmth or longing. Can you describe it?",
        "Reminiscence often makes us reflect. How does it affect your mood?",
        "Let's explore your nostalgia. What stands out?",
        "It's okay to remember the past. How does it feel emotionally?"
    ]
},
"optimism": {
    "keywords": ["optimism", "hopefulness", "positivity"],
    "responses": [
        "Feeling optimistic is uplifting. What are you hopeful about?",
        "Hopefulness can energize you. How does it affect your outlook?",
        "Positivity often influences decisions. What makes you feel positive?",
        "Let's explore your optimism. What stands out?",
        "It's great to feel hopeful. How can you nurture it?"
    ]
},
"overwhelm": {
    "keywords": ["overwhelm", "stress", "pressure"],
    "responses": [
        "Feeling overwhelmed is tough. What’s causing it?",
        "Stress can weigh heavily. How are you coping?",
        "Pressure can feel intense. Can you identify small steps to manage it?",
        "Let's reflect on this overwhelm. What can you do first?",
        "It's okay to feel pressured. How might you ease it?"
    ]
},
"panic": {
    "keywords": ["panic", "terror", "alarm"],
    "responses": [
        "Feeling panic is intense. Can you describe what triggered it?",
        "Terror can overwhelm. Let's focus on grounding techniques.",
        "Alarm signals danger. How can you calm yourself right now?",
        "Let's explore your panic. What helps you regain control?",
        "It's okay to feel scared. What small steps can help you?"
    ]
},
"passion": {
    "keywords": ["passion", "zeal", "enthusiasm"],
    "responses": [
        "Feeling passionate is energizing. What drives this feeling?",
        "Zeal can motivate action. How can you channel it positively?",
        "Enthusiasm brings joy. What excites you the most?",
        "Let's explore your passion. How does it affect your energy?",
        "It's wonderful to feel motivated. How might you express it?"
    ]
},
"peace": {
    "keywords": ["peace", "serenity", "tranquility"],
    "responses": [
        "Feeling peaceful is valuable. What contributes to this serenity?",
        "Serenity can calm the mind. Can you describe this feeling?",
        "Tranquility is grounding. How does it affect your body?",
        "Let's reflect on your peace. What stands out?",
        "It's wonderful to feel calm. How can you maintain it?"
    ]
},
"pity": {
    "keywords": ["pity", "sympathy", "compassion"],
    "responses": [
        "Feeling pity shows empathy. Who are you thinking about?",
        "Sympathy can help connections. How does this affect you?",
        "Compassion is valuable. How might you act on this feeling?",
        "Let's explore your pity. What stands out?",
        "It's okay to feel concern for others. How does it affect you?"
    ]
},
"pride": {
    "keywords": ["pride", "self-respect", "accomplishment"],
    "responses": [
        "Feeling pride is rewarding. What achievement brings this?",
        "Self-respect is important. Can you reflect on it?",
        "Accomplishment feels good. How does it affect your mood?",
        "Let's explore your pride. What stands out most?",
        "It's wonderful to feel proud. How might you celebrate it?"
    ]
},
"rage": {
    "keywords": ["rage", "fury", "wrath"],
    "responses": [
        "Feeling rage is intense. Can you describe what caused it?",
        "Fury can be overwhelming. How does it affect your thoughts?",
        "Wrath often signals boundaries. How might you handle it safely?",
        "Let's explore your anger. What triggers it?",
        "It's okay to feel enraged. How can you express it responsibly?"
    ]
},
"regret": {
    "keywords": ["regret", "remorse", "repentance"],
    "responses": [
        "Feeling regret is normal. Can you explain what happened?",
        "Remorse can guide reflection. How might you move forward?",
        "Repentance shows awareness. What can you learn from this?",
        "Let's explore your regret. How does it affect your mood?",
        "It's okay to feel regret. How might you make amends or forgive yourself?"
    ]
},
"relief": {
    "keywords": ["relief", "comfort", "alleviation"],
    "responses": [
        "Feeling relief is good. What eased your worries?",
        "Comfort can be grounding. How does it feel in your body?",
        "Alleviation of stress is valuable. What contributed to it?",
        "Let's reflect on your relief. How does it affect you?",
        "It's great to feel comforted. How might you maintain this feeling?"
    ]
},
"remorse": {
    "keywords": ["remorse", "contrition", "regretfulness"],
    "responses": [
        "Feeling remorse is heavy. What is the cause?",
        "Contrition can guide reflection. How do you want to move forward?",
        "Regretfulness is natural. Can you explore what you learned?",
        "Let's reflect on your remorse. How does it affect you?",
        "It's okay to feel this. How can you forgive yourself?"
    ]
},
"resentment": {
    "keywords": ["resentment", "grudge", "bitterness"],
    "responses": [
        "Feeling resentment is valid. Who or what is involved?",
        "Holding a grudge can weigh on you. How does it feel?",
        "Bitterness can affect your mood. Can you reflect on it?",
        "Let's explore your resentment. What triggered it?",
        "It's okay to feel this way. How can you release it safely?"
    ]
},
"sadness": {
    "keywords": ["sadness", "sorrow", "melancholy"],
    "responses": [
        "Feeling sad is natural. What’s weighing on you?",
        "Sorrow can be heavy. Can you describe how it feels?",
        "Melancholy often signals reflection. What comes to mind?",
        "Let's explore your sadness. How can you care for yourself?",
        "It's okay to feel down. How might you find comfort?"
    ]
},
"satisfaction": {
    "keywords": ["satisfaction", "contentment", "fulfillment"],
    "responses": [
        "Feeling satisfied is great. What brought this fulfillment?",
        "Contentment can lift your mood. How does it feel in your body?",
        "Fulfillment often comes from small achievements. What stands out?",
        "Let's reflect on your satisfaction. What made this possible?",
        "It's wonderful to feel content. How might you savor this moment?"
    ]
},
"self-conscious": {
    "keywords": ["self-conscious", "insecure", "awkwardness"],
    "responses": [
        "Feeling self-conscious is normal. Can you describe why?",
        "Insecurity can affect thoughts and actions. How does it feel?",
        "Awkwardness happens to everyone. How are you handling it?",
        "Let's explore your self-consciousness. What triggered it?",
        "It's okay to feel insecure. How might you build confidence?"
    ]
},
"shame": {
    "keywords": ["shame", "humiliation", "embarrassment"],
    "responses": [
        "Feeling shame is heavy. Can you explain what happened?",
        "Humiliation can be tough. How does it affect you?",
        "Embarrassment is normal. What helps you cope?",
        "Let's explore your shame. How might you release it?",
        "It's okay to feel this way. How can you forgive yourself?"
    ]
},
"shock": {
    "keywords": ["shock", "astonishment", "surprise"],
    "responses": [
        "Feeling shocked is natural. What happened?",
        "Astonishment can be overwhelming. Can you describe it?",
        "Surprise can catch us off guard. How does it affect you?",
        "Let's reflect on this shock. What stands out?",
        "It's okay to be surprised. How are you processing it?"
    ]
},
"skepticism": {
    "keywords": ["skepticism", "doubt", "disbelief"],
    "responses": [
        "Feeling skeptical is normal. What are you doubting?",
        "Disbelief can be protective. How does it feel internally?",
        "Doubt often prompts reflection. What are you questioning?",
        "Let's explore your skepticism. What stands out?",
        "It's okay to feel unsure. How might you find clarity?"
    ]
},
"surprise": {
    "keywords": ["surprise", "unexpected", "astonishment"],
    "responses": [
        "Feeling surprised can be exciting or shocking. What happened?",
        "Unexpected events catch us off guard. How does it feel?",
        "Astonishment can stir emotions. Can you describe it?",
        "Let's explore your surprise. What stands out?",
        "It's okay to be surprised. How might you process it?"
    ]
},
"sympathy": {
    "keywords": ["sympathy", "compassion", "concern"],
    "responses": [
        "Feeling sympathy shows empathy. Who are you thinking of?",
        "Compassion can help connections. How does this affect you?",
        "Concern for others is natural. Can you act on it positively?",
        "Let's explore your sympathy. What stands out?",
        "It's okay to care for others. How might you support them?"
    ]
},
"trust": {
    "keywords": ["trust", "confidence", "faith"],
    "responses": [
        "Feeling trust is valuable. Who or what do you trust?",
        "Confidence can be empowering. How does it affect you?",
        "Faith in someone or something can uplift. Can you describe it?",
        "Let's explore your trust. What makes it strong?",
        "It's wonderful to feel trust. How can you nurture it?"
    ]
},
"uncertainty": {
    "keywords": ["uncertainty", "indecision", "unsure"],
    "responses": [
        "Feeling uncertain is normal. What's causing it?",
        "Indecision can be stressful. How does it feel?",
        "Being unsure often signals reflection. What are you weighing?",
        "Let's explore your uncertainty. What could help you decide?",
        "It's okay to feel unsure. How might you gain clarity?"
    ]
},
"unease": {
    "keywords": ["unease", "discomfort", "restlessness"],
    "responses": [
        "Feeling uneasy is natural. Can you explain why?",
        "Discomfort signals something important. How does it feel?",
        "Restlessness can affect your body. What might help you relax?",
        "Let's explore your unease. What stands out?",
        "It's okay to feel uncomfortable. How can you soothe yourself?"
    ]
},
"vulnerability": {
    "keywords": ["vulnerability", "exposure", "openness"],
    "responses": [
        "Feeling vulnerable can be powerful. What makes you feel exposed?",
        "Openness requires courage. How does it affect you?",
        "Exposure can be scary. How might you protect yourself?",
        "Let's explore your vulnerability. What insights arise?",
        "It's okay to be vulnerable. How can you handle it safely?"
    ]
},
"worry": {
    "keywords": ["worry", "concern", "anxiety"],
    "responses": [
        "Feeling worried is normal. What are you concerned about?",
        "Concern often signals important priorities. Can you describe it?",
        "Anxiety can weigh heavily. How does it affect you?",
        "Let's explore your worry. What might ease it?",
        "It's okay to feel concerned. How can you calm yourself?"
    ]
},
"zeal": {
    "keywords": ["zeal", "passion", "fervor"],
    "responses": [
        "Feeling zealous is energizing. What drives this fervor?",
        "Passion can motivate action. How might you channel it positively?",
        "Fervor can inspire. What excites you the most?",
        "Let's explore your zeal. How does it affect your energy?",
        "It's wonderful to feel motivated. How might you express it?"
    ]
},
"affection": {
    "keywords": ["affection", "fondness", "care"],
    "responses": [
        "Feeling affection is warm. Who or what do you care for?",
        "Fondness can uplift. How does it make you feel?",
        "Care for others is important. How might you express it?",
        "Let's explore your affection. What stands out most?",
        "It's wonderful to feel close to someone. How can you nurture it?"
    ]
},
"aggravation": {
    "keywords": ["aggravation", "annoyance", "irritation"],
    "responses": [
        "Feeling aggravated is normal. What caused this irritation?",
        "Annoyance can affect your mood. How are you handling it?",
        "Irritation signals unmet needs. Can you describe them?",
        "Let's explore your aggravation. What triggers it?",
        "It's okay to feel frustrated. How might you release it?"
    ]
},
"alienation": {
    "keywords": ["alienation", "estrangement", "disconnection"],
    "responses": [
        "Feeling alienated can be hard. Can you describe why?",
        "Estrangement often affects our mood. How does it feel?",
        "Disconnection can signal unmet needs. What could help you?",
        "Let's explore your alienation. What stands out?",
        "It's okay to feel separate. How might you reconnect?"
    ]
},
"apathy": {
    "keywords": ["apathy", "indifference", "detachment"],
    "responses": [
        "Feeling apathetic is normal sometimes. What contributes to it?",
        "Indifference can signal burnout. How does it affect you?",
        "Detachment can protect you emotionally. Can you describe it?",
        "Let's explore your apathy. What would spark interest?",
        "It's okay to feel disconnected. How might you re-engage?"
    ]
},
"apprehension": {
    "keywords": ["apprehension", "anxiety", "nervousness"],
    "responses": [
        "Feeling apprehensive is normal. What worries you?",
        "Anxiety can be overwhelming. How does it feel in your body?",
        "Nervousness often signals anticipation. What are you expecting?",
        "Let's explore your apprehension. What helps ease it?",
        "It's okay to feel anxious. How can you calm yourself?"
    ]
},
"bewilderment": {
    "keywords": ["bewilderment", "confusion", "perplexity"],
    "responses": [
        "Feeling bewildered is normal. What is confusing you?",
        "Confusion often prompts reflection. Can you describe it?",
        "Perplexity can signal processing. How does it affect you?",
        "Let's explore your bewilderment. What stands out?",
        "It's okay to feel puzzled. How might you gain clarity?"
    ]
},
"bitterness": {
    "keywords": ["bitterness", "resentment", "grudge"],
    "responses": [
        "Feeling bitter is natural. What caused this resentment?",
        "Resentment can weigh on you. How does it feel internally?",
        "Holding a grudge can affect your mood. What might help?",
        "Let's explore your bitterness. What triggered it?",
        "It's okay to feel upset. How might you release it safely?"
    ]
},
"calmness": {
    "keywords": ["calmness", "tranquility", "serenity"],
    "responses": [
        "Feeling calm is valuable. What contributes to this tranquility?",
        "Serenity can be grounding. How does it feel internally?",
        "Peaceful moments are precious. What stands out to you?",
        "Let's reflect on your calmness. How can you maintain it?",
        "It's wonderful to feel serene. How might you sustain it?"
    ]
},
"compassion": {
    "keywords": ["compassion", "kindness", "care"],
    "responses": [
        "Feeling compassion is beautiful. Who are you thinking of?",
        "Kindness can uplift both you and others. How does it feel?",
        "Caring for someone shows empathy. Can you describe it?",
        "Let's explore your compassion. What stands out?",
        "It's wonderful to feel caring. How might you act on it?"
    ]
},
"conflict": {
    "keywords": ["conflict", "disagreement", "argument"],
    "responses": [
        "Feeling conflict is natural. What caused this disagreement?",
        "Arguments can be stressful. How does it affect you?",
        "Disagreement can teach us boundaries. Can you explore it?",
        "Let's reflect on this conflict. What triggered it?",
        "It's okay to experience conflict. How might you resolve it?"
    ]
},
"contentment2": {
    "keywords": ["contentment2", "ease", "satisfaction2"],
    "responses": [
        "Feeling content is wonderful. What brings you ease?",
        "Satisfaction can be grounding. Can you describe it?",
        "Ease of mind is valuable. How does it feel internally?",
        "Let's explore your contentment. What stands out most?",
        "It's great to feel satisfied. How might you savor it?"
    ]
},
"curiosity2": {
    "keywords": ["curiosity2", "interest2", "inquiring"],
    "responses": [
        "Curiosity is a spark. What are you exploring?",
        "Interest leads to discovery. Can you describe it?",
        "Being inquiring opens your mind. How does it feel?",
        "Let's reflect on your curiosity. What draws your attention?",
        "It's great to feel interested. How might you act on it?"
    ]
},
"defiance": {
    "keywords": ["defiance", "rebellion", "resistance"],
    "responses": [
        "Feeling defiant is natural. What are you resisting?",
        "Rebellion can express boundaries. How does it affect you?",
        "Resistance can be empowering. Can you describe it?",
        "Let's explore your defiance. What triggered it?",
        "It's okay to feel rebellious. How might you act safely?"
    ]
},
"delight": {
    "keywords": ["delight", "pleasure2", "joy2"],
    "responses": [
        "Feeling delight is wonderful. What brings you pleasure?",
        "Joy can uplift your spirit. Can you describe it?",
        "Pleasure is valuable. How does it feel internally?",
        "Let's explore your delight. What stands out most?",
        "It's great to feel joyful. How might you savor it?"
    ]
},
"desperation": {
    "keywords": ["desperation", "hopelessness2", "urgency"],
    "responses": [
        "Feeling desperate is heavy. What’s causing it?",
        "Hopelessness can be overwhelming. Can you describe it?",
        "Urgency often signals need. How does it affect you?",
        "Let's explore your desperation. What would bring relief?",
        "It's okay to feel this way. How might you cope?"
    ]
},
"disbelief": {
    "keywords": ["disbelief2", "shock2", "incredulity"],
    "responses": [
        "Feeling disbelief is normal. What surprised you?",
        "Shock can be intense. How does it affect you?",
        "Incredulity shows something unexpected. Can you describe it?",
        "Let's explore your disbelief. What stands out?",
        "It's okay to feel amazed. How might you process it?"
    ]
},
"disdain": {
    "keywords": ["disdain", "contempt", "scorn"],
    "responses": [
        "Feeling disdain is natural. What triggered it?",
        "Contempt can show boundaries. How does it feel?",
        "Scorn often signals disagreement. Can you describe it?",
        "Let's explore your disdain. What stands out?",
        "It's okay to feel this way. How might you respond constructively?"
    ]
},
"eagerness": {
    "keywords": ["eagerness", "enthusiasm2", "readiness"],
    "responses": [
        "Feeling eager is energizing. What excites you?",
        "Enthusiasm can motivate action. Can you describe it?",
        "Readiness prepares you for action. How does it feel?",
        "Let's reflect on your eagerness. What stands out?",
        "It's great to feel motivated. How might you act on it?"
    ]
},
"elation": {
    "keywords": ["elation2", "exhilaration", "thrill2"],
    "responses": [
        "Feeling elated is amazing. What brought this excitement?",
        "Exhilaration lifts your mood. Can you describe it?",
        "Thrill can energize you. How does it affect your body?",
        "Let's explore your elation. What stands out?",
        "It's wonderful to feel exhilarated. How might you savor it?"
    ]
},
"embolden": {
    "keywords": ["embolden", "courage", "bravery"],
    "responses": [
        "Feeling emboldened is powerful. What gives you courage?",
        "Bravery often inspires action. How does it feel internally?",
        "Courage can push you forward. Can you describe it?",
        "Let's explore your bravery. What stands out?",
        "It's great to feel empowered. How might you act on it?"
    ]
},
"envy2": {
    "keywords": ["envy2", "covet", "desire2"],
    "responses": [
        "Feeling envy is normal. What triggers it?",
        "Covetous feelings often reflect desires. How does it feel?",
        "Desire can be motivating. Can you explore it?",
        "Let's reflect on your envy. What stands out?",
        "It's okay to feel this way. How might you redirect it?"
    ]
},
"exasperation": {
    "keywords": ["exasperation", "frustration2", "irritability2"],
    "responses": [
        "Feeling exasperated is natural. What caused it?",
        "Frustration can be heavy. How does it affect you?",
        "Irritability signals stress. Can you describe it?",
        "Let's explore your exasperation. What stands out?",
        "It's okay to feel annoyed. How might you release it?"
    ]
},
"exhilaration": {
    "keywords": ["exhilaration2", "elation2", "thrill3"],
    "responses": [
        "Feeling exhilarated is amazing. What brought this energy?",
        "Elation lifts the spirit. Can you describe it?",
        "Thrill can excite the body. How does it feel?",
        "Let's explore your exhilaration. What stands out?",
        "It's wonderful to feel energized. How might you savor it?"
    ]
},
"fascination": {
    "keywords": ["fascination", "captivation", "intrigue"],
    "responses": [
        "Feeling fascinated is great. What has captured your attention?",
        "Being captivated sparks curiosity. How does it feel?",
        "Intrigue often stimulates thought. Can you describe it?",
        "Let's explore your fascination. What stands out?",
        "It's wonderful to feel interested. How might you act on it?"
    ]
},
"fright": {
    "keywords": ["fright", "alarm2", "panic2"],
    "responses": [
        "Feeling frightened is normal. What caused it?",
        "Alarm can be intense. How does it affect you?",
        "Panic often signals danger. Can you describe it?",
        "Let's explore your fright. What stands out?",
        "It's okay to feel scared. How might you calm yourself?"
    ]
},
"gloom": {
    "keywords": ["gloom", "despondency", "sadness2"],
    "responses": [
        "Feeling gloomy is normal. What weighs on you?",
        "Despondency can be heavy. Can you describe it?",
        "Sadness can affect your mood. How does it feel?",
        "Let's explore your gloom. What stands out?",
        "It's okay to feel down. How might you uplift yourself?"
    ]
},
"gratitude2": {
    "keywords": ["gratitude2", "thankfulness", "appreciation2"],
    "responses": [
        "Feeling grateful is wonderful. What are you thankful for?",
        "Thankfulness uplifts the spirit. Can you describe it?",
        "Appreciation is valuable. How does it affect you?",
        "Let's explore your gratitude. What stands out?",
        "It's great to feel thankful. How might you express it?"
    ]
},
"guilt2": {
    "keywords": ["guilt2", "remorse2", "self-reproach"],
    "responses": [
        "Feeling guilty is tough. Can you explain why?",
        "Remorse signals reflection. How might you move forward?",
        "Self-reproach is normal. Can you explore it?",
        "Let's explore your guilt. What stands out?",
        "It's okay to feel regret. How might you forgive yourself?"
    ]
},
"hope2": {
    "keywords": ["hope2", "anticipation2", "optimism2"],
    "responses": [
        "Feeling hopeful is uplifting. What are you looking forward to?",
        "Anticipation can energize. Can you describe it?",
        "Optimism brings clarity. How does it feel?",
        "Let's reflect on your hope. What stands out?",
        "It's wonderful to feel hopeful. How might you nurture it?"
    ]
},
"humor": {
    "keywords": ["humor", "fun", "laughter"],
    "responses": [
        "Feeling humorous is fun. What made you laugh?",
        "Fun moments lift the spirit. Can you describe it?",
        "Laughter is healing. How does it feel?",
        "Let's explore your humor. What stands out?",
        "It's wonderful to feel amused. How might you enjoy it more?"
    ]
},
"impatience2": {
    "keywords": ["impatience2", "restless2", "agitation2"],
    "responses": [
        "Feeling impatient is normal. What’s causing it?",
        "Restlessness can signal tension. How does it affect you?",
        "Agitation can be heavy. Can you describe it?",
        "Let's explore your impatience. What stands out?",
        "It's okay to feel restless. How might you ease it?"
    ]
},
"infatuation": {
    "keywords": ["infatuation", "crush", "adoration2"],
    "responses": [
        "Feeling infatuated is exciting. Who or what do you adore?",
        "A crush can spark strong feelings. How does it affect you?",
        "Adoration can uplift the heart. Can you describe it?",
        "Let's explore your infatuation. What stands out?",
        "It's okay to feel attracted. How might you express it safely?"
    ]
}
}
fallback_responses = [
    "I'm listening. Tell me more about that.",
    "How does that make you feel?",
    "I see. Go on.",
    "Can you help me understand what you mean by that?",
    "That sounds important. Why do you think that is?"
]

def get_therapist_response(user_text):
    text_lower = user_text.lower()
    
    # 1. Check for specific patterns
    for category, data in therapist_patterns.items():
        for keyword in data["keywords"]:
            if keyword in text_lower:
                return random.choice(data["responses"])
    
    # 2. General empathy (Mirroring)
    if len(user_text) > 10 and " feel " in text_lower:
        return f"It sounds like those feelings are really strong. Why do you think you feel {text_lower.split(' feel ')[1].split()[0]}?"

    # 3. Fallback
    return random.choice(fallback_responses)


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"reply": "I'm here. You can say anything."})

    # Simulate thinking time for realism
    time.sleep(0.8)

    if USE_REAL_AI:
        # Placeholder for real API call (e.g., openai.ChatCompletion.create...)
        response_text = "Real AI mode is not configured yet. Please add your API key."
    else:
        response_text = get_therapist_response(user_message)

    return jsonify({"reply": response_text})

if __name__ == '__main__':
    print("MindMate Therapist Server running on http://localhost:5000")
    app.run(debug=True, port=5000)

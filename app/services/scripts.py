import random

YOUTUBE_TEMPLATES = [
    "Hey everyone! Today we're diving into {topic}. Let's break it down in a fun and easy way!",
    "Ever wondered about {topic}? Stick around because we’re going to explain it like never before!",
    "This video is all about {topic}. Make sure to watch till the end!",
]

TWITTER_TEMPLATES = [
    "Quick take on {topic}: 🧵",
    "Let’s talk about {topic}. Here’s a breakdown ↓",
    "{topic} in 3 simple points. Ready? 👇",
]

INSTAGRAM_TEMPLATES = [
    "Swipe through to learn about {topic}! 📲",
    "What is {topic}? Let me show you!",
    "Here's a quick story on {topic}! 🎥",
]

def generate(topic: str, style: str = "YouTube") -> str:
    style = style.lower()
    if style == "youtube":
        template = random.choice(YOUTUBE_TEMPLATES)
    elif style == "twitter":
        template = random.choice(TWITTER_TEMPLATES)
    elif style == "instagram":
        template = random.choice(INSTAGRAM_TEMPLATES)
    else:
        template = f"Here's a brief script about {topic}."

    return template.format(topic=topic)
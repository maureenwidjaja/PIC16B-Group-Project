#!/usr/bin/env python
# coding: utf-8

# In[1]:


# create sentiment worker module
import re

# Define sentiment words
sentiment_words = {
    # pacing of the book
    "fast-paced": ["intense", "page turner", "fast", "fast paced", "quick", "thrilling", "gripping"],
    "slow-paced": ["slow", "slow paced", "slow pacing", "gradual", "steady", "builds slowly", "patient"],
    "suspenseful": ["suspense", "suspenseful", "nail biting", "edge of your seat", "tension", "unpredictable"],
    "relaxing": ["relaxing", "relaxed", "comforting", "cozy", "lighthearted", "gentle", "easygoing"],

    # themes and mood
    "romance": ["romantic", "romance", "love", "emotional", "sweet", "dreamy", "steamy", "passionate", "chemistry"],
    "mysterious": ["mysterious", "mystery", "intriguing", "unraveling", "puzzling", "confusing", "detective"],
    "philosophical": ["philosophical", "deep", "existentialism", "helpful"],
    "magical": ["magical", "magic", "enchanting", "charming", "whimsical", "fairytale", "wondrous", "fantastical"],
    "realistic": ["believable", "gritty", "grounded", "realistic", "authentic", "genuine", "slice of life"],
    "nostalgic": ["nostalgic", "reminiscent", "bittersweet", "memories", "childhood", "wistful", "sentimental"],
    "dark": ["dark", "gloomy", "disturbing", "ominous", "gritty", "chilling", "sinister"],
    "angry": ["angry", "rage", "fiery", "furious", "frustrating", "heated", "aggressive"],
    "sad": ["sad", "depression", "emotional", "tear-jerker", "cried"],
    "funny": ["funny", "witty", "hilarious", "laughing", "sarcastic", "light-hearted", "humorous", "entertaining"],

    # emotional impact
    "heartwarming": ["heartwarming", "sweet", "uplifting", "touching", "moving", "feel-good", "comforting", "joyful"],
    "heartbreaking": ["painful", "heartbreaking", "tearjerking", "sad", "aching", "bittersweet", "poignant"],
    "depressing": ["depressing", "sad", "dark", "depression", "somber", "tragic", "dystopian", "crushing", "heavy"],
    "hopeful": ["hope", "hopeful", "optimistic", "encourage", "encouraging", "faith", "bright", "positive"],
    "inspiring": ["inspiring", "powerful", "thought-provoking", "transformative", "stirring", "soulful", "meaningful"],
    "moving": ["inspiring", "moving", "powerful", "resonant", "profound", "touching", "stirring"],

    # story depth and characters
    "character-driven": ["character development", "emotional depth", "well written", "relatable", "personal", "introspective"],
    "plot-driven": ["action-packed", "plot driven", "adventure", "packed with surprises", "suspenseful"],

    # writing style and readability
    "descriptive": ["descriptive", "vivid", "detailed", "atmospheric", "scenic", "evocative"],
    "clearly-written": ["clear", "clearly written", "straightforward", "concise", "easy to read", "smooth"],
    "dense": ["complex", "wordy", "intricate", "highly detailed", "wordy", "heavy"],
    "poetic": ["lyrical", "poetry", "elegant", "artistic", "expressive", "soulful"],
}

# Ensure the sentiment_words dictionary is not empty
if not sentiment_words:
    raise ValueError("sentiment_words dictionary is empty!")

# Create a function to extract sentiment count
def extract_sentiment_count(text):
    """Extract sentiment count from a given text."""
    if not isinstance(text, str):
        return {sentiment: 0.0 for sentiment in sentiment_words}

    # Extract words from text using regex, ignoring punctuation
    words = re.findall(r'\b\w+\b', text.lower())

    # Count sentiment words in the text
    sentiment_counts = {sentiment: sum(1 for word in words if word in keywords) 
                        for sentiment, keywords in sentiment_words.items()}

    return sentiment_counts

# Function to process sentiment scores for a single book
def process_book_sentiment(book_id_reviews):
    """Process sentiment scores for one book."""
    try:
        book_id, reviews = book_id_reviews
        if not reviews:
            return book_id, {sentiment: 0 for sentiment in sentiment_words}  # Return zero sentiment if no reviews

        combined_text = " ".join(reviews[:min(50, len(reviews))])  # Limit to first 50 reviews
        return book_id, extract_sentiment_count(combined_text)
    
    except Exception as e:
        print(f"Error processing book {book_id}: {e}")
        return book_id, None

# Prevent multiprocessing issues when running as a script
if __name__ == "__main__":
    pass


# In[ ]:





import re
import string
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer

# Ensure stopwords are downloaded
try:
    nltk.download('stopwords', quiet=True)
    from nltk.corpus import stopwords
    STOP_WORDS = set(stopwords.words('english'))
except Exception:
    # Minimal fallback stop words if NLTK fails
    STOP_WORDS = {"i", "me", "my", "we", "our", "you", "your", "he", "him", "she", "her", "it", "they", "them", "what", "which", "who", "this", "that", "am", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "into", "through", "during", "before", "after", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "can", "will", "just", "don", "should", "now"}

def clean_text(text):
    """
    Cleans raw web string into normalized ML input processing
    1. Lowercase text
    2. Remove punctuation
    3. Remove numbers
    4. Strip extraneous whitespaces
    5. Remove english stop words
    """
    if not isinstance(text, str):
        return ""
        
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\d+', '', text)
    text = " ".join(text.split())
    
    words = text.split()
    words = [w for w in words if w not in STOP_WORDS]
    
    return " ".join(words)

def extract_tfidf_features(corpus, ngram_range=(1, 2)):
    """
    Converts a pre-cleaned text corpus into vectorized space utilizing N-Grams
    """
    vectorizer = TfidfVectorizer(ngram_range=ngram_range, max_features=5000)
    X_vec = vectorizer.fit_transform(corpus)
    return X_vec, vectorizer

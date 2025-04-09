import requests
from bs4 import BeautifulSoup
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

# 1. Fetch Webpage Content
def get_website_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove scripts, styles
    for element in soup(["script", "style", "meta", "noscript"]):
        element.extract()

    return soup.get_text(separator=" ")

# 2. Clean Text
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    text = re.sub(r'[^\w\s-]', '', text)  # Keep hyphens
    words = text.lower().split()
    
    # Ensure "training" is not removed as a stopword
    stop_words = set(stopwords.words('english')) - {"training"}
    
    words = [word for word in words if word not in stop_words]
    return words

# 3. Get Keyword Frequency
def get_keywords(words, top_n=10):
    return Counter(words).most_common(top_n)

# 4. TF-IDF Analysis
def tfidf_analysis(text):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=50)
    tfidf_matrix = vectorizer.fit_transform([text])
    
    # Print full vocabulary to check if "training" appears
    print("TF-IDF Vocabulary:", vectorizer.get_feature_names_out())

    return vectorizer.get_feature_names_out()

# Run the analysis
url = "https://www.glftsh.org/"
text = get_website_text(url)

# Debug step: Check if "training" exists in extracted text
print("'training' found in raw text:", "training" in text.lower())

cleaned_words = clean_text(text)
keyword_freq = get_keywords(cleaned_words)
tfidf_keywords = tfidf_analysis(text)

print("Most Frequent Keywords:", keyword_freq)
print("TF-IDF Keywords:", tfidf_keywords)

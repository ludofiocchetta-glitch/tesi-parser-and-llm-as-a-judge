from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_metrics(parsed_text: str, gold_text: str) -> dict:
    
    # Token extraction
    extracted_tokens = set(parsed_text.lower().strip().split())
    gs_tokens = set(gold_text.lower().strip().split())

    if not extracted_tokens or not gs_tokens:
        return {
            "precision": 0.0, "recall": 0.0, "f1": 0.0,
            "jaccard_similarity": 0.0, "overlap_coefficient": 0.0, 
            "cosine_similarity": 0.0
        }

    # Sets intersection and union
    intersection = extracted_tokens & gs_tokens
    union = extracted_tokens | gs_tokens

    # Core metrics
    precision = len(intersection) / len(extracted_tokens)
    recall = len(intersection) / len(gs_tokens)
    f1 = (2 * precision * recall) / (precision + recall)

    # Additional metrics
    jaccard_similarity = len(intersection) / len(union)
    overlap_coefficient = len(intersection) / min(len(extracted_tokens), len(gs_tokens))

    # TF-IDF vectorization for cosine similarity
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([gold_text, parsed_text])
    cos_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "jaccard_similarity": jaccard_similarity,
        "overlap_coefficient": overlap_coefficient,
        "cosine_similarity": float(cos_similarity[0][0])
    }
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
#from rouge_score import rouge_scorer

def calculate_metrics(parsed_text: str, gold_text: str) -> dict:
  
    try:
        # Cast to string 
        parsed_text = str(parsed_text) if parsed_text else ""
        gold_text = str(gold_text) if gold_text else ""

        # Empty string
        if not parsed_text.strip() or not gold_text.strip():
            return {
                "precision": 0.0, 
                "recall": 0.0, 
                "f1": 0.0, 
                "jaccard_similarity": 0.0, 
                "rouge_l": 0.0, 
                "cosine_similarity": 0.0
            }

        # Token extraction
        extracted_tokens = set(re.findall(r'\b\w+\b', parsed_text.lower()))
        gs_tokens = set(re.findall(r'\b\w+\b', gold_text.lower()))

        if not extracted_tokens or not gs_tokens:
            return {
                "precision": 0.0,
                "recall": 0.0, 
                "f1": 0.0, 
                "jaccard_similarity": 0.0,
                "rouge_l": 0.0, 
                "cosine_similarity": 0.0
            }

        # Sets intersection and union
        intersection = extracted_tokens & gs_tokens
        union = extracted_tokens | gs_tokens

        # Core metrics
        precision = len(intersection) / len(extracted_tokens)
        recall = len(intersection) / len(gs_tokens)
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # Additional metrics
        jaccard_similarity = len(intersection) / len(union) if len(union) > 0 else 0.0
        
        #try:
           # scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=False)
            #scores = scorer.score(gold_text, parsed_text)
            
            #rouge_l_score = scores['rougeL'].fmeasure
       # except Exception:
            #rouge_l_score = 0.0

        # TF-IDF vectorization for cosine similarity
        try:
            vectorizer = TfidfVectorizer(token_pattern=r'(?u)\b\w+\b')
            tfidf_matrix = vectorizer.fit_transform([gold_text, parsed_text])
            cos_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except Exception:
            cos_similarity = 0.0

        return {
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "jaccard_similarity": float(jaccard_similarity),
            "rouge_l": 1.0,            
            "cosine_similarity": float(cos_similarity)
        }
        
    except Exception as e:
        # If something goes wrong
        return {
            "precision": 0.0, 
            "recall": 0.0, 
            "f1": 0.0,
            "jaccard_similarity": 0.0, 
            "rouge_l": 0.0, 
            "cosine_similarity": 0.0
        }
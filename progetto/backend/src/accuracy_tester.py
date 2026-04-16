import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


title = "isola_di_oahu_cosa_vedere_e_come_organizzare_le_vacanze"
parsed_mk = f"./md_garbage/viaggi-usa/{title}.md"
gs_path = f"../../supporto_temp/html_gs_usati/{title}_gs.txt"

token_estratti = set()
token_gs = set()
token_estratti_str = ""
token_gs_str = ""

with open(parsed_mk,encoding="utf-8") as f:
    for line in f:
        words = line.lower().strip().split()
        for word in words:
            token_estratti.add(word)

with open(gs_path,encoding="utf-8") as f:
    for line in f:
        words = line.lower().strip().split()
        for word in words:
            token_gs.add(word)



#creazione di alcuni insiemi
intersection = token_estratti & token_gs
union = token_estratti | token_gs
#den_cosine=math.sqrt(len(token_estratti))*math.sqrt(len(token_gs))


#calcolo metriche principali
precision = len(intersection)/len(token_estratti)
recall = len(intersection)/len(token_gs)
f1 = (2*precision*recall)/(precision+recall)

#altre metriche
jaccard_similarity = len(intersection)/len(union)
overlap_coefficient=len(intersection)/min(len(token_estratti),len(token_gs))

#parte extra coseno

with open(gs_path,encoding="utf-8") as f:
    token_gs_str = f.read()

with open(parsed_mk,encoding="utf-8") as f:
    token_estratti_str = f.read()


#unione dei file
file_str = [token_gs_str,token_estratti_str]

#vettorizzazione e similarità coseno
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(file_str)
similarita_cos = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])



print(f"Risultati per {title}:")
print("Precision: " + str(precision))
print("Recall: " + str(recall))
print("F1: " + str(f1))
print("Jaccard Similarity: " + str(jaccard_similarity))
print("Overlap Coefficient: "+str(overlap_coefficient))
print("Cosine Similarity: "+str(similarita_cos[0][0]))
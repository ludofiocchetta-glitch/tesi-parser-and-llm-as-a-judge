import math

title = "scooby-doo"
parsed_mk = f"{title}.md"
gs_path = f"../progetto/supporto_temp/{title}_gs.txt"

token_estratti = set()
token_gs = set()

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

intersection = token_estratti & token_gs
union = token_estratti | token_gs
den_cosine=math.sqrt(len(token_estratti))*math.sqrt(len(token_gs))


precision = len(intersection)/len(token_estratti)
recall = len(intersection)/len(token_gs)
f1 = (2*precision*recall)/(precision+recall)
jaccard_similarity = len(intersection)/len(union)
overlap_coefficient=len(intersection)/min(len(token_estratti),len(token_gs))
cosine_similarity=len(intersection)/den_cosine


print(f"Risultati per {title}:")
print("Precision: " + str(precision))
print("Recall: " + str(recall))
print("F1: " + str(f1))
print("Jaccard Similarity: " + str(jaccard_similarity))
print("Overlap Coefficient: "+str(overlap_coefficient))
print("Cosine Similarity: "+str(cosine_similarity))
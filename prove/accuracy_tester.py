title = "lanzarote"
parsed_mk = f"{title}.md"
gs_path = f"..\progetto\supporto_temp\{title}_gs.txt"

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

precision = len(token_estratti & token_gs)/len(token_estratti)
recall = len(token_estratti & token_gs)/len(token_gs)
f1 = (2*precision*recall)/(precision+recall)

print(f"Risultati per {title}:")
print("Precision: " + str(precision))
print("Recall: " + str(recall))
print("F1: " + str(f1))

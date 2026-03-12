from rag import RAG

rag = RAG()

results = rag.search("¿En qué proyectos trabajó Sebastián?")

for r in results:
    print(r)
    print("------")
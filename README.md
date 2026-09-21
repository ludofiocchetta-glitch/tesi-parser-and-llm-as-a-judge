# Oltre il Gold Standard: analisi comparativa tra metriche tradizionali e approcci LLM-as-a-Judge per la valutazione del web parsing

Repository ufficiale del progetto di tesi in Ingegneria Informatica alla Sapienza Università di Roma. 

**[Tesi completa in formato PDF](./relazione_fiocchetta_ludovica.pdf)**

Questo progetto implementa un'infrastruttura a microservizi per l'estrazione automatizzata di testo pulito dal web, tramite la libreria **Crawl4AI**, e la sua valutazione attraverso opportuni indicatori oggettivi. Il sistema supera i limiti delle metriche tradizionali integrando valutazioni avanzate e un approccio **LLM-as-a-Judge**, con il motore **Ollama** il modello **Llama 3.2**, capace di operare anche in configurazione *Reference-Free*.

## Principali funzioni

*   **Estrazione dati (web parsing):** pipeline asincrona con manipolazione del DOM e pulizia regex per estrarre testo in formato Markdown ignorando il rumore HTML (banner, menu, sidebar).
*   **Valutazione tradizionale:** calcolo di *Precision*, *Recall* e *F1-score* a livello di token.
*   **Valutazione avanzata:** integrazione di *Jaccard Similarity*, *Bigram Overlap*, *Cosine Similarity*, *METEOR* e *BERTScore* per misurare conservazione reale del significato.
*   **Paradigma LLM-as-a-Judge:** utilizzo del modello Llama 3.2 3B in locale per generare uno *score* quantitativo (1-5) e un *feedback* qualitativo sull'accuratezza dell'estrazione, con e senza *Gold Standard*.
*   **Gestione Gold Standard:** interfaccia CRUD per salvare, modificare e interrogare i testi di riferimento all'interno di un database relazionale.

##  Architettura

Il progetto è containerizzato per garantirne la massima riproducibilità ed è diviso in quattro macro-componenti:

1.  **Backend (FastAPI):** gestisce il routing asincrono, il motore di estrazione e il calcolo matematico delle metriche.
2.  **Frontend (Jinja2 + HTML/CSS):** interfaccia utente reattiva esposta tramite FastAPI per la comparazione visiva dei testi e la consultazione della dashboard statistica.
3.  **Database (MariaDB):** archiviazione persistente dell'HTML grezzo, dei testi estratti, dei *Gold Standard* e dei risultati di valutazione.
4.  **LLM Engine (Ollama):** Motore di inferenza locale per l'esecuzione del modello Llama 3.2.

## Installazione e avvio

Assicurati di avere **Docker** e **Docker Compose** installati sul tuo sistema.

1.  Clona il repository:
    ```bash
    git clone [https://github.com/ludofiocchetta-glitch/tesi-parser-and-llm-as-a-judge.git](https://github.com/ludofiocchetta-glitch/tesi-parser-and-llm-as-a-judge.git)
    cd tesi-parser-and-llm-as-a-judge/progetto
    ```

2.  Avvia l'infrastruttura a microservizi:
    ```bash
    docker-compose up --build
    ```
    *Nota: al primo avvio, lo script `init_db.py` popolerà automaticamente il database e Ollama scaricherà i pesi del modello Llama 3.2.*

## Utilizzo

Una volta che i container sono in esecuzione, puoi accedere ai servizi tramite browser:

*   **Interfaccia utente:** `http://localhost:8004`
    *   Accedi alla *Home Page* per monitorare lo stato dei servizi e decidere quale modulo provare.
    *   Usa il modulo *Parser & Evaluation* per testare l'estrazione e il giudizio su URL in tempo reale o dal database locale.
    *   Usa il modulo *Gold Standard* per inserire nuovi testi di riferimento.
    *   Usa il modulo *Stats* per visualizzare le statistiche aggregate per ogni dominio
*   **API documentata** `http://localhost:8003/docs`
    *   Esplora e testa direttamente gli tutti endpoint RESTful come `/parse`, `/evaluate` e `/evaluate_judge`.

## Domini supportati
Il sistema è attualmente configurato per estrarre e valutare dati dai seguenti domini:
*   `en.wikipedia.org`
*   `www.cbsnews.com`
*   `www.cnbc.com`
*   `www.viaggi-usa.it`

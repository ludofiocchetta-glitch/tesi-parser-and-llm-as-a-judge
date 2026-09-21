# Oltre il Gold Standard: analisi comparativa tra metriche tradizionali e approcci LLM-as-a-Judge per la valutazione del web parsing
*(Beyond the Gold Standard: a comparative analysis between traditional metrics and LLM-as-a-Judge approaches for web parsing evaluation)*

Official repository for the Computer Engineering Bachelor's thesis project at Sapienza University of Rome. 

**[Full Thesis in PDF](./relazione_fiocchetta_ludovica.pdf)**

This project implements a microservices infrastructure for the automated extraction of clean text from the web, using the **Crawl4AI** library, and its evaluation through objective metrics. The system overcomes the limitations of traditional metrics by integrating advanced semantic evaluations and an **LLM-as-a-Judge** approach, powered by the **Ollama** engine and the **Llama 3.2** model, capable of operating even in a *Reference-Free* configuration.

## Core Features

*   **Data extraction (web parsing):** asynchronous pipeline featuring DOM manipulation and regex cleaning to extract text in Markdown format while ignoring HTML noise (banners, menus, sidebars).
*   **Traditional evaluation:** token-level calculation of *Precision*, *Recall*, and *F1-score*.
*   **Advanced evaluation:** integration of *Jaccard Similarity*, *Bigram Overlap*, *Cosine Similarity*, *METEOR*, and *BERTScore* to measure the actual preservation of meaning.
*   **LLM-as-a-Judge Paradigm:** local execution of the Llama 3.2 3B model to generate a quantitative *score* (1-5) and qualitative *feedback* on extraction accuracy, both with and without a *Gold Standard*.
*   **Gold Standard Management:** CRUD interface to save, modify, and query reference texts within a relational database.

## Architecture

The project is fully containerized to ensure maximum reproducibility and is divided into four main components:

1.  **Backend (FastAPI):** handles asynchronous routing, the extraction engine, and the mathematical calculation of metrics.
2.  **Frontend (Jinja2 + HTML/CSS):** reactive user interface exposed via FastAPI for visual text comparison and access to the statistical dashboard.
3.  **Database (MariaDB):** persistent storage for raw HTML, extracted texts, *Gold Standards*, and evaluation results.
4.  **LLM Engine (Ollama):** local inference engine to run the Llama 3.2 model.

## Installation and Setup

Ensure you have **Docker** and **Docker Compose** installed on your system.

1.  Clone the repository and navigate to the project folder:
    ```bash
    git clone [https://github.com/ludofiocchetta-glitch/tesi-parser-and-llm-as-a-judge.git](https://github.com/ludofiocchetta-glitch/tesi-parser-and-llm-as-a-judge.git)
    cd tesi-parser-and-llm-as-a-judge/progetto
    ```

2.  Start the microservices infrastructure:
    ```bash
    docker-compose up --build
    ```
    *Note: On the first run, the `init_db.py` script will automatically populate the database, and Ollama will download the Llama 3.2 model weights.*

## Usage

Once the containers are running, you can access the services via your browser:

*   **User Interface:** `http://localhost:8004`
    *   Access the *Home Page* to monitor service status and choose which module to explore.
    *   Use the *Parser & Evaluation* module to test extraction and evaluation on URLs in real-time or from the local database.
    *   Use the *Gold Standard* module to insert new reference texts.
    *   Use the *Stats* module to view aggregate statistics for each domain.
*   **API Documentation (Swagger UI):** `http://localhost:8003/docs`
    *   Explore and directly test all RESTful endpoints such as `/parse`, `/evaluate`, and `/evaluate_judge`.

## Supported Domains
The system is currently configured to extract and evaluate data from the following domains:
*   `en.wikipedia.org`
*   `www.cbsnews.com`
*   `www.cnbc.com`
*   `www.viaggi-usa.it`

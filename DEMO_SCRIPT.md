# Demo Script (2–3 minutes)

## Introduction (≈30s)
"This is the Business Knowledge AI Bot. It answers questions about a company using RAG, Retrieval-Augmented Generation: instead of trusting what a language model remembers, the bot first looks up the relevant passages in a company knowledge base and only then writes an answer from them. That keeps answers grounded in the company's own documents."

## Show the knowledge base (≈15s)
Open the `knowledge-base/` folder and show the five Markdown files (about, services, careers, local-offices, insights). "This is a summary of Liquid's public web pages. It is the only source of company facts."

## Run ingestion (≈30s)
```bash
python ingest.py
```
"The documents are loaded, divided into smaller chunks, converted into TF-IDF vectors with scikit-learn and saved to a local index file — all offline, no API." Point at the summary: documents loaded, chunks created, local index created successfully.

## Launch the application (≈10s)
```bash
python app.py
```
Open the local address in the browser.

## Demonstrate five questions (≈75s)
**These match the current knowledge base. If you edit the files, adjust the questions, and run each one before recording to check the answer matches the documents.**

1. "What cloud services does Liquid offer?" (answerable from `services.md`).
2. "Where is the South Africa office and how do I contact it?" (answerable from `local-offices.md`).
3. "What job areas does Liquid recruit in?" (answerable from `careers.md`).
4. "What is the address of the Kenya office?" Only the South Africa office details are in the documents, so expect the "I don't know based on the company documents I have available" fallback.
5. "Who won the football World Cup in 2010?" Unrelated, so expect the fallback again.

For each answer, expand **Retrieved sources and context** and show which file and chunk were used.

## Explain RAG (≈30s)
```text
Question
↓
Similarity Retrieval
↓
Relevant Chunks
↓
Context
↓
Local Python answer builder
↓
Answer
```
"The question is turned into a TF-IDF vector, cosine similarity finds the most similar chunks, and only those are used to build the answer — assembled locally in Python from the documents themselves. If nothing is close enough, the bot says it doesn't know. So the chatbot is grounded in the supplied knowledge base, runs fully offline, and needs no API key."

## Recommended 5-question sequence (tells a story)

| # | Question | What it shows |
| --- | --- | --- |
| 1 | What is Liquid Intelligent Technologies? | Basic retrieval |
| 2 | What services does Liquid provide? | Knowledge retrieval |
| 3 | What countries does Liquid operate in? | Specific retrieval |
| 4 | Tell me about careers at Liquid. | A different knowledge-base section |
| 5 | What is the capital of Japan? | Fallback — proves it does not hallucinate |

The story: general question → specific question → a different document → another topic → a completely unrelated question that is refused. A bot that knows when to say *"that's not in my knowledge base"* is more trustworthy than one that answers everything.

## Full verified question set

All of the following were run against the current knowledge base and behave as marked. Green/yellow/blue questions return a grounded answer; red questions return the fallback: *"I don't know based on the company documents I have available."*

**🟢 Basic — should answer**
- What is Liquid Intelligent Technologies?
- What services does Liquid provide?
- What countries does Liquid operate in?
- What industries does Liquid serve?
- Tell me about Liquid's digital infrastructure.

**🟡 More specific — should answer**
- What connectivity solutions does Liquid offer?
- What cloud services does Liquid provide?
- What cybersecurity services does Liquid offer?
- What does Liquid say about its careers?
- Where are Liquid's offices located?
- What does Liquid's company profile say about its mission?
- What technologies or solutions does Liquid provide to businesses?

**🔵 Retrieval (paraphrased) — should answer**
- Which services are relevant to businesses that need reliable connectivity?
- What information does Liquid provide about cloud solutions?
- What does the company say about opportunities for employees?
- What can you tell me about Liquid's presence in Africa?

**🔴 Out of scope — should trigger the fallback**
- What is Liquid's CEO's favourite football team?
- What is the password to Liquid's internal systems?
- What is the capital of Japan?
- What is Liquid's revenue for 2026?
- Who is the CEO of Microsoft?

**Conversational**
- "Hi" / "Thanks" → friendly replies without touching the knowledge base.
- Empty input → asks you to type a question.

> Note: if you edit the knowledge-base files, re-run `python ingest.py` and re-check any questions whose wording depends on the changed content.

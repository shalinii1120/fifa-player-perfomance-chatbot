# FIFA Dataset SLM: Intelligent Football Question-Answering Chatbot

A domain-specific chatbot that lets users explore FIFA player-performance data through natural-language questions instead of filtering a large CSV by hand.

Built for the **Design Thinking Challenge**, B.Tech CSE (AI & ML), JAIN (Deemed-to-be University), Bengaluru.

> **Dataset note:** the FIFA World Cup 2026 Player Performance Dataset used here is **simulated / synthetic**. It is not verified official FIFA tournament statistics.

---

## Problem

- The dataset is a CSV with about **54,600 records and 75 columns**.
- Users need technical skill to filter and interpret it, and manual searching is slow.
- Users would rather **ask a normal question** and get a clear answer.

**Problem statement:** *How might we develop a domain-specific intelligent chatbot that enables users to understand, retrieve and explore FIFA player-performance information through natural-language questions?*

## Solution: hybrid architecture

```
User Question -> Domain Check -> Dataset Retrieval -> SLM / Ollama Response -> Final Answer
```

| Component | Role |
|---|---|
| Domain check | Keeps the bot in football scope; non-football questions get a domain-restriction reply |
| Pandas retrieval | Supplies factual answers from the dataset (profiles, attributes, goals, comparisons, goalkeeper analysis) |
| Fine-tuned **FLAN-T5-Small** | Small Language Model trained on FIFA question-answer pairs |
| **Ollama** (`llama3.2:3b`) | Local fallback for football questions the dataset does not directly answer |
| Streamlit | Web chat interface |

The SLM alone does **not** perform all factual retrieval. Facts are grounded in the dataset through Pandas.

## Features

- Player search and profile display
- Single- and multiple-attribute questions
- Highest / lowest goals queries
- Player and team comparisons, goalkeeper analysis
- Greeting handling (Hi, Hello)
- Football questions answered locally via Ollama
- Rejection of non-football questions

## Design Thinking journey

| Stage | What we did in this project |
|---|---|
| 1. Empathize | Identified why large FIFA CSV data is hard to understand; users want to ask questions |
| 2. Define | Wrote the problem statement, objectives and scope; chose an SLM-based approach |
| 3. Ideate | Selected the hybrid design: retrieval + SLM + Ollama |
| 4. Prototype | Prepared data, fine-tuned FLAN-T5-Small, built the Streamlit chatbot |
| 5. Test | Checked answers against the dataset; recorded hallucinations and limits |

## Development workflow

1. **Collect and inspect:** load the CSV with Pandas; check data types, missing values and duplicates.
2. **Prepare:** clean the data, convert rows into question-answer examples, split into train / validation / test, save processed files.
3. **Train:** fine-tune `google/flan-t5-small` with Hugging Face Transformers and PyTorch (Kaggle Notebook); save checkpoint and tokenizer.
4. **Build the chatbot:** Streamlit app with Pandas retrieval and Ollama integration.

## Tech stack

Python, Pandas, Hugging Face Transformers, PyTorch, FLAN-T5-Small, Streamlit, Ollama (`llama3.2:3b`), Kaggle Notebook, Hugging Face, Git and GitHub.

## Getting started

> Adjust file names to match this repository.

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd <your-repo-folder>

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) enable the Ollama fallback
ollama pull llama3.2:3b
ollama serve

# 4. Run the chatbot
streamlit run app.py
```

Place the dataset CSV and the trained FLAN-T5 checkpoint where the app expects them (see the paths in `app.py`).

## Testing summary

Test areas: player profile retrieval, single and multiple attributes, highest / lowest goals, player and team comparison, greetings, football questions via Ollama, non-football rejection, consistency with the dataset, and FLAN-T5 hallucination checks.

## Limitations

- The fine-tuned SLM may generate **incorrect numerical information**.
- Factual responses must be grounded in the dataset.
- Ollama requires the local service and model to be running.
- The chatbot is limited to the available dataset and football scope.
- Further testing and improvement are required. No accuracy score is claimed.

## Future improvements

- [ ] Improve training data quality
- [ ] Expand the question-answer dataset
- [ ] Improve model factual accuracy
- [ ] Add more advanced player-performance analytics
- [ ] Improve the UI and add conversation history
- [ ] Deploy the application publicly

## Team

- Shalini (25BTRCL166)
- LVS Ruthvik (25BTRCL127)
- Lepmuhang (25BTRCL129)

Section: CSE-AIML-C, JAIN (Deemed-to-be University), Bengaluru

## License

Add a license of your choice (for example MIT) before publishing.

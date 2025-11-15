# VariantAI — RAG Variant Interpretation Assistant

VariantAI is a retrieval-augmented generation (RAG) Streamlit application that combines OpenAI LLMs, LangChain, and a domain-specific Chroma knowledge base to assist with genomic variant interpretation. The app exposes a retriever-backed conversational interface and a set of function-calling tools for literature lookup and variant/gene lookups.

## Key features
- Retrieval-augmented answers grounded in a local Chroma vector store.
- Function-calling tools for literature search (SerpApi/Google Scholar), MyVariantInfo-like clinical lookups, and consequence/gene name helpers.
- Reusable indexing notebook to build or extend the knowledge base.
- Traceability via optional LangSmith integration.

## Repository layout (important files)
- `app.py` — Streamlit UI and RAG orchestration. Contains vectorstore loader `app.load_vectorstore` and exposes `app.retriever`.
- `function_calls.py` — Implementations of function-calling tools (e.g., `show_literature`, `get_clinical_info`, `get_consequence_info`, `get_gene_name`) and the `tools` descriptor list used by the assistant.
- `RAG.ipynb` — Notebook used to scrape/load documents, chunk text, embed, and populate the Chroma collection `variant_annotation_kb`.
- `requirements.txt` — Python dependencies.
- `chroma_langchain_db/` — Persisted Chroma embeddings and SQLite files (generated at runtime).
- `test_function_calls.py` — Unit tests for external-tool wrappers and helpers.

## Prerequisites
- Python 3.9+ (verify virtualenv or venv)
- API keys for external services as environment variables:
  - OPENAI_API_KEY (required)
  - SERP_API_KEY (optional — required for Google Scholar via SerpApi)
  - LANGSMITH_API_KEY (optional — used for tracing)
- Optional: a running local/remote Chroma instance if customizing persistence settings.

## Quickstart (local)
1. Create and activate a Python virtual environment:
```bash
python -m venv .venv
```
   - Windows: 
```bash
venv\Scripts\activate
```
   - macOS/Linux: 
```bash
source .venv/bin/activate
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Fill API keys in a `.env` file (based on `.env.example`) with required keys:
   - OPENAI_API_KEY=your_openai_api_key
   - SERP_API_KEY=your_serp_api_key  # optional
   - LANGSMITH_API_KEY=your_langsmith_api_key  # optional
4. (Optional) Rebuild or extend the Chroma DB:
   - Open `RAG.ipynb` and run the indexing workflow to scrape documents (from `knowledge_base`), chunk text, and persist embeddings in `chroma_langchain_db/`.
   - Alternately, implement a small indexing script that uses the same chunking/embedding configuration as the notebook.
5. Run the app:
```bash
streamlit run app.py
```
6. Interact with the assistant in the browser. Use function-calling prompts where relevant to trigger tool execution (literature search, variant lookups). If nessesary, user can download the char history or restart chat using setting located in left sidebar.
## Example video

![VariantAI demo](./example/example_variantAI.gif)

## Vectorstore & embeddings
- The app uses LangChain's `OpenAIEmbeddings` (or configured embedding provider) to embed documents and store them in a Chroma collection named `variant_annotation_kb`.
- Embeddings and metadata are persisted in `chroma_langchain_db/`. To force a rebuild, stop the app, delete that directory, and re-run the indexing notebook/script.

## Function-calling tools
- `function_calls.tools` contains the JSON descriptors exposed to the LLM for function calling.
- Tool implementations live in `function_calls.py`. They handle:
  - Literature search via SerpApi (if configured).
  - Clinical variant information lookups (MyVariantInfo-style wrappers or other APIs).
  - Consequence/gene name helper utilities.
- Tests in `test_function_calls.py` demonstrate mocking external APIs and exercising these helpers.

## Testing
- Run unit tests:

```bash
pytest -q
```
- Tests mock networked calls; provide small fixtures or mocks when running locally.

## Security & safety
- Outputs are informational only. Do not use VariantAI as a sole source for clinical decision making.
- Sanitize any user-submitted data before logging or persisting.
- Ensure API keys are kept out of source control and use role-limited keys when possible.

## License
- This project is provided for research and demonstration. Confirm and add a LICENSE file appropriate for your use case before redistribution.

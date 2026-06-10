# AI Feature Suggestions for Pharmax POS

**Purpose:** Reference document for unique AI-powered features to elevate the project beyond a generic POS/inventory system for the CST3990 final year project.

**Chosen features:** #1 (Text-to-SQL) and #3 (RAG Sales Copilot)

---

## Feature 1: Natural Language Business Intelligence (Text-to-SQL) ✅ CHOSEN

### What It Does
Lets the admin (pharmacy owner) ask business questions in plain English and get instant answers with data visualizations.

### Example Queries
- "What were my top 10 selling products this month?"
- "How much revenue did we make last week from cash vs. transfer?"
- "Which products haven't sold in 30 days?"
- "Show me daily sales totals for the past 2 weeks"
- "Which staff member processed the most invoices today?"

### How It Works
1. User types a question in a chat-like interface on the admin dashboard
2. The system sends the question + database schema context to an LLM
3. LLM generates a safe SQL query
4. Backend validates and executes the query
5. Results are formatted and returned — tables, charts, or summary text

### Technical Architecture
- **LLM Provider:** OpenAI API (or local via Ollama for offline mode)
- **Schema Context:** Auto-generated description of all tables/columns passed as system prompt
- **Safety Layer:** SQL query validation — read-only queries only (SELECT), no mutations
- **Response Formatter:** Detects result shape and picks table vs. chart vs. single-value display
- **Frontend:** Chat-style interface in the admin dashboard (Vue component)

### New Backend Components
- `app/services/ai/text_to_sql_service.py` — prompt construction, LLM call, SQL validation
- `app/api/routes/ai_route.py` — POST `/ai/query` endpoint
- `app/schemas/ai_schema.py` — request/response models

### Academic Value
- Prompt engineering and schema grounding techniques
- SQL injection prevention in LLM-generated queries
- Hallucination mitigation strategies (query validation, result verification)
- Evaluation methodology (accuracy of generated queries vs. expected results)
- Comparison of LLM providers/models for Text-to-SQL tasks
- Literature: Spider benchmark, DIN-SQL, C3 framework, BIRD benchmark

### Ethical Considerations
- Data privacy: queries run locally, no patient data sent to external APIs (only schema + question)
- Transparency: show the generated SQL to the user so they can verify
- Fallback: graceful handling when the LLM can't generate a valid query

### Effort Estimate
Medium. Database schema already exists. Core work is the prompt engineering, SQL validation layer, and a chat UI component.

---

## Feature 2: Prescription OCR → Auto-Invoice

### What It Does
Staff photographs a handwritten or printed prescription. AI extracts drug names and dosages, fuzzy-matches against the product catalog, and pre-populates the invoice with matched items.

### How It Works
1. Staff uploads/captures a photo of the prescription on the sales screen
2. Image is sent to an OCR/Vision model for text extraction
3. Extracted text is parsed to identify drug names, dosages, and quantities
4. Each extracted item is fuzzy-matched against the products table (name, brand, SKU)
5. Matched items are presented for staff confirmation before adding to invoice
6. Staff confirms/corrects, and items are added to the draft invoice

### Technical Architecture
- **OCR Engine:** Tesseract (local/offline) or Vision LLM API (GPT-4o, etc.)
- **Text Parsing:** Regex + NLP to extract structured drug info from raw OCR text
- **Fuzzy Matching:** Levenshtein distance / trigram similarity against product names
- **Confidence Scoring:** Each match gets a confidence score; low-confidence matches are flagged for manual review

### New Backend Components
- `app/services/ai/ocr_service.py` — image processing, OCR extraction
- `app/services/ai/prescription_parser.py` — NLP parsing of extracted text
- `app/services/ai/product_matcher.py` — fuzzy matching against product catalog
- `app/api/routes/ai_route.py` — POST `/ai/parse-prescription` endpoint

### Academic Value
- OCR accuracy analysis (handwritten vs. printed, various lighting conditions)
- Fuzzy string matching algorithms (Levenshtein, Jaro-Winkler, trigram)
- Error handling in medical/safety-critical contexts
- Ethical implications of AI in prescription processing
- Human-in-the-loop design patterns (staff always confirms before submitting)

### Ethical Considerations
- AI never auto-dispenses — staff must verify every matched item
- Misrecognition risk is explicitly communicated to the user
- Audit trail: original image stored alongside the invoice for verification
- Patient data handling (prescription images may contain patient names)

### Effort Estimate
Medium-High. OCR pipeline is the hard part. Fuzzy matching is straightforward. Invoice creation hooks into existing API.

---

## Feature 3: AI Sales Copilot (RAG over Product Catalog) ✅ CHOSEN

### What It Does
A chat interface on the sales screen where staff can ask product-related questions in natural language and get instant, contextual answers drawn from the pharmacy's own product data.

### Example Queries
- "What do we have for cough under ₦500?"
- "What's the generic alternative for Augmentin?"
- "Customer is allergic to penicillin, what can I give for infection?"
- "Do we have any children's paracetamol in stock?"
- "What's the difference between Ibuprofen 200mg and 400mg?"

### How It Works
1. Product catalog is embedded into a vector store (on startup or when products change)
2. Staff types a question in the copilot chat panel
3. Question is embedded and used to retrieve the most relevant products
4. Retrieved products + question are sent to an LLM for a contextual response
5. Response includes product suggestions with prices, stock levels, and alternatives

### Technical Architecture
- **Embedding Model:** OpenAI embeddings API or local sentence-transformers model
- **Vector Store:** ChromaDB or FAISS (lightweight, local-compatible)
- **LLM:** OpenAI API or local Ollama model for response generation
- **Index Updates:** Re-index when products are added/updated/deleted (event-driven)
- **Frontend:** Side-panel chat on the sales/invoice creation page

### New Backend Components
- `app/services/ai/embedding_service.py` — product embedding and indexing
- `app/services/ai/rag_service.py` — retrieval + LLM response generation
- `app/api/routes/ai_route.py` — POST `/ai/ask` endpoint
- Vector store file: `app/_db/product_vectors/` (local ChromaDB)

### Academic Value
- Retrieval-Augmented Generation (RAG) architecture and evaluation
- Vector embedding strategies for product catalogs
- Chunking and indexing strategies for structured data
- Hallucination prevention through grounding (only suggest products that exist in DB)
- Response quality evaluation (relevance, accuracy, helpfulness)
- Comparison: RAG vs. fine-tuning vs. plain prompting
- Literature: RAG papers (Lewis et al. 2020), vector DB comparisons

### Ethical Considerations
- AI responses always include a disclaimer: "Verify with a pharmacist"
- Never provides dosage advice — only product availability and alternatives
- Grounded in real inventory data — can't hallucinate products that don't exist
- Staff always makes the final decision on what to add to the invoice

### Effort Estimate
Medium. Most work is setting up the embedding pipeline and vector store. LLM integration is shared with Feature 1. Frontend is a chat panel component.

---

## Feature 4: Anomaly Detection for Loss Prevention

### What It Does
Monitors transaction patterns in the background and flags anomalies that could indicate theft, errors, or fraud — presented as alerts on the admin dashboard.

### What It Detects
- **Unusual void/cancel rates** — a staff member cancelling significantly more invoices than average
- **Stock discrepancies** — physical stock doesn't match expected stock based on purchases minus sales
- **Suspicious discount patterns** — repeated small adjustments that could indicate skimming
- **Unusual timing** — transactions at odd hours or unusually fast sequences
- **Controlled substance outliers** — sales of specific drug categories above normal thresholds

### How It Works
1. A background job (scheduled daily or hourly) analyzes recent transaction data
2. Statistical methods compute baselines and detect deviations
3. Flagged anomalies are stored with severity scores and explanations
4. Admin dashboard shows an alerts panel with anomalies to review
5. Admin can mark alerts as reviewed/dismissed/escalated

### Technical Architecture
- **Detection Methods:** Z-score analysis, moving averages, isolation forest (scikit-learn)
- **Scheduling:** Background task via FastAPI lifespan events or APScheduler
- **Storage:** `Anomaly` table with type, severity, details, status, related entity
- **Alerting:** Dashboard widget + optional summary in daily report

### New Backend Components
- `app/services/ai/anomaly_service.py` — detection algorithms and scoring
- `app/models/anomaly_table.py` — Anomaly model
- `app/schemas/anomaly_schema.py` — read/update schemas
- `app/api/routes/anomaly_route.py` — GET `/anomalies/`, PATCH `/anomalies/{id}`

### Academic Value
- Statistical anomaly detection techniques and their trade-offs
- False positive/negative analysis and threshold tuning
- Time-series analysis on transactional data
- Privacy and ethical considerations of employee monitoring
- Business impact analysis (estimated loss prevented)

### Ethical Considerations
- Employee monitoring must be disclosed and consented to
- Anomalies are flags for investigation, not accusations
- Privacy of transaction data — who can see anomaly reports
- False positive handling — process for clearing flagged staff

### Effort Estimate
Low-Medium. Works entirely on existing transaction data. Core algorithms are well-documented. Main work is the detection service and a dashboard alerts component.

---

## Implementation Priority

| Priority | Feature | Status | Shared Infrastructure |
|----------|---------|--------|----------------------|
| 1 | Text-to-SQL (BI) | ✅ Chosen | LLM service, AI route |
| 2 | RAG Sales Copilot | ✅ Chosen | LLM service, AI route, embeddings |
| 3 | Anomaly Detection | Future option | Background jobs |
| 4 | Prescription OCR | Future option | OCR pipeline, fuzzy matching |

### Shared Infrastructure (needed for #1 and #3)
- LLM client abstraction (supports OpenAI API + local Ollama)
- `app/services/ai/llm_client.py` — unified interface for LLM calls
- `app/api/routes/ai_route.py` — AI endpoints grouped under `/ai/`
- `app/core/ai_config.py` — API keys, model selection, temperature settings
- Environment variable: `LLM_PROVIDER=openai|ollama`

---

## Project Narrative

> "An AI-augmented pharmacy management system that enables non-technical pharmacy owners to query their business data using natural language, and assists sales staff with intelligent product recommendations — deployed for a real pharmacy in Nigeria."

This positions the project as a **domain-specific AI application** rather than a generic POS, with strong academic grounding in NLP, RAG, and human-computer interaction.

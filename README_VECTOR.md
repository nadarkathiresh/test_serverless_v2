# Fast Vector Search Chatbot (CPU-only)

⚡ **Sub-200ms response time** | 🖥️ **CPU-only** | 💰 **10-100x cheaper than LLM**

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements_vector.txt
```

### 2. Run the chatbot (CLI mode)

```bash
python3 chatbot_vector.py
```

You'll see:
```
[INIT] Loading Q&A pairs from qa_pairs.json...
[INIT] Loaded 23 Q&A pairs
[INIT] Loading embedding model: all-MiniLM-L6-v2...
[INIT] Model loaded in 1.2s
[INIT] Generating embeddings for questions...
[INIT] Embeddings generated in 0.3s
✅ Chatbot ready! 23 Q&As indexed.

🐝 Biplob World Chatbot (Vector Search)
Type your question and press Enter. Type 'quit' to exit.

You: 
```

### 3. Ask questions!

```
You: Who founded Biplob World?

🤖 Bot: Biplob World was founded by Ritika and Abhishek Talwar.
   📊 Confidence: 98.5% | ⚡ Time: 45ms
   🔍 Matched: "Who founded Biplob World?"
```

## Usage Modes

### A. Interactive CLI (default)
```bash
python3 chatbot_vector.py
```

### B. HTTP Server
```bash
python3 chatbot_vector.py --serve --port 8080
```

Then test with curl:
```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Biplob World?"}'
```

Response:
```json
{
  "answer": "Biplob World is founded by Ritika and Abhishek Talwar...",
  "confidence": 0.95,
  "response_time_ms": 42.3,
  "status": "success"
}
```

### C. Python API

```python
from chatbot_vector import VectorChatbot

chatbot = VectorChatbot(qa_file="qa_pairs.json")
result = chatbot.answer("Who is Biplob?")

print(result["answer"])
# Output: Biplob the Bumblebee is the world's first ever eco-warrior...
```

## Performance

| Metric | Value |
|--------|-------|
| **Startup time** | ~2 seconds |
| **Response time** | 30-150ms |
| **Memory usage** | ~200MB |
| **CPU usage** | Low (no GPU needed) |
| **Accuracy** | High (pre-verified answers) |

## Adding More Q&A Pairs

### Method 1: Manual (best quality)

Edit `generate_qa_pairs.py` and add to the `generate_manual_qa_pairs()` function:

```python
{
    "question": "Your new question?",
    "answer": "The accurate answer."
},
```

Then regenerate:
```bash
python3 generate_qa_pairs.py --method manual
```

### Method 2: OpenAI Auto-generation

```bash
export OPENAI_API_KEY=sk-...
python3 generate_qa_pairs.py --method openai --num-pairs 50
```

## Deployment Options

### Option 1: Local/Development
```bash
python3 chatbot_vector.py --serve --port 8080
```

### Option 2: Runpod Serverless (CPU workers)

Update `Dockerfile`:
```dockerfile
# Replace the CMD line with:
CMD ["python3", "chatbot_vector.py", "--serve", "--port", "8080"]
```

Build and deploy:
```bash
docker build -t YOUR_USER/biplob-chatbot-vector:latest .
docker push YOUR_USER/biplob-chatbot-vector:latest
```

In Runpod:
- Select **CPU workers** (much cheaper!)
- Image: `YOUR_USER/biplob-chatbot-vector:latest`
- Port: 8080
- Min workers: 1 (for instant responses)

Expected cost: **~10-50x cheaper** than GPU serverless

### Option 3: Cloud Functions (AWS Lambda, GCP Functions, etc.)

The chatbot is lightweight enough to run on serverless functions:
- Cold start: ~2s
- Warm start: 30-150ms
- Memory: 512MB sufficient

## Files

- `chatbot_vector.py` - Main chatbot (CLI + HTTP server)
- `generate_qa_pairs.py` - Q&A pair generator
- `qa_pairs.json` - Pre-generated Q&A database (23 pairs)
- `requirements_vector.txt` - CPU-only dependencies
- `product_info.txt` - Source content

## Comparison: Vector Search vs LLM

| Feature | Vector Search (NEW) | LLM Generation (OLD) |
|---------|---------------------|----------------------|
| Response time | **30-150ms** ⚡ | 5-15 seconds |
| Cold start | 2 seconds | 10-15 seconds |
| Hardware | CPU-only | GPU required |
| Cost per 1M requests | **$1-5** 💰 | $100-500 |
| Accuracy | High (verified) | Variable |
| Consistency | 100% | Variable |
| Scalability | Excellent | Moderate |

## Troubleshooting

**Q: "qa_pairs.json not found"**
```bash
python3 generate_qa_pairs.py --method manual
```

**Q: "sentence-transformers not found"**
```bash
pip install -r requirements_vector.txt
```

**Q: Responses are not accurate**
- Add more Q&A pairs to `generate_qa_pairs.py`
- Lower `similarity_threshold` (default: 0.5)
- Improve question phrasing in the Q&A database

**Q: Want to use a different embedding model?**
```bash
python3 chatbot_vector.py --model "paraphrase-MiniLM-L6-v2"
```

Faster models:
- `all-MiniLM-L6-v2` (default, ~80MB)
- `paraphrase-MiniLM-L3-v2` (smaller, faster)

Better quality (slower):
- `all-mpnet-base-v2` (better accuracy)

## Next Steps

1. ✅ Test locally: `python3 chatbot_vector.py`
2. ✅ Add more Q&A pairs to improve coverage
3. ✅ Deploy to Runpod CPU workers or cloud functions
4. ✅ Monitor response times and confidence scores
5. 📊 Consider hybrid: vector search + LLM fallback for unknown questions

---

**Need help?** Check the code comments in `chatbot_vector.py` and `generate_qa_pairs.py`


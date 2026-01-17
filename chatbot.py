import os
import time
import runpod
import torch
from typing import List, Tuple
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = os.environ.get("LLAMA_MODEL", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
CONTEXT_FILE = os.environ.get("CONTEXT_FILE", "product_info.txt")


def read_file_text(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Context file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def split_text_into_chunks(text: str, max_chars: int = 1200, overlap: int = 150) -> List[str]:
    """
    Simple character-based chunking with overlap to keep context continuity.
    """
    chunks = []
    start = 0
    text_length = len(text)
    if text_length == 0:
        return chunks
    while start < text_length:
        end = min(start + max_chars, text_length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == text_length:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


def build_retriever(chunks: List[str]) -> Tuple[TfidfVectorizer, torch.Tensor, List[str]]:
    """
    Builds a TF-IDF retriever over the provided chunks.
    Returns the vectorizer, normalized matrix, and raw chunks.
    """
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True, strip_accents="unicode")
    tfidf_matrix = vectorizer.fit_transform(chunks)
    # sklearn returns a sparse matrix; cosine_similarity will handle it directly
    return vectorizer, tfidf_matrix, chunks


def retrieve_top_k(query: str, vectorizer: TfidfVectorizer, tfidf_matrix, chunks: List[str], k: int = 3) -> List[str]:
    query_vec = vectorizer.transform([query])
    sims = cosine_similarity(query_vec, tfidf_matrix)[0]
    top_indices = sims.argsort()[::-1][:k]
    return [chunks[i] for i in top_indices if sims[i] > 0]


def format_prompt(context_snippets: List[str], question: str) -> str:
    context_text = "\n\n---\n\n".join(context_snippets)
    system = (
        "You are a helpful assistant for answering questions about Biplob World and its products.\n"
        "Use ONLY the information provided in the context below. If the answer is not contained in the context, say you don't know.\n"
        "Answer concisely and accurately."
    )
    prompt = (
        f"{system}\n\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {question}\n"
        f"Answer:"
    )
    return prompt


def load_llm_pipeline():
    """
    Lazy-load the tokenizer, model, and text-generation pipeline.
    Uses float16 when possible; falls back to float32 on CPU-only environments.
    """
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    # Read token for gated repos (e.g., Llama 3.2). HF Hub honors env var automatically,
    # but we also pass it explicitly for robustness.
    hf_token = os.environ.get("HUGGING_FACE_HUB_TOKEN") or os.environ.get("HF_TOKEN")
    
    # System info
    cuda_available = torch.cuda.is_available()
    gpu_name = torch.cuda.get_device_name(0) if cuda_available else "None"
    
    print(f"[SETUP] Loading model: {MODEL_NAME}")
    print(f"[SETUP] CUDA available: {cuda_available}")
    print(f"[SETUP] GPU: {gpu_name}")
    print(f"[SETUP] Using 4-bit quantization: {cuda_available}")
    
    hf_token = os.environ.get("HUGGING_FACE_HUB_TOKEN") or os.environ.get("HF_TOKEN")
    
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        use_fast=True,
        token=hf_token,
    )
    # Use 4-bit quantization on GPU for 2-3x speedup
    if cuda_available:
        print("[SETUP] Loading model in 4-bit mode...")
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            load_in_4bit=True,
            device_map="auto",
            token=hf_token,
        )
        print(f"[SETUP] Model loaded on: {model.device}")
    else:
        print("[SETUP] Loading model in CPU mode (slow)...")
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=dtype,
            device_map=None,
            token=hf_token,
        )
    # Ensure pad token id is set to eos if undefined to avoid warnings
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    text_gen = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device=0 if torch.cuda.is_available() else -1,
    )
    return text_gen


def assemble_context_retriever():
    text = read_file_text(CONTEXT_FILE)
    chunks = split_text_into_chunks(text)
    return build_retriever(chunks)


def chatbot_handler(event):
    global text_gen_pipeline
    global retriever_tuple
    
    start_time = time.time()
    timings = {}

    # Load model if needed
    if "text_gen_pipeline" not in globals():
        load_start = time.time()
        text_gen_pipeline = load_llm_pipeline()
        timings["model_load"] = round(time.time() - load_start, 2)

    if "retriever_tuple" not in globals():
        retriever_start = time.time()
        retriever_tuple = assemble_context_retriever()
        timings["retriever_load"] = round(time.time() - retriever_start, 2)

    input_payload = event.get("input", {}) or {}
    question = input_payload.get("question")
    if not question:
        return {"error": "No 'question' provided in input."}

    top_k = int(input_payload.get("top_k", 2))  # Reduced from 3 for faster prompts
    max_new_tokens = int(input_payload.get("max_new_tokens", 100))  # Reduced for speed
    temperature = float(input_payload.get("temperature", 0.3))

    # Retrieval timing
    retrieval_start = time.time()
    vectorizer, tfidf_matrix, chunks = retriever_tuple
    context_snippets = retrieve_top_k(question, vectorizer, tfidf_matrix, chunks, k=top_k)
    timings["retrieval"] = round(time.time() - retrieval_start, 3)

    if not context_snippets:
        # Fall back to a safe response when nothing is retrieved
        context_snippets = [
            "No specific context passages matched the question based on the provided source content."
        ]

    prompt = format_prompt(context_snippets, question)
    
    # Generation timing
    gen_start = time.time()
    outputs = text_gen_pipeline(
        prompt,
        max_new_tokens=max_new_tokens,
        do_sample=temperature > 0,
        temperature=temperature if temperature > 0 else None,
        top_p=0.9,
        num_beams=1,  # Greedy/sampling only, no beam search for speed
        eos_token_id=text_gen_pipeline.tokenizer.eos_token_id,
        pad_token_id=text_gen_pipeline.tokenizer.pad_token_id,
    )
    timings["generation"] = round(time.time() - gen_start, 2)

    # pipeline returns a list of dicts with 'generated_text'
    generated_text = outputs[0]["generated_text"]
    # Return only the part after "Answer:" if present
    answer = generated_text.split("Answer:", 1)[-1].strip() if "Answer:" in generated_text else generated_text.strip()

    timings["total"] = round(time.time() - start_time, 2)
    
    print(f"[TIMING] {timings}")

    return {
        "answer": answer,
        "timings": timings,
        "used_chunks": context_snippets,
        "model": MODEL_NAME,
    }


runpod.serverless.start({"handler": chatbot_handler})


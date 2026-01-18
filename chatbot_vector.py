"""
Fast Vector Search Chatbot for Biplob World
CPU-only, sub-200ms response time

Usage:
    # Standalone CLI
    python chatbot_vector.py

    # As a simple web server
    python chatbot_vector.py --serve --port 8080
"""

import json
import time
import argparse
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer


class VectorChatbot:
    """
    Fast vector search chatbot using pre-generated Q&A pairs.
    No GPU needed, <200ms response time.
    """
    
    def __init__(self, qa_file: str = "qa_pairs.json", model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize chatbot with Q&A pairs and embedding model.
        
        Args:
            qa_file: Path to JSON file with Q&A pairs
            model_name: Sentence transformer model (default is fast & lightweight)
        """
        print(f"[INIT] Loading Q&A pairs from {qa_file}...")
        self.qa_pairs = self._load_qa_pairs(qa_file)
        print(f"[INIT] Loaded {len(self.qa_pairs)} Q&A pairs")
        
        print(f"[INIT] Loading embedding model: {model_name}...")
        start = time.time()
        self.model = SentenceTransformer(model_name)
        print(f"[INIT] Model loaded in {time.time() - start:.2f}s")
        
        print("[INIT] Generating embeddings for questions...")
        start = time.time()
        self.questions = [qa["question"] for qa in self.qa_pairs]
        self.answers = [qa["answer"] for qa in self.qa_pairs]
        self.question_embeddings = self.model.encode(
            self.questions,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        print(f"[INIT] Embeddings generated in {time.time() - start:.2f}s")
        print(f"✅ Chatbot ready! {len(self.qa_pairs)} Q&As indexed.\n")
    
    def _load_qa_pairs(self, qa_file: str) -> List[Dict[str, str]]:
        """Load Q&A pairs from JSON file."""
        try:
            with open(qa_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ {qa_file} not found!")
            print(f"Run: python generate_qa_pairs.py")
            raise
    
    def search(self, question: str, top_k: int = 3) -> List[Tuple[str, str, float]]:
        """
        Search for similar questions and return answers.
        
        Args:
            question: User's question
            top_k: Number of results to return
            
        Returns:
            List of (matched_question, answer, similarity_score) tuples
        """
        # Encode user question
        query_embedding = self.model.encode([question], convert_to_numpy=True)[0]
        
        # Compute cosine similarity
        similarities = np.dot(self.question_embeddings, query_embedding) / (
            np.linalg.norm(self.question_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append((
                self.questions[idx],
                self.answers[idx],
                float(similarities[idx])
            ))
        
        return results
    
    def answer(self, question: str, similarity_threshold: float = 0.5) -> Dict:
        """
        Answer a question with timing information.
        
        Args:
            question: User's question
            similarity_threshold: Minimum similarity score (0-1) to return an answer
            
        Returns:
            Dict with answer, matched_question, confidence, and timing
        """
        start_time = time.time()
        
        results = self.search(question, top_k=1)
        matched_question, answer, score = results[0]
        
        total_time = time.time() - start_time
        
        # If similarity is too low, suggest the user refine their question
        if score < similarity_threshold:
            return {
                "answer": "I don't have enough information to answer that question accurately. Could you rephrase or ask something more specific about Biplob World products?",
                "matched_question": matched_question,
                "confidence": score,
                "response_time_ms": round(total_time * 1000, 2),
                "status": "low_confidence"
            }
        
        return {
            "answer": answer,
            "matched_question": matched_question,
            "confidence": round(score, 3),
            "response_time_ms": round(total_time * 1000, 2),
            "status": "success"
        }
    
    def interactive_cli(self):
        """Run interactive command-line interface."""
        print("=" * 60)
        print("🐝 Biplob World Chatbot (Vector Search)")
        print("=" * 60)
        print("Type your question and press Enter. Type 'quit' to exit.\n")
        
        while True:
            try:
                question = input("You: ").strip()
                if not question:
                    continue
                if question.lower() in ["quit", "exit", "q"]:
                    print("\n👋 Goodbye!")
                    break
                
                result = self.answer(question)
                print(f"\n🤖 Bot: {result['answer']}")
                print(f"   📊 Confidence: {result['confidence']:.2%} | ⚡ Time: {result['response_time_ms']}ms")
                if result.get("matched_question"):
                    print(f"   🔍 Matched: \"{result['matched_question']}\"")
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")


def serve_http(chatbot: VectorChatbot, port: int = 8080):
    """
    Serve chatbot as a simple HTTP API using Flask.
    Requires: pip install flask
    """
    try:
        from flask import Flask, request, jsonify
        from flask_cors import CORS
    except ImportError:
        print("❌ Flask not installed. Run: pip install flask flask-cors")
        return
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "healthy", "qa_pairs": len(chatbot.qa_pairs)})
    
    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.get_json()
        question = data.get("question", "")
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        threshold = data.get("similarity_threshold", 0.5)
        result = chatbot.answer(question, threshold)
        return jsonify(result)
    
    @app.route("/search", methods=["POST"])
    def search():
        """Return top-k similar Q&As"""
        data = request.get_json()
        question = data.get("question", "")
        top_k = data.get("top_k", 3)
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        results = chatbot.search(question, top_k)
        return jsonify({
            "results": [
                {
                    "matched_question": q,
                    "answer": a,
                    "confidence": round(s, 3)
                }
                for q, a, s in results
            ]
        })
    
    print(f"\n🚀 Starting HTTP server on http://0.0.0.0:{port}")
    print(f"   Endpoints:")
    print(f"   - GET  /health")
    print(f"   - POST /chat    (body: {{\"question\": \"...\"}})")
    print(f"   - POST /search  (body: {{\"question\": \"...\", \"top_k\": 3}})")
    print(f"\nPress Ctrl+C to stop.\n")
    
    app.run(host="0.0.0.0", port=port, debug=False)


def main():
    parser = argparse.ArgumentParser(description="Biplob World Vector Search Chatbot")
    parser.add_argument("--qa-file", default="qa_pairs.json",
                        help="Path to Q&A pairs JSON file")
    parser.add_argument("--model", default="all-MiniLM-L6-v2",
                        help="Sentence transformer model name")
    parser.add_argument("--serve", action="store_true",
                        help="Run as HTTP server instead of CLI")
    parser.add_argument("--port", type=int, default=8080,
                        help="Port for HTTP server (default: 8080)")
    
    args = parser.parse_args()
    
    # Initialize chatbot
    chatbot = VectorChatbot(qa_file=args.qa_file, model_name=args.model)
    
    # Run in selected mode
    if args.serve:
        serve_http(chatbot, port=args.port)
    else:
        chatbot.interactive_cli()


if __name__ == "__main__":
    main()


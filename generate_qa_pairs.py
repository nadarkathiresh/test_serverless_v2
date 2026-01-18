"""
Q&A Pair Generator for Biplob World Product Information

This script generates question-answer pairs from product_info.txt
You can either:
1. Run this with OpenAI API to auto-generate Q&As
2. Manually add Q&As to qa_pairs.json

Usage:
    python generate_qa_pairs.py --api openai  # Use OpenAI API
    python generate_qa_pairs.py --manual       # Use manual Q&As
"""

import json
import os
import argparse
from typing import List, Dict


def read_product_info(filepath: str = "product_info.txt") -> str:
    """Read the product information file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def generate_manual_qa_pairs() -> List[Dict[str, str]]:
    """
    Manually curated Q&A pairs based on product_info.txt
    These are high-quality, guaranteed accurate answers.
    """
    qa_pairs = [
        {
            "question": "What is Biplob World?",
            "answer": "Biplob World is founded by Ritika and Abhishek Talwar. They create story-based content for kids aged 2–14 in the form of storybooks, STEM games, toys, videos and DIY kits. They cover 2 main themes – Sustainability and Indian History and Heritage."
        },
        {
            "question": "Who founded Biplob World?",
            "answer": "Biplob World was founded by Ritika and Abhishek Talwar."
        },
        {
            "question": "What age groups does Biplob World cater to?",
            "answer": "Biplob World creates content for kids aged 2–14 years old."
        },
        {
            "question": "What are the main themes of Biplob World?",
            "answer": "The two main themes are Sustainability and Indian History and Heritage."
        },
        {
            "question": "Who is Biplob the Bumblebee?",
            "answer": "Biplob the Bumblebee is the world's first ever eco-warrior superhero. He is a loveable character that lives on a farm and helps friends find 100% natural solutions to everyday problems, teaching children about concepts like rainwater harvesting, solar energy, and sustainable development."
        },
        {
            "question": "What age is Biplob's World content suitable for?",
            "answer": "Biplob's World is suitable for children aged 2 and above."
        },
        {
            "question": "Who is Detective Col. Zoro?",
            "answer": "Detective Col. Zoro is an Indian Panther Hound detective who solves mystery cases that reveal unknown facets of Indian history. The content is suitable for children aged 6 and above."
        },
        {
            "question": "What is the ZoroVerse?",
            "answer": "The ZoroVerse is a world inhabited only by dogs where Detective Col. Zoro solves cases with his friends Dr. Simsim the archaeologist, Major Dom the bulldog, and Major Tipu the Rottweiler commando. It consists of short novels, boardgames, and cool toys."
        },
        {
            "question": "Who is the author of Biplob World content?",
            "answer": "All content is authored by Abhishek Talwar, a certified sustainability expert and history enthusiast. He has authored over 70 titles in the BIPLOB and Col. Zoro series."
        },
        {
            "question": "How many books and games has Biplob World sold?",
            "answer": "Biplob World has sold over 1 million books and games across India."
        },
        {
            "question": "What types of products does Biplob World offer?",
            "answer": "Biplob World offers storybooks, STEM games, toys, videos, DIY kits, boardgames, flashcards, T-shirts, sippers, caps, and other merchandise."
        },
        {
            "question": "What are the 17 SDGs mentioned in Biplob's stories?",
            "answer": "The stories help children understand the 17 Sustainable Development Goals (SDGs) and concepts like rainwater harvesting, human-animal conflict, solar energy, and sustainable development."
        },
        {
            "question": "What historical figures are covered in Col. Zoro stories?",
            "answer": "Col. Zoro stories cover legends like Chhatrapati Shivaji Maharaj, Lalitaditya Muktapida, and Rani Naiki Devi."
        },
        {
            "question": "How do Biplob games help child development?",
            "answer": "Biplob games and DIY kits help develop motor skills through puzzle games, board games, card games, and physical books. They support both gross motor skills (running, climbing) and fine motor skills (gripping, turning pages)."
        },
        {
            "question": "What is the recommended screen time for children?",
            "answer": "According to the Indian Academy of Pediatrics: Children below 2 years should have no screen time, children 2-5 years should have maximum 1 hour of supervised screen time, and children 5-10 should have less than 2 hours of screen time."
        },
        {
            "question": "How can parents reduce their kids' screen time?",
            "answer": "Parents can set clear rules and limits, create screen-free zones (dining room, bedrooms), schedule screen-free times (meals, homework, before bedtime), encourage active alternatives like outdoor play and reading, be a role model, and reward screen-free behavior."
        },
        {
            "question": "What are Biplob Early Learner books?",
            "answer": "Biplob Early Learner Book 1 to 10 combo is for children aged 2 and above. Using simple language and colorful illustrations, these books combine fun activities with lessons on positive values and good habits."
        },
        {
            "question": "What makes Abhishek Talwar's writing style unique?",
            "answer": "Abhishek has a typical 'entertainment-first' style to content creation, which ensures children are thoroughly engaged with the narrative. Learning happens seamlessly as a result of engagement with the content."
        },
        {
            "question": "What STEM.org certified products does Biplob World have?",
            "answer": "Biplob World has several STEM.org certified DIY kits, games, and toys that children can play with for hours of educational fun."
        },
        {
            "question": "Can I use Biplob products for family bonding?",
            "answer": "Yes! Biplob World has many fun and educational boardgames that are perfect for spending quality time together as a family, especially during screen-free times."
        },
        {
            "question": "What is the Adventures of Biplob the Bumblebee series about?",
            "answer": "This charming series introduces kids to eco-friendly and sustainable habits through the adventures of Biplob, a clever little bumblebee who loves helping others and the environment. The short chapters, captivating illustrations, and incredible storytelling make it perfect for young readers."
        },
        {
            "question": "How do I choose the right Biplob book for my child?",
            "answer": "Look for books that match your child's interests (animals, colors, humor, adventure, etc.) and age. Biplob Early Learner books (age 2+) have large print, plenty of visuals, and easy-to-follow plots. For older children (6+), the Col. Zoro mystery series offers more complex stories."
        },
        {
            "question": "Are there videos available from Biplob World?",
            "answer": "Yes, Biplob World offers short videos and animated content featuring Biplob the Bumblebee and Col. Zoro characters for educational infotainment."
        }
    ]
    return qa_pairs


def generate_with_openai(product_text: str, api_key: str, num_pairs: int = 50) -> List[Dict[str, str]]:
    """
    Generate Q&A pairs using OpenAI API.
    Requires: pip install openai
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        prompt = f"""Based on the following product information, generate {num_pairs} diverse question-answer pairs.
Make the questions natural (how people would actually ask) and answers accurate and concise.

Product Information:
{product_text}

Return ONLY a JSON array in this exact format:
[{{"question": "...", "answer": "..."}}, ...]
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Q&A pair generator. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        
        content = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        qa_pairs = json.loads(content)
        return qa_pairs
        
    except ImportError:
        print("OpenAI package not installed. Run: pip install openai")
        return []
    except Exception as e:
        print(f"Error generating with OpenAI: {e}")
        return []


def save_qa_pairs(qa_pairs: List[Dict[str, str]], output_file: str = "qa_pairs.json"):
    """Save Q&A pairs to JSON file."""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(qa_pairs, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(qa_pairs)} Q&A pairs to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate Q&A pairs for Biplob World")
    parser.add_argument("--method", choices=["manual", "openai"], default="manual",
                        help="Method to generate Q&A pairs")
    parser.add_argument("--api-key", help="OpenAI API key (if using openai method)")
    parser.add_argument("--num-pairs", type=int, default=50,
                        help="Number of Q&A pairs to generate (for openai method)")
    parser.add_argument("--output", default="qa_pairs.json",
                        help="Output JSON file")
    
    args = parser.parse_args()
    
    if args.method == "manual":
        print("📝 Using manually curated Q&A pairs...")
        qa_pairs = generate_manual_qa_pairs()
    elif args.method == "openai":
        if not args.api_key:
            args.api_key = os.environ.get("OPENAI_API_KEY")
        if not args.api_key:
            print("❌ OpenAI API key required. Set --api-key or OPENAI_API_KEY env var")
            return
        print(f"🤖 Generating {args.num_pairs} Q&A pairs with OpenAI...")
        product_text = read_product_info()
        qa_pairs = generate_with_openai(product_text, args.api_key, args.num_pairs)
        if not qa_pairs:
            print("⚠️  Generation failed. Falling back to manual Q&As...")
            qa_pairs = generate_manual_qa_pairs()
    
    save_qa_pairs(qa_pairs, args.output)
    print(f"\n✨ Done! You can now run: python chatbot_vector.py")


if __name__ == "__main__":
    main()


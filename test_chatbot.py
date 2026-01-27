"""
Simple test script to demo the vector chatbot
"""

from chatbot_vector import VectorChatbot

print("🔄 Initializing chatbot...")
chatbot = VectorChatbot(qa_file="qa_pairs.json")

# Test questions (including greetings)
test_questions = [
    "Hi",
    "Hello there",
    "Who founded Biplob World?",
    "What is Biplob the Bumblebee?",
    "What age groups does Biplob World cater to?",
    "Tell me about Col. Zoro",
]

print("\n" + "="*60)
print("🤖 TESTING CHATBOT")
print("="*60 + "\n")

for question in test_questions:
    print(f"❓ Q: {question}")
    result = chatbot.answer(question)
    print(f"✅ A: {result['answer']}")
    print(f"   📊 Confidence: {result['confidence']:.1%} | ⚡ {result['response_time_ms']}ms")
    print()

print("="*60)
print("✨ All tests complete!")
print("\nTo use interactively, run: python3 chatbot_vector.py")
print("="*60)

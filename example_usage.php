<?php
/**
 * Example usage of Biplob World Chatbot PHP Client
 * 
 * Make sure the Python chatbot server is running:
 * python3 chatbot_vector.py --serve --port 8080
 */

require_once 'BiplobChatbot.php';

// Initialize the chatbot client
// Use the URL where your Python chatbot is running
$chatbot = new BiplobChatbot('http://localhost:8080', 10);

echo "======================================\n";
echo "Biplob World Chatbot - PHP Examples\n";
echo "======================================\n\n";

// Example 1: Check if service is healthy
echo "1. Health Check\n";
echo "   Status: " . ($chatbot->isHealthy() ? "✅ Healthy" : "❌ Unhealthy") . "\n\n";

// Example 2: Simple question (returns full response)
echo "2. Ask a Question (Full Response)\n";
$question = "Who founded Biplob World?";
echo "   Q: $question\n";
$result = $chatbot->ask($question);

if ($result) {
    echo "   A: {$result['answer']}\n";
    echo "   Confidence: " . round($result['confidence'] * 100, 1) . "%\n";
    echo "   Response Time: {$result['response_time_ms']}ms\n";
    echo "   Status: {$result['status']}\n\n";
} else {
    echo "   Error: " . $chatbot->getLastError() . "\n\n";
}

// Example 3: Get clean answer text only
echo "3. Get Simple Answer (Text Only)\n";
$question = "What age groups does Biplob World cater to?";
echo "   Q: $question\n";
$answer = $chatbot->getAnswer($question);
echo "   A: $answer\n\n";

// Example 4: Search for multiple similar answers
echo "4. Search Multiple Results\n";
$question = "Tell me about sustainability";
echo "   Q: $question\n";
$searchResults = $chatbot->search($question, 3);

if ($searchResults) {
    foreach ($searchResults['results'] as $index => $result) {
        $num = $index + 1;
        $confidence = round($result['confidence'] * 100, 1);
        echo "   Result $num ($confidence% match):\n";
        echo "   - Matched: {$result['matched_question']}\n";
        echo "   - Answer: " . substr($result['answer'], 0, 100) . "...\n\n";
    }
} else {
    echo "   Error: " . $chatbot->getLastError() . "\n\n";
}

// Example 5: Handle low confidence answers
echo "5. Low Confidence Handling\n";
$question = "What is the weather today?";
echo "   Q: $question\n";
$result = $chatbot->ask($question, 0.7); // Higher threshold

if ($result) {
    echo "   Status: {$result['status']}\n";
    echo "   Confidence: " . round($result['confidence'] * 100, 1) . "%\n";
    echo "   A: {$result['answer']}\n\n";
}

// Example 6: Error handling
echo "6. Error Handling\n";
$result = $chatbot->ask("");
if ($result === null) {
    echo "   Error caught: " . $chatbot->getLastError() . "\n\n";
}

echo "======================================\n";
echo "✨ Examples complete!\n";
echo "======================================\n";

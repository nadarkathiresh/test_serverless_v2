<?php
/**
 * Chatbot API Endpoint
 * 
 * This file handles AJAX requests from the chat widget
 * and communicates with the Python chatbot server.
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

require_once 'BiplobChatbot.php';

// Configuration
define('CHATBOT_URL', 'http://localhost:8080'); // Change this to your chatbot server URL
define('CHATBOT_TIMEOUT', 10);

try {
    // Get JSON input
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);
    
    if (!$data || !isset($data['question'])) {
        throw new Exception('No question provided');
    }
    
    $question = trim($data['question']);
    
    if (empty($question)) {
        throw new Exception('Question cannot be empty');
    }
    
    // Initialize chatbot
    $chatbot = new BiplobChatbot(CHATBOT_URL, CHATBOT_TIMEOUT);
    
    // Check if service is healthy
    if (!$chatbot->isHealthy()) {
        throw new Exception('Chatbot service is not available. Please try again later.');
    }
    
    // Get answer
    $similarityThreshold = $data['similarity_threshold'] ?? 0.5;
    $result = $chatbot->ask($question, $similarityThreshold);
    
    if ($result === null) {
        throw new Exception($chatbot->getLastError() ?? 'Failed to get response from chatbot');
    }
    
    // Return successful response
    echo json_encode([
        'success' => true,
        'answer' => $result['answer'],
        'confidence' => $result['confidence'],
        'response_time_ms' => $result['response_time_ms'],
        'status' => $result['status'],
        'matched_question' => $result['matched_question'] ?? null
    ]);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ]);
}

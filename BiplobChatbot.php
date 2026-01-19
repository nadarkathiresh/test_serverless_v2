<?php
/**
 * Biplob World Chatbot PHP Client
 * 
 * Simple PHP wrapper to communicate with the Python vector chatbot API.
 * 
 * @author Biplob World
 * @version 1.0
 */

class BiplobChatbot
{
    private string $baseUrl;
    private int $timeout;
    private ?string $lastError = null;
    
    /**
     * Initialize the chatbot client
     * 
     * @param string $baseUrl Base URL of the chatbot server (e.g., 'http://localhost:8080')
     * @param int $timeout Request timeout in seconds (default: 10)
     */
    public function __construct(string $baseUrl = 'http://localhost:8080', int $timeout = 10)
    {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->timeout = $timeout;
    }
    
    /**
     * Ask a question and get an answer
     * 
     * @param string $question The user's question
     * @param float $similarityThreshold Minimum confidence score (0.0 - 1.0)
     * @return array|null Response array or null on error
     * 
     * Response format:
     * [
     *   'answer' => 'The answer text',
     *   'confidence' => 0.95,
     *   'response_time_ms' => 45.2,
     *   'status' => 'success',
     *   'matched_question' => 'Original question matched'
     * ]
     */
    public function ask(string $question, float $similarityThreshold = 0.5): ?array
    {
        if (empty($question)) {
            $this->lastError = "Question cannot be empty";
            return null;
        }
        
        $payload = [
            'question' => $question,
            'similarity_threshold' => $similarityThreshold
        ];
        
        $response = $this->makeRequest('/chat', $payload);
        
        if ($response === null) {
            return null;
        }
        
        return $response;
    }
    
    /**
     * Search for similar questions (returns top K results)
     * 
     * @param string $question The user's question
     * @param int $topK Number of results to return
     * @return array|null Array of results or null on error
     * 
     * Response format:
     * [
     *   'results' => [
     *     [
     *       'matched_question' => '...',
     *       'answer' => '...',
     *       'confidence' => 0.95
     *     ],
     *     ...
     *   ]
     * ]
     */
    public function search(string $question, int $topK = 3): ?array
    {
        if (empty($question)) {
            $this->lastError = "Question cannot be empty";
            return null;
        }
        
        $payload = [
            'question' => $question,
            'top_k' => $topK
        ];
        
        $response = $this->makeRequest('/search', $payload);
        
        if ($response === null) {
            return null;
        }
        
        return $response;
    }
    
    /**
     * Check if the chatbot service is healthy
     * 
     * @return bool True if healthy, false otherwise
     */
    public function isHealthy(): bool
    {
        try {
            $ch = curl_init($this->baseUrl . '/health');
            curl_setopt_array($ch, [
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_TIMEOUT => 5,
                CURLOPT_HTTPGET => true,
            ]);
            
            $response = curl_exec($ch);
            $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            curl_close($ch);
            
            return $httpCode === 200;
        } catch (Exception $e) {
            $this->lastError = "Health check failed: " . $e->getMessage();
            return false;
        }
    }
    
    /**
     * Get the last error message
     * 
     * @return string|null Error message or null if no error
     */
    public function getLastError(): ?string
    {
        return $this->lastError;
    }
    
    /**
     * Make an HTTP request to the chatbot API
     * 
     * @param string $endpoint API endpoint (e.g., '/chat')
     * @param array $payload Request payload
     * @return array|null Response data or null on error
     */
    private function makeRequest(string $endpoint, array $payload): ?array
    {
        $url = $this->baseUrl . $endpoint;
        
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($payload),
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json',
                'Accept: application/json'
            ],
            CURLOPT_TIMEOUT => $this->timeout,
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);
        
        if ($error) {
            $this->lastError = "cURL error: $error";
            return null;
        }
        
        if ($httpCode !== 200) {
            $this->lastError = "HTTP error $httpCode: $response";
            return null;
        }
        
        $data = json_decode($response, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            $this->lastError = "JSON decode error: " . json_last_error_msg();
            return null;
        }
        
        return $data;
    }
    
    /**
     * Get formatted answer text (strips metadata, returns clean answer)
     * 
     * @param string $question The user's question
     * @return string Answer text or error message
     */
    public function getAnswer(string $question): string
    {
        $result = $this->ask($question);
        
        if ($result === null) {
            return "Sorry, I couldn't process your question. Please try again.";
        }
        
        return $result['answer'] ?? 'No answer available.';
    }
}

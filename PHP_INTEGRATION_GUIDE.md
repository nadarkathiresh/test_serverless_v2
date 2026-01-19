# PHP Integration Guide - Biplob World Chatbot

Complete guide to integrate the vector chatbot with your PHP application.

## 📁 Files Created

1. **`BiplobChatbot.php`** - PHP client class (use this in your PHP code)
2. **`chatbot_api.php`** - REST API endpoint (for AJAX calls)
3. **`chatbot_widget.php`** - Example chat widget UI
4. **`example_usage.php`** - CLI usage examples

## 🚀 Quick Start

### Step 1: Start the Python Chatbot Server

```bash
cd /Users/kathiresh.nadar/Documents/KT_Projects/GPU_Projects/test_serverless_v2
python3 chatbot_vector.py --serve --port 8080
```

Keep this running in the background.

### Step 2: Test PHP Integration

#### A. Command Line Test
```bash
php example_usage.php
```

#### B. Web Browser Test
```bash
# Start PHP built-in server
php -S localhost:9000

# Open in browser:
# http://localhost:9000/chatbot_widget.php
```

## 📚 Integration Methods

### Method 1: Direct PHP Integration (Server-Side)

Use this when you want to call the chatbot from your PHP backend code.

```php
<?php
require_once 'BiplobChatbot.php';

// Initialize
$chatbot = new BiplobChatbot('http://localhost:8080');

// Ask a question
$result = $chatbot->ask("Who founded Biplob World?");

if ($result) {
    echo $result['answer'];
} else {
    echo "Error: " . $chatbot->getLastError();
}
?>
```

**Use Cases:**
- Contact form responses
- FAQ pages
- Email auto-responses
- Backend processing

### Method 2: AJAX/API Integration (Client-Side)

Use this for interactive chat widgets or single-page applications.

**Setup:**
1. Copy `chatbot_api.php` to your web root
2. Update `CHATBOT_URL` in `chatbot_api.php`
3. Make AJAX calls from JavaScript

**Example:**
```javascript
fetch('chatbot_api.php', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: 'What is Biplob World?' })
})
.then(res => res.json())
.then(data => {
    console.log(data.answer);
});
```

**Use Cases:**
- Live chat widgets
- Interactive Q&A sections
- Chatbots on product pages

### Method 3: WordPress/CMS Integration

```php
<?php
// In your WordPress theme functions.php or custom plugin

require_once get_template_directory() . '/BiplobChatbot.php';

function biplob_chatbot_shortcode($atts) {
    $atts = shortcode_atts([
        'question' => ''
    ], $atts);
    
    if (empty($atts['question'])) {
        return '';
    }
    
    $chatbot = new BiplobChatbot('http://localhost:8080');
    $answer = $chatbot->getAnswer($atts['question']);
    
    return '<div class="biplob-answer">' . esc_html($answer) . '</div>';
}

add_shortcode('biplob_ask', 'biplob_chatbot_shortcode');

// Usage in posts/pages:
// [biplob_ask question="Who founded Biplob World?"]
?>
```

## 🎯 Common Use Cases

### 1. FAQ Page Automation

```php
<?php
require_once 'BiplobChatbot.php';
$chatbot = new BiplobChatbot('http://localhost:8080');

$faqs = [
    "What is Biplob World?",
    "Who founded Biplob World?",
    "What age groups do you cater to?",
    "What products do you offer?"
];

foreach ($faqs as $question) {
    $answer = $chatbot->getAnswer($question);
    echo "<div class='faq-item'>";
    echo "<h3>Q: $question</h3>";
    echo "<p>A: $answer</p>";
    echo "</div>";
}
?>
```

### 2. Contact Form Auto-Response

```php
<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    require_once 'BiplobChatbot.php';
    $chatbot = new BiplobChatbot('http://localhost:8080');
    
    $userQuestion = $_POST['message'];
    $result = $chatbot->ask($userQuestion);
    
    if ($result && $result['confidence'] > 0.7) {
        // Send auto-response email with the answer
        $autoResponse = "Thank you for your question!\n\n";
        $autoResponse .= "Q: $userQuestion\n";
        $autoResponse .= "A: {$result['answer']}\n\n";
        $autoResponse .= "If you need more information, we'll get back to you soon!";
        
        mail($_POST['email'], 'Re: Your Question', $autoResponse);
    } else {
        // Forward to support team for manual response
        mail('support@biplobworld.com', 'New Question', $userQuestion);
    }
}
?>
```

### 3. Product Page Q&A

```php
<?php
// Display on product pages
require_once 'BiplobChatbot.php';
$chatbot = new BiplobChatbot('http://localhost:8080');

// Get product-specific questions
$productQuestions = [
    "Tell me about Biplob games",
    "What DIY kits do you offer?",
    "Are there Col. Zoro toys available?"
];

$results = [];
foreach ($productQuestions as $q) {
    $result = $chatbot->ask($q);
    if ($result && $result['confidence'] > 0.6) {
        $results[] = [
            'question' => $q,
            'answer' => $result['answer']
        ];
    }
}
?>

<div class="product-qa">
    <h3>Common Questions</h3>
    <?php foreach ($results as $qa): ?>
        <div class="qa-item">
            <strong><?= htmlspecialchars($qa['question']) ?></strong>
            <p><?= htmlspecialchars($qa['answer']) ?></p>
        </div>
    <?php endforeach; ?>
</div>
```

## 🔧 Configuration

### BiplobChatbot.php Configuration

```php
// Change the chatbot server URL
$chatbot = new BiplobChatbot('http://your-server:8080', 10);

// Adjust confidence threshold
$result = $chatbot->ask($question, 0.7); // 70% minimum confidence

// Get multiple results
$results = $chatbot->search($question, 5); // Top 5 results
```

### chatbot_api.php Configuration

Edit these lines in `chatbot_api.php`:

```php
// Line 14-15: Change to your chatbot server
define('CHATBOT_URL', 'http://localhost:8080');
define('CHATBOT_TIMEOUT', 10);
```

## 🌐 Production Deployment

### Option 1: Same Server

If PHP and Python run on the same server:

```bash
# Use localhost
$chatbot = new BiplobChatbot('http://localhost:8080');
```

### Option 2: Separate Server

If chatbot runs on a different server:

```bash
# Use internal/external IP or domain
$chatbot = new BiplobChatbot('http://chatbot.yourserver.com:8080');
```

### Option 3: Runpod/Cloud Deployment

Deploy Python chatbot to Runpod, then:

```php
// Use your Runpod endpoint URL
$chatbot = new BiplobChatbot('https://your-endpoint.runpod.io');
```

## 🔒 Security Best Practices

### 1. Environment Variables

```php
<?php
// Don't hardcode URLs in production
$chatbotUrl = getenv('CHATBOT_URL') ?: 'http://localhost:8080';
$chatbot = new BiplobChatbot($chatbotUrl);
?>
```

### 2. Rate Limiting

```php
<?php
session_start();

// Limit to 10 questions per session per hour
$limit = 10;
$key = 'chatbot_requests_' . session_id();

if (!isset($_SESSION[$key])) {
    $_SESSION[$key] = ['count' => 0, 'reset' => time() + 3600];
}

if (time() > $_SESSION[$key]['reset']) {
    $_SESSION[$key] = ['count' => 0, 'reset' => time() + 3600];
}

if ($_SESSION[$key]['count'] >= $limit) {
    die(json_encode(['error' => 'Rate limit exceeded']));
}

$_SESSION[$key]['count']++;
?>
```

### 3. Input Validation

```php
<?php
function validateQuestion($question) {
    // Remove HTML tags
    $question = strip_tags($question);
    
    // Limit length
    if (strlen($question) > 500) {
        throw new Exception('Question too long (max 500 characters)');
    }
    
    // Check for spam patterns
    if (preg_match('/viagra|cialis|casino/i', $question)) {
        throw new Exception('Invalid question');
    }
    
    return $question;
}
?>
```

## 🐛 Troubleshooting

### Error: "cURL error: Failed to connect"

**Solution:**
- Make sure Python chatbot server is running
- Check the URL/port in `BiplobChatbot.php`
- Test with: `curl http://localhost:8080/health`

### Error: "Chatbot service is not available"

**Solution:**
```bash
# Restart the Python server
python3 chatbot_vector.py --serve --port 8080
```

### Slow Responses (>5 seconds)

**Solutions:**
1. Keep the Python server warm (don't restart frequently)
2. Use caching for common questions
3. Consider hosting closer to your PHP server

### Caching Example

```php
<?php
function getCachedAnswer($question) {
    $cacheKey = 'chatbot_' . md5($question);
    $cached = apcu_fetch($cacheKey);
    
    if ($cached !== false) {
        return $cached;
    }
    
    $chatbot = new BiplobChatbot('http://localhost:8080');
    $answer = $chatbot->getAnswer($question);
    
    // Cache for 1 hour
    apcu_store($cacheKey, $answer, 3600);
    
    return $answer;
}
?>
```

## 📊 Monitoring & Analytics

### Log All Queries

```php
<?php
function logChatbotQuery($question, $result) {
    $log = [
        'timestamp' => date('Y-m-d H:i:s'),
        'question' => $question,
        'confidence' => $result['confidence'] ?? 0,
        'response_time' => $result['response_time_ms'] ?? 0
    ];
    
    file_put_contents(
        'chatbot_logs.json',
        json_encode($log) . "\n",
        FILE_APPEND
    );
}
?>
```

## 📞 Support

For issues or questions:
1. Check the Python server logs
2. Enable error_reporting in PHP
3. Test with `example_usage.php` first
4. Review `README_VECTOR.md` for Python setup

## ✅ Checklist

Before going live:

- [ ] Python chatbot server is running
- [ ] PHP can connect to the chatbot (test with `example_usage.php`)
- [ ] URLs are configured correctly in all files
- [ ] Rate limiting is enabled
- [ ] Input validation is in place
- [ ] Error handling is implemented
- [ ] Caching is configured (optional but recommended)
- [ ] Monitoring/logging is set up

---

**Quick Reference:**

- Start server: `python3 chatbot_vector.py --serve --port 8080`
- Test PHP: `php example_usage.php`
- Test web: `php -S localhost:9000` → `http://localhost:9000/chatbot_widget.php`
- Check health: `curl http://localhost:8080/health`

#!/usr/bin/env python3
"""
⚡ Memory Vault API Integration Demo
Demonstrates how to integrate MemoryLink into your applications
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

class MemoryVaultAPI:
    """Memory Vault API Client - Production-ready example"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
    
    def health_check(self) -> bool:
        """Check if the API is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
    
    def store_memory(self, content: str, metadata: Optional[Dict] = None) -> Dict:
        """Store a new memory"""
        payload = {
            "content": content,
            "metadata": metadata or {}
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/memories/",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def search_memories(self, query: str, limit: int = 10, threshold: float = 0.3) -> List[Dict]:
        """Search memories semantically"""
        payload = {
            "query": query,
            "limit": limit,
            "threshold": threshold
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/search/",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_all_memories(self) -> List[Dict]:
        """Retrieve all stored memories"""
        try:
            response = self.session.get(f"{self.base_url}/memories/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

def print_banner():
    """Display demo banner"""
    print(f"{Colors.CYAN}")
    print("⚡" + "═" * 55 + "⚡")
    print("       MEMORY VAULT API INTEGRATION DEMO")
    print("        Learn to build with MemoryLink")
    print("           Production-ready examples")
    print("⚡" + "═" * 55 + "⚡")
    print(f"{Colors.END}")

def print_code_example(title: str, code: str, language: str = "python"):
    """Print a syntax-highlighted code example"""
    print(f"\n{Colors.BOLD}{Colors.PURPLE}📝 {title}{Colors.END}")
    print(f"{Colors.CYAN}```{language}{Colors.END}")
    print(f"{Colors.GREEN}{code}{Colors.END}")
    print(f"{Colors.CYAN}```{Colors.END}")

def demo_basic_operations(api: MemoryVaultAPI):
    """Demonstrate basic API operations"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🎯 LEVEL 4A: Basic API Operations{Colors.END}")
    print("─" * 50)
    
    # Example 1: Storing a memory
    print(f"{Colors.YELLOW}1. Storing a new memory...{Colors.END}")
    
    demo_content = """
Kubernetes is an open-source container orchestration platform that automates deploying, 
scaling, and managing containerized applications. It groups containers into logical units 
called pods and provides features like service discovery, load balancing, storage 
orchestration, and automated rollouts/rollbacks.

Key concepts:
- Pods: Smallest deployable units
- Services: Stable network endpoints  
- Deployments: Manage replica sets
- ConfigMaps/Secrets: Configuration management
- Ingress: External access to services
    """
    
    result = api.store_memory(
        content=demo_content.strip(),
        metadata={
            "topic": "devops",
            "technology": "kubernetes",
            "difficulty": "intermediate",
            "source": "api_demo",
            "timestamp": datetime.now().isoformat(),
            "demo": True
        }
    )
    
    if "error" not in result:
        print(f"{Colors.GREEN}✅ Memory stored successfully!{Colors.END}")
        print(f"   Memory ID: {result.get('id', 'N/A')}")
    else:
        print(f"{Colors.RED}❌ Failed to store memory: {result['error']}{Colors.END}")
    
    time.sleep(1)
    
    # Example 2: Searching memories
    print(f"\n{Colors.YELLOW}2. Searching for container orchestration...{Colors.END}")
    
    search_results = api.search_memories(
        query="container orchestration platforms",
        limit=3,
        threshold=0.5
    )
    
    if "error" not in search_results and search_results:
        print(f"{Colors.GREEN}✅ Found {len(search_results)} relevant memories{Colors.END}")
        for i, result in enumerate(search_results[:2], 1):
            memory = result.get('memory', {})
            similarity = result.get('similarity', 0)
            topic = memory.get('metadata', {}).get('topic', 'Unknown')
            print(f"   {i}. {topic} (similarity: {similarity:.2%})")
    else:
        print(f"{Colors.RED}❌ Search failed or no results{Colors.END}")
    
    time.sleep(1)

def demo_advanced_integration(api: MemoryVaultAPI):
    """Demonstrate advanced integration patterns"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🎯 LEVEL 4B: Advanced Integration Patterns{Colors.END}")
    print("─" * 50)
    
    # Smart Knowledge Base Example
    print(f"{Colors.YELLOW}Building a Smart Knowledge Base...{Colors.END}")
    
    knowledge_items = [
        {
            "content": "REST API design principle: Use HTTP methods semantically - GET for retrieval, POST for creation, PUT for full updates, PATCH for partial updates, DELETE for removal. Status codes should reflect the operation result.",
            "metadata": {"category": "api_design", "principle": "rest", "level": "basic"}
        },
        {
            "content": "Microservices communication patterns: Synchronous (HTTP/gRPC) for real-time needs, Asynchronous (message queues) for decoupled operations, Event-driven architecture for loosely coupled services.",
            "metadata": {"category": "architecture", "pattern": "microservices", "level": "advanced"}
        }
    ]
    
    print(f"  📚 Adding knowledge items to the vault...")
    for i, item in enumerate(knowledge_items, 1):
        result = api.store_memory(item["content"], item["metadata"])
        if "error" not in result:
            print(f"    {i}. {Colors.GREEN}✓{Colors.END} Added {item['metadata']['category']} knowledge")
        else:
            print(f"    {i}. {Colors.RED}✗{Colors.END} Failed to add knowledge")
    
    time.sleep(1)
    
    # Intelligent Q&A Example
    print(f"\n{Colors.YELLOW}Intelligent Q&A System Example...{Colors.END}")
    
    questions = [
        "How should I design REST APIs?",
        "What are microservices communication patterns?",
        "Best practices for API status codes"
    ]
    
    for question in questions:
        print(f"\n  ❓ Question: \"{question}\"")
        results = api.search_memories(question, limit=2, threshold=0.4)
        
        if "error" not in results and results:
            best_match = results[0]
            similarity = best_match.get('similarity', 0)
            content = best_match.get('memory', {}).get('content', '')
            
            if similarity > 0.7:
                print(f"  {Colors.GREEN}🎯 High confidence answer found (similarity: {similarity:.2%}){Colors.END}")
                preview = content[:150] + "..." if len(content) > 150 else content
                print(f"     {preview}")
            else:
                print(f"  {Colors.YELLOW}📝 Related information found (similarity: {similarity:.2%}){Colors.END}")
        else:
            print(f"  {Colors.RED}❌ No relevant information found{Colors.END}")

def show_code_examples():
    """Show production-ready code examples"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🎯 LEVEL 4C: Production Code Examples{Colors.END}")
    print("─" * 50)
    
    # Python Client Example
    python_example = '''
import requests
from typing import Dict, List, Optional

class MemoryVaultClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def store(self, content: str, metadata: Optional[Dict] = None) -> Dict:
        """Store a memory with error handling"""
        try:
            response = self.session.post(
                f"{self.base_url}/memories/",
                json={"content": content, "metadata": metadata or {}},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Semantic search with fallback"""
        try:
            response = self.session.post(
                f"{self.base_url}/search/",
                json={"query": query, "limit": limit},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return []

# Usage
vault = MemoryVaultClient()
result = vault.store("Important meeting notes...", {"project": "alpha"})
memories = vault.search("project alpha meeting notes")
'''
    
    print_code_example("🐍 Python Integration Example", python_example.strip())
    
    # JavaScript Example
    js_example = '''
class MemoryVault {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async store(content, metadata = {}) {
    try {
      const response = await fetch(`${this.baseUrl}/memories/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, metadata })
      });
      return await response.json();
    } catch (error) {
      return { error: error.message };
    }
  }

  async search(query, limit = 10) {
    try {
      const response = await fetch(`${this.baseUrl}/search/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, limit })
      });
      return await response.json();
    } catch (error) {
      return [];
    }
  }
}

// Usage
const vault = new MemoryVault();
await vault.store("User feedback analysis", { source: "survey" });
const results = await vault.search("user feedback insights");
'''
    
    print_code_example("🌐 JavaScript/Node.js Example", js_example.strip(), "javascript")
    
    # Configuration Example
    config_example = '''
# .env file for production deployment
OPENAI_API_KEY=your_production_key_here
POSTGRES_HOST=your-postgres-host.com
POSTGRES_DB=memorylink_production
POSTGRES_USER=memorylink_user
POSTGRES_PASSWORD=secure_random_password

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Security
CORS_ORIGINS=["https://yourdomain.com"]
RATE_LIMIT=100  # requests per minute
'''
    
    print_code_example("⚙️ Production Configuration", config_example.strip(), "bash")

def show_integration_tips():
    """Show integration tips and best practices"""
    print(f"\n{Colors.BOLD}{Colors.PURPLE}💡 Integration Tips & Best Practices{Colors.END}")
    print("─" * 50)
    
    tips = [
        ("🔒 Security", "Always use HTTPS in production, validate inputs, implement rate limiting"),
        ("⚡ Performance", "Batch operations when possible, use connection pooling, cache frequent searches"),
        ("🛡️ Error Handling", "Implement retries with exponential backoff, graceful degradation for failures"),
        ("📊 Monitoring", "Log API calls, monitor response times, set up alerts for failures"),
        ("🔄 Scalability", "Use load balancers, implement database sharding for large datasets"),
        ("🧪 Testing", "Unit tests for API clients, integration tests with test databases")
    ]
    
    for category, tip in tips:
        print(f"{Colors.CYAN}{category}:{Colors.END} {tip}")

def main():
    """Main demo function"""
    print_banner()
    
    # Initialize API client
    api = MemoryVaultAPI()
    
    # Check connection
    print(f"{Colors.YELLOW}🔍 Connecting to Memory Vault API...{Colors.END}")
    if not api.health_check():
        print(f"{Colors.RED}❌ Cannot connect to Memory Vault server!{Colors.END}")
        print(f"{Colors.YELLOW}💡 Make sure the server is running with 'make start'{Colors.END}")
        sys.exit(1)
    
    print(f"{Colors.GREEN}✅ Connected successfully!{Colors.END}")
    
    print(f"\n{Colors.BOLD}{Colors.PURPLE}🎮 LEVEL 4: API Integration Mastery{Colors.END}")
    print(f"{Colors.CYAN}Learn to build production-ready applications with MemoryLink{Colors.END}")
    
    # Run demonstrations
    demo_basic_operations(api)
    demo_advanced_integration(api)
    show_code_examples()
    show_integration_tips()
    
    # Completion message
    print(f"\n{Colors.PURPLE}{'═' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}🎉 API Integration Demo Complete!{Colors.END}")
    print(f"{Colors.PURPLE}{'═' * 60}{Colors.END}")
    
    print(f"\n{Colors.YELLOW}🎯 Next Steps:{Colors.END}")
    print(f"{Colors.GREEN}  • Check out examples/ directory for more integration samples")
    print(f"  • Read docs/api.md for complete API reference")
    print(f"  • Explore docs/development.md for advanced topics")
    print(f"  • Build something amazing with MemoryLink!{Colors.END}")
    
    print(f"\n{Colors.PURPLE}🏆 Achievement Unlocked: Integration Master - API mastery complete!{Colors.END}")
    print(f"{Colors.CYAN}You are now ready to build production applications with MemoryLink!{Colors.END}")

if __name__ == "__main__":
    main()
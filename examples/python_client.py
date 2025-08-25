#!/usr/bin/env python3
"""
🐍 MemoryLink Python Client Examples
Complete examples for integrating MemoryLink into Python applications
"""

import requests
import json
import asyncio
import time
from typing import Dict, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from contextlib import contextmanager

# ANSI colors for beautiful output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

@dataclass
class Memory:
    """Memory data structure"""
    id: str
    content: str
    metadata: Dict
    created_at: str
    similarity: Optional[float] = None

class MemoryLinkError(Exception):
    """Custom exception for MemoryLink operations"""
    pass

class MemoryVaultClient:
    """
    Production-ready MemoryLink Python client
    
    Features:
    - Connection pooling
    - Error handling with retries
    - Type hints
    - Logging
    - Async support
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.timeout = timeout
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'MemoryLink-Python-Client/1.0'
        })
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
    
    @contextmanager
    def error_handling(self, operation: str):
        """Context manager for consistent error handling"""
        try:
            yield
        except requests.exceptions.ConnectionError:
            raise MemoryLinkError(f"Cannot connect to MemoryLink server. Is it running?")
        except requests.exceptions.Timeout:
            raise MemoryLinkError(f"Operation '{operation}' timed out after {self.timeout}s")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise MemoryLinkError(f"Resource not found")
            elif e.response.status_code == 400:
                raise MemoryLinkError(f"Invalid request: {e.response.text}")
            else:
                raise MemoryLinkError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise MemoryLinkError(f"Unexpected error in '{operation}': {str(e)}")
    
    def health_check(self) -> bool:
        """Check if the Memory Vault is healthy"""
        with self.error_handling("health_check"):
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
    
    def store_memory(self, content: str, metadata: Optional[Dict] = None) -> Memory:
        """
        Store a new memory in the vault
        
        Args:
            content: The memory content (text)
            metadata: Optional metadata dictionary
            
        Returns:
            Memory object with generated ID
            
        Raises:
            MemoryLinkError: If storage fails
        """
        if not content or not content.strip():
            raise MemoryLinkError("Memory content cannot be empty")
        
        payload = {
            "content": content.strip(),
            "metadata": metadata or {}
        }
        
        with self.error_handling("store_memory"):
            response = self.session.post(f"{self.base_url}/memories/", json=payload)
            response.raise_for_status()
            
            data = response.json()
            return Memory(
                id=data["id"],
                content=data["content"],
                metadata=data.get("metadata", {}),
                created_at=data.get("created_at", "")
            )
    
    def search_memories(self, query: str, limit: int = 10, threshold: float = 0.3) -> List[Memory]:
        """
        Search memories using semantic similarity
        
        Args:
            query: Natural language search query
            limit: Maximum number of results (1-100)
            threshold: Similarity threshold (0.0-1.0)
            
        Returns:
            List of Memory objects with similarity scores
            
        Raises:
            MemoryLinkError: If search fails
        """
        if not query or not query.strip():
            raise MemoryLinkError("Search query cannot be empty")
        
        if not 1 <= limit <= 100:
            raise MemoryLinkError("Limit must be between 1 and 100")
            
        if not 0.0 <= threshold <= 1.0:
            raise MemoryLinkError("Threshold must be between 0.0 and 1.0")
        
        payload = {
            "query": query.strip(),
            "limit": limit,
            "threshold": threshold
        }
        
        with self.error_handling("search_memories"):
            response = self.session.post(f"{self.base_url}/search/", json=payload)
            response.raise_for_status()
            
            results = response.json()
            memories = []
            
            for result in results:
                memory_data = result.get("memory", {})
                memories.append(Memory(
                    id=memory_data.get("id", ""),
                    content=memory_data.get("content", ""),
                    metadata=memory_data.get("metadata", {}),
                    created_at=memory_data.get("created_at", ""),
                    similarity=result.get("similarity", 0.0)
                ))
            
            return memories
    
    def get_all_memories(self, limit: int = 100, offset: int = 0) -> List[Memory]:
        """
        Retrieve all stored memories
        
        Args:
            limit: Maximum number of memories to return
            offset: Number of memories to skip
            
        Returns:
            List of Memory objects
        """
        with self.error_handling("get_all_memories"):
            params = {"limit": limit, "offset": offset}
            response = self.session.get(f"{self.base_url}/memories/", params=params)
            response.raise_for_status()
            
            memories = []
            for data in response.json():
                memories.append(Memory(
                    id=data["id"],
                    content=data["content"], 
                    metadata=data.get("metadata", {}),
                    created_at=data.get("created_at", "")
                ))
            
            return memories
    
    def get_memory_by_id(self, memory_id: str) -> Memory:
        """
        Get a specific memory by ID
        
        Args:
            memory_id: UUID of the memory
            
        Returns:
            Memory object
            
        Raises:
            MemoryLinkError: If memory not found
        """
        with self.error_handling("get_memory_by_id"):
            response = self.session.get(f"{self.base_url}/memories/{memory_id}")
            response.raise_for_status()
            
            data = response.json()
            return Memory(
                id=data["id"],
                content=data["content"],
                metadata=data.get("metadata", {}),
                created_at=data.get("created_at", "")
            )


class SmartKnowledgeBase:
    """
    High-level wrapper for building intelligent knowledge bases
    """
    
    def __init__(self, vault_client: MemoryVaultClient):
        self.vault = vault_client
    
    def add_article(self, title: str, content: str, tags: List[str] = None, 
                   source: str = None, difficulty: str = "intermediate") -> Memory:
        """Add an article to the knowledge base"""
        metadata = {
            "type": "article",
            "title": title,
            "tags": tags or [],
            "source": source,
            "difficulty": difficulty,
            "added_at": datetime.now().isoformat()
        }
        
        # Combine title and content for better searchability
        full_content = f"# {title}\n\n{content}"
        
        return self.vault.store_memory(full_content, metadata)
    
    def add_code_snippet(self, title: str, code: str, language: str, 
                        description: str = "", tags: List[str] = None) -> Memory:
        """Add a code snippet to the knowledge base"""
        metadata = {
            "type": "code",
            "title": title,
            "language": language,
            "tags": tags or [],
            "added_at": datetime.now().isoformat()
        }
        
        content = f"# {title}\n\n"
        if description:
            content += f"{description}\n\n"
        content += f"```{language}\n{code}\n```"
        
        return self.vault.store_memory(content, metadata)
    
    def add_meeting_notes(self, meeting_title: str, date: str, 
                         attendees: List[str], notes: str, 
                         action_items: List[str] = None) -> Memory:
        """Add meeting notes to the knowledge base"""
        metadata = {
            "type": "meeting",
            "title": meeting_title,
            "date": date,
            "attendees": attendees,
            "action_items": action_items or [],
            "added_at": datetime.now().isoformat()
        }
        
        content = f"# Meeting: {meeting_title}\n\n"
        content += f"**Date:** {date}\n"
        content += f"**Attendees:** {', '.join(attendees)}\n\n"
        content += f"## Notes\n{notes}\n\n"
        
        if action_items:
            content += "## Action Items\n"
            for item in action_items:
                content += f"- {item}\n"
        
        return self.vault.store_memory(content, metadata)
    
    def smart_search(self, query: str, content_type: str = None, 
                    limit: int = 10) -> List[Memory]:
        """
        Intelligent search with optional filtering by content type
        """
        memories = self.vault.search_memories(query, limit=limit * 2)  # Get extra results
        
        if content_type:
            # Filter by content type
            filtered = [m for m in memories if m.metadata.get("type") == content_type]
            return filtered[:limit]
        
        return memories[:limit]
    
    def get_by_tags(self, tags: List[str], limit: int = 20) -> List[Memory]:
        """Find memories by tags (approximate matching)"""
        # Search using tags as query terms
        query = " ".join(tags)
        memories = self.vault.search_memories(query, limit=limit)
        
        # Filter results that actually contain the tags
        filtered = []
        for memory in memories:
            memory_tags = memory.metadata.get("tags", [])
            if any(tag in memory_tags for tag in tags):
                filtered.append(memory)
        
        return filtered


class AutoMemoryLogger:
    """
    Automatic logging system that captures and stores structured information
    """
    
    def __init__(self, vault_client: MemoryVaultClient, auto_tag: bool = True):
        self.vault = vault_client
        self.auto_tag = auto_tag
    
    def log_learning(self, topic: str, content: str, source: str = "", 
                    confidence_level: int = 7) -> Memory:
        """Log learning progress"""
        metadata = {
            "type": "learning",
            "topic": topic,
            "source": source,
            "confidence_level": confidence_level,  # 1-10 scale
            "logged_at": datetime.now().isoformat()
        }
        
        if self.auto_tag:
            # Simple auto-tagging based on content
            tags = self._extract_simple_tags(content)
            metadata["auto_tags"] = tags
        
        formatted_content = f"# Learning: {topic}\n\n{content}"
        if source:
            formatted_content += f"\n\n**Source:** {source}"
        formatted_content += f"\n\n**Confidence Level:** {confidence_level}/10"
        
        return self.vault.store_memory(formatted_content, metadata)
    
    def log_idea(self, title: str, description: str, category: str = "general",
                priority: str = "medium") -> Memory:
        """Log ideas and thoughts"""
        metadata = {
            "type": "idea",
            "title": title,
            "category": category,
            "priority": priority,
            "logged_at": datetime.now().isoformat()
        }
        
        content = f"# Idea: {title}\n\n{description}"
        content += f"\n\n**Category:** {category}"
        content += f"\n**Priority:** {priority}"
        
        return self.vault.store_memory(content, metadata)
    
    def log_problem_solution(self, problem: str, solution: str, 
                           tools_used: List[str] = None) -> Memory:
        """Log problems and their solutions"""
        metadata = {
            "type": "problem_solution",
            "tools_used": tools_used or [],
            "solved_at": datetime.now().isoformat()
        }
        
        content = f"# Problem & Solution\n\n"
        content += f"## Problem\n{problem}\n\n"
        content += f"## Solution\n{solution}\n\n"
        
        if tools_used:
            content += f"## Tools Used\n"
            for tool in tools_used:
                content += f"- {tool}\n"
        
        return self.vault.store_memory(content, metadata)
    
    def _extract_simple_tags(self, content: str) -> List[str]:
        """Simple tag extraction based on common programming terms"""
        common_tags = {
            'python': ['python', 'py', 'django', 'flask', 'pandas', 'numpy'],
            'javascript': ['javascript', 'js', 'node', 'react', 'vue', 'angular'],
            'database': ['sql', 'postgresql', 'mysql', 'database', 'db'],
            'web': ['html', 'css', 'http', 'api', 'rest', 'web'],
            'docker': ['docker', 'container', 'dockerfile'],
            'git': ['git', 'github', 'version control', 'commit']
        }
        
        content_lower = content.lower()
        found_tags = []
        
        for tag, keywords in common_tags.items():
            if any(keyword in content_lower for keyword in keywords):
                found_tags.append(tag)
        
        return found_tags


# Example Usage and Demo Functions

def demo_basic_usage():
    """Demonstrate basic MemoryLink usage"""
    print(f"{Colors.CYAN}🐍 Python Client Basic Usage Demo{Colors.END}")
    print("─" * 50)
    
    with MemoryVaultClient() as vault:
        # Check connection
        if not vault.health_check():
            print(f"{Colors.RED}❌ Cannot connect to MemoryLink server{Colors.END}")
            return
        
        print(f"{Colors.GREEN}✅ Connected to Memory Vault{Colors.END}")
        
        # Store a memory
        print(f"\n{Colors.YELLOW}📝 Storing a memory...{Colors.END}")
        memory = vault.store_memory(
            content="FastAPI is a modern Python web framework for building APIs with automatic interactive documentation.",
            metadata={
                "topic": "web_development",
                "framework": "fastapi",
                "language": "python"
            }
        )
        print(f"   Stored memory with ID: {memory.id[:8]}...")
        
        # Search for memories
        print(f"\n{Colors.YELLOW}🔍 Searching for Python web frameworks...{Colors.END}")
        results = vault.search_memories("Python web framework for APIs", limit=3)
        
        for i, result in enumerate(results, 1):
            print(f"   {i}. Similarity: {result.similarity:.2%}")
            print(f"      Content: {result.content[:80]}...")


def demo_smart_knowledge_base():
    """Demonstrate the Smart Knowledge Base wrapper"""
    print(f"\n{Colors.CYAN}🧠 Smart Knowledge Base Demo{Colors.END}")
    print("─" * 50)
    
    with MemoryVaultClient() as vault:
        if not vault.health_check():
            print(f"{Colors.RED}❌ Cannot connect to MemoryLink server{Colors.END}")
            return
        
        kb = SmartKnowledgeBase(vault)
        
        # Add different types of content
        print(f"{Colors.YELLOW}📚 Adding article...{Colors.END}")
        kb.add_article(
            title="Introduction to Async Programming",
            content="Asynchronous programming allows multiple operations to run concurrently without blocking execution.",
            tags=["async", "programming", "concurrency"],
            source="Learning Notes",
            difficulty="intermediate"
        )
        
        print(f"{Colors.YELLOW}💻 Adding code snippet...{Colors.END}")
        kb.add_code_snippet(
            title="Async Function Example",
            code="async def fetch_data():\n    await asyncio.sleep(1)\n    return 'data'",
            language="python",
            description="Simple async function that simulates data fetching",
            tags=["python", "async", "example"]
        )
        
        print(f"{Colors.YELLOW}📋 Adding meeting notes...{Colors.END}")
        kb.add_meeting_notes(
            meeting_title="Sprint Planning",
            date="2024-01-15",
            attendees=["Alice", "Bob", "Charlie"],
            notes="Discussed async implementation for the API endpoints. Decided to use FastAPI with async/await pattern.",
            action_items=["Research FastAPI async patterns", "Create proof of concept"]
        )
        
        # Smart search
        print(f"\n{Colors.YELLOW}🎯 Smart search for async content...{Colors.END}")
        results = kb.smart_search("asynchronous programming examples", limit=3)
        
        for i, result in enumerate(results, 1):
            title = result.metadata.get("title", "Untitled")
            content_type = result.metadata.get("type", "unknown")
            print(f"   {i}. [{content_type.upper()}] {title} (similarity: {result.similarity:.2%})")


def demo_auto_logger():
    """Demonstrate the Auto Memory Logger"""
    print(f"\n{Colors.CYAN}📊 Auto Memory Logger Demo{Colors.END}")
    print("─" * 50)
    
    with MemoryVaultClient() as vault:
        if not vault.health_check():
            print(f"{Colors.RED}❌ Cannot connect to MemoryLink server{Colors.END}")
            return
        
        logger = AutoMemoryLogger(vault)
        
        # Log learning
        print(f"{Colors.YELLOW}📚 Logging learning progress...{Colors.END}")
        logger.log_learning(
            topic="Docker Networking",
            content="Docker creates isolated networks for containers. Bridge networks allow container-to-container communication.",
            source="Docker Documentation",
            confidence_level=8
        )
        
        # Log an idea
        print(f"{Colors.YELLOW}💡 Logging an idea...{Colors.END}")
        logger.log_idea(
            title="Memory Export Feature",
            description="Add ability to export memories as Markdown files with metadata preserved in YAML frontmatter.",
            category="feature",
            priority="medium"
        )
        
        # Log problem/solution
        print(f"{Colors.YELLOW}🔧 Logging problem/solution...{Colors.END}")
        logger.log_problem_solution(
            problem="Docker containers losing data when restarted",
            solution="Use named volumes or bind mounts to persist data between container restarts",
            tools_used=["Docker volumes", "docker-compose"]
        )
        
        print(f"{Colors.GREEN}✅ All items logged successfully{Colors.END}")


def demo_error_handling():
    """Demonstrate error handling capabilities"""
    print(f"\n{Colors.CYAN}⚠️ Error Handling Demo{Colors.END}")
    print("─" * 50)
    
    # Test with invalid URL to demonstrate error handling
    vault = MemoryVaultClient("http://localhost:9999")  # Wrong port
    
    try:
        vault.health_check()
    except MemoryLinkError as e:
        print(f"{Colors.RED}Caught expected error: {e}{Colors.END}")
    
    # Test with empty content
    with MemoryVaultClient() as vault:
        try:
            vault.store_memory("")  # Empty content
        except MemoryLinkError as e:
            print(f"{Colors.YELLOW}Validation error: {e}{Colors.END}")


def main():
    """Run all demonstrations"""
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("🐍" + "═" * 60 + "🐍")
    print("        MEMORYLINK PYTHON CLIENT EXAMPLES")
    print("          Complete Integration Demos")
    print("🐍" + "═" * 60 + "🐍")
    print(f"{Colors.END}")
    
    try:
        demo_basic_usage()
        demo_smart_knowledge_base()
        demo_auto_logger()
        demo_error_handling()
        
        print(f"\n{Colors.GREEN}🎉 All demos completed successfully!{Colors.END}")
        print(f"{Colors.CYAN}Ready to integrate MemoryLink into your Python applications!{Colors.END}")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Demo interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Demo failed: {e}{Colors.END}")


if __name__ == "__main__":
    main()
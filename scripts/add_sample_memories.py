#!/usr/bin/env python3
"""
🌟 Memory Vault Sample Data Generator
Adds sample memories to help new Memory Keepers get started
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any

# ANSI color codes for beautiful terminal output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_banner():
    """Display the sample data generator banner"""
    print(f"{Colors.CYAN}")
    print("🌟" + "═" * 50 + "🌟")
    print("     MEMORY VAULT SAMPLE DATA GENERATOR")
    print("         Populating your vault with")
    print("        knowledge from across domains")
    print("🌟" + "═" * 50 + "🌟")
    print(f"{Colors.END}")

def animated_print(text: str, delay: float = 0.05):
    """Print text with typewriter animation"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def check_server_health() -> bool:
    """Check if the Memory Vault server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def store_memory(content: str, metadata: Dict[str, Any]) -> Dict:
    """Store a memory in the vault"""
    try:
        response = requests.post(
            "http://localhost:8000/memories/",
            json={"content": content, "metadata": metadata},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_sample_memories() -> List[Dict[str, Any]]:
    """Get a diverse collection of sample memories"""
    return [
        {
            "content": """
Python decorators are a powerful feature that allows you to modify or extend the behavior of functions or classes without permanently modifying their code. They work by wrapping another function and can execute code before and after the wrapped function runs.

Example:
```python
def my_decorator(func):
    def wrapper():
        print("Before function")
        func()
        print("After function")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")
```
            """,
            "metadata": {
                "topic": "programming",
                "language": "python",
                "difficulty": "intermediate",
                "source": "learning_notes",
                "tags": ["decorators", "functions", "python", "programming"]
            }
        },
        {
            "content": """
The Pomodoro Technique is a time management method developed by Francesco Cirillo in the late 1980s. It uses a timer to break work into intervals, traditionally 25 minutes in length, separated by short breaks. Each interval is known as a pomodoro, from the Italian word for 'tomato', after the tomato-shaped kitchen timer that Cirillo used as a university student.

Steps:
1. Choose a task to work on
2. Set timer for 25 minutes
3. Work until timer rings
4. Take a short 5-minute break
5. After 4 pomodoros, take a longer break (15-30 minutes)
            """,
            "metadata": {
                "topic": "productivity",
                "technique": "pomodoro",
                "difficulty": "beginner",
                "source": "productivity_blog",
                "tags": ["time_management", "productivity", "focus", "technique"]
            }
        },
        {
            "content": """
React Hooks fundamentally changed how we write React components by allowing functional components to have state and lifecycle methods. The useState hook lets you add state to functional components, while useEffect handles side effects and replaces lifecycle methods like componentDidMount and componentWillUnmount.

Key benefits:
- Cleaner, more readable code
- Better logic reuse between components  
- Easier testing
- Smaller bundle sizes
- More predictable behavior

Common hooks: useState, useEffect, useContext, useReducer, useMemo, useCallback
            """,
            "metadata": {
                "topic": "web_development",
                "framework": "react",
                "concept": "hooks",
                "difficulty": "intermediate",
                "source": "react_documentation",
                "tags": ["react", "hooks", "frontend", "javascript", "state_management"]
            }
        },
        {
            "content": """
Machine Learning can be categorized into three main types:

1. **Supervised Learning**: Algorithm learns from labeled training data to make predictions
   - Examples: Classification, Regression
   - Algorithms: Linear Regression, Random Forest, Neural Networks

2. **Unsupervised Learning**: Finds patterns in data without labeled examples
   - Examples: Clustering, Dimensionality Reduction
   - Algorithms: K-Means, PCA, t-SNE

3. **Reinforcement Learning**: Agent learns through trial and error by receiving rewards
   - Examples: Game playing, Robotics, Autonomous vehicles
   - Algorithms: Q-Learning, Policy Gradient, Actor-Critic
            """,
            "metadata": {
                "topic": "machine_learning",
                "category": "overview",
                "difficulty": "beginner",
                "source": "ml_course",
                "tags": ["machine_learning", "ai", "supervised", "unsupervised", "reinforcement"]
            }
        },
        {
            "content": """
Database indexing is a data structure technique used to quickly locate and access data in a database. Indexes create shortcuts to data, similar to an index in a book.

Types of indexes:
- **B-Tree Index**: Most common, good for equality and range queries
- **Hash Index**: Fastest for equality lookups, not for ranges
- **Bitmap Index**: Efficient for low-cardinality data
- **Partial Index**: Only indexes rows meeting certain conditions

Trade-offs:
✅ Faster SELECT queries
❌ Slower INSERT/UPDATE/DELETE operations
❌ Additional storage space required

Rule of thumb: Index frequently queried columns, avoid over-indexing
            """,
            "metadata": {
                "topic": "database",
                "concept": "indexing",
                "difficulty": "intermediate",
                "source": "database_book",
                "tags": ["database", "indexing", "performance", "sql", "optimization"]
            }
        },
        {
            "content": """
The SOLID principles are five design principles in object-oriented programming that make software designs more understandable, flexible, and maintainable:

**S** - Single Responsibility Principle: A class should have only one reason to change
**O** - Open/Closed Principle: Open for extension, closed for modification  
**L** - Liskov Substitution Principle: Objects should be replaceable with instances of subtypes
**I** - Interface Segregation Principle: Many client-specific interfaces are better than one general-purpose interface
**D** - Dependency Inversion Principle: Depend on abstractions, not concretions

These principles help create code that is easier to maintain, test, and extend over time.
            """,
            "metadata": {
                "topic": "software_engineering",
                "concept": "solid_principles",
                "difficulty": "intermediate",
                "source": "design_patterns_book",
                "tags": ["solid", "oop", "design_principles", "software_architecture", "clean_code"]
            }
        },
        {
            "content": """
Docker containerization allows you to package applications with their dependencies into lightweight, portable containers. Key concepts:

**Image**: Read-only template used to create containers
**Container**: Running instance of an image
**Dockerfile**: Text file with instructions to build an image
**Registry**: Storage for Docker images (like Docker Hub)

Basic commands:
- `docker build -t myapp .` - Build image from Dockerfile
- `docker run myapp` - Run container from image
- `docker ps` - List running containers
- `docker stop <container>` - Stop a container
- `docker-compose up` - Start multi-container applications

Benefits: Consistency across environments, easy scaling, isolation
            """,
            "metadata": {
                "topic": "devops",
                "tool": "docker",
                "concept": "containerization",
                "difficulty": "beginner",
                "source": "docker_tutorial",
                "tags": ["docker", "containerization", "devops", "deployment", "microservices"]
            }
        },
        {
            "content": """
Git branching strategies help teams collaborate effectively:

**Git Flow**:
- main: Production-ready code
- develop: Integration branch for features
- feature/*: Individual feature branches
- release/*: Release preparation
- hotfix/*: Critical production fixes

**GitHub Flow** (Simpler):
- main: Always deployable
- feature branches: Short-lived, merged via PR

**Best Practices**:
- Use descriptive branch names
- Keep branches focused and small
- Delete merged branches
- Use meaningful commit messages
- Review code before merging

Choose strategy based on team size and deployment frequency.
            """,
            "metadata": {
                "topic": "version_control",
                "tool": "git",
                "concept": "branching_strategy",
                "difficulty": "intermediate",
                "source": "git_best_practices",
                "tags": ["git", "branching", "collaboration", "workflow", "version_control"]
            }
        }
    ]

def display_progress_bar(current: int, total: int, width: int = 50):
    """Display a colorful progress bar"""
    percent = current / total
    filled = int(width * percent)
    bar = '█' * filled + '░' * (width - filled)
    print(f"\r{Colors.CYAN}Progress: [{bar}] {percent:.1%} ({current}/{total}){Colors.END}", end='')

def main():
    """Main function to add sample memories"""
    print_banner()
    
    # Check server health
    print(f"{Colors.YELLOW}🔍 Checking Memory Vault server status...{Colors.END}")
    if not check_server_health():
        print(f"{Colors.RED}❌ Error: Memory Vault server not running!{Colors.END}")
        print(f"{Colors.YELLOW}💡 Run 'make start' first to awaken the vault{Colors.END}")
        sys.exit(1)
    
    print(f"{Colors.GREEN}✅ Memory Vault server is active!{Colors.END}\n")
    
    # Get sample memories
    memories = get_sample_memories()
    
    print(f"{Colors.PURPLE}{Colors.BOLD}📚 Adding {len(memories)} sample memories to your vault...{Colors.END}")
    print(f"{Colors.CYAN}This will give you diverse content to practice semantic search!{Colors.END}\n")
    
    # Store each memory with progress indication
    successful = 0
    failed = 0
    
    for i, memory_data in enumerate(memories, 1):
        display_progress_bar(i-1, len(memories))
        
        result = store_memory(memory_data["content"], memory_data["metadata"])
        
        if "error" not in result:
            successful += 1
            print(f"\n{Colors.GREEN}✅ Memory {i}: {memory_data['metadata']['topic']} - {memory_data['metadata'].get('concept', 'general')}{Colors.END}")
        else:
            failed += 1
            print(f"\n{Colors.RED}❌ Failed to store memory {i}: {result['error']}{Colors.END}")
        
        time.sleep(0.5)  # Small delay for dramatic effect
    
    # Final progress bar
    display_progress_bar(len(memories), len(memories))
    print("\n")
    
    # Summary
    print(f"{Colors.PURPLE}{'═' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}🎉 Sample Memory Installation Complete!{Colors.END}")
    print(f"{Colors.PURPLE}{'═' * 60}{Colors.END}")
    
    print(f"{Colors.CYAN}📊 Results Summary:{Colors.END}")
    print(f"{Colors.GREEN}  ✅ Successfully added: {successful} memories{Colors.END}")
    if failed > 0:
        print(f"{Colors.RED}  ❌ Failed to add: {failed} memories{Colors.END}")
    
    print(f"\n{Colors.YELLOW}🎯 What you can do now:{Colors.END}")
    print(f"{Colors.GREEN}  • Run 'make search' to try semantic search{Colors.END}")
    print(f"{Colors.GREEN}  • Search for topics like 'Python functions', 'productivity tips', or 'Docker basics'{Colors.END}")
    print(f"{Colors.GREEN}  • Use the API to integrate with your applications{Colors.END}")
    
    print(f"\n{Colors.PURPLE}🏆 Achievement Unlocked: Memory Scribe - You've added your first memories!{Colors.END}")
    
    # Show some example searches
    print(f"\n{Colors.CYAN}💡 Try these sample searches:{Colors.END}")
    example_searches = [
        "How do Python decorators work?",
        "Time management techniques for developers",
        "React state management patterns",
        "Database performance optimization",
        "Docker containerization basics"
    ]
    
    for search in example_searches:
        print(f"{Colors.BLUE}  🔍 \"{search}\"{Colors.END}")

if __name__ == "__main__":
    main()
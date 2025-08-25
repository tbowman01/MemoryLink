#!/usr/bin/env python3
"""
🔍 Memory Vault Interactive Search
A beautiful, interactive command-line search interface for your memories
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# ANSI color codes for beautiful terminal output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class MemoryVaultSearch:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.search_count = 0
    
    def print_banner(self):
        """Display the interactive search banner"""
        print(f"{Colors.PURPLE}")
        print("🔮" + "═" * 60 + "🔮")
        print("        MEMORY VAULT INTERACTIVE SEARCH")
        print("           Discover memories by meaning")
        print("          Powered by AI semantic search")
        print("🔮" + "═" * 60 + "🔮")
        print(f"{Colors.END}")
    
    def check_server_health(self) -> bool:
        """Check if the Memory Vault server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def search_memories(self, query: str, limit: int = 10, threshold: float = 0.3) -> List[Dict]:
        """Search memories using semantic similarity"""
        try:
            response = requests.post(
                f"{self.base_url}/search/",
                json={
                    "query": query,
                    "limit": limit,
                    "threshold": threshold
                },
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def display_search_results(self, results: List[Dict], query: str):
        """Display search results in a beautiful format"""
        if not results or "error" in results:
            print(f"{Colors.RED}❌ Search failed or no results found{Colors.END}")
            if "error" in results:
                print(f"{Colors.YELLOW}Error: {results['error']}{Colors.END}")
            return
        
        print(f"\n{Colors.CYAN}🎯 Search Results for: {Colors.BOLD}\"{query}\"{Colors.END}")
        print(f"{Colors.CYAN}Found {len(results)} relevant memories:{Colors.END}")
        print("─" * 80)
        
        for i, result in enumerate(results, 1):
            # Extract data
            memory = result.get('memory', {})
            content = memory.get('content', 'No content')
            metadata = memory.get('metadata', {})
            similarity = result.get('similarity', 0)
            
            # Header with similarity score
            similarity_color = Colors.GREEN if similarity > 0.8 else Colors.YELLOW if similarity > 0.6 else Colors.BLUE
            print(f"\n{Colors.BOLD}{Colors.PURPLE}📄 Result #{i}{Colors.END} "
                  f"{similarity_color}(Similarity: {similarity:.2%}){Colors.END}")
            
            # Metadata tags
            if metadata:
                tags = []
                for key, value in metadata.items():
                    if key == 'tags' and isinstance(value, list):
                        tags.extend([f"#{tag}" for tag in value])
                    else:
                        tags.append(f"{key}:{value}")
                
                if tags:
                    tag_str = " ".join(tags[:6])  # Limit to first 6 tags
                    print(f"{Colors.CYAN}🏷️  {tag_str}{Colors.END}")
            
            # Content preview (first 300 characters)
            content_preview = content.strip()
            if len(content_preview) > 300:
                content_preview = content_preview[:300] + "..."
            
            # Format content with proper indentation
            lines = content_preview.split('\n')
            for line in lines[:8]:  # Limit to 8 lines
                if line.strip():
                    print(f"   {line}")
            
            if len(lines) > 8:
                print(f"{Colors.YELLOW}   ... (content truncated){Colors.END}")
            
            print("─" * 60)
        
        print(f"\n{Colors.GREEN}✨ Search completed! Found {len(results)} memories{Colors.END}")
    
    def get_search_suggestions(self) -> List[str]:
        """Get sample search suggestions"""
        return [
            "Python programming concepts",
            "productivity and time management",
            "web development with React",
            "database optimization techniques",
            "machine learning algorithms",
            "software design patterns",
            "Docker containerization",
            "version control with Git",
            "API development best practices",
            "debugging and testing strategies"
        ]
    
    def display_search_tips(self):
        """Display helpful search tips"""
        print(f"\n{Colors.YELLOW}💡 Search Tips:{Colors.END}")
        print(f"{Colors.CYAN}  • Use natural language: \"How to optimize database queries\"")
        print(f"  • Try concept-based searches: \"state management patterns\"")
        print(f"  • Search by topic: \"machine learning classification\"")
        print(f"  • Ask questions: \"What are SOLID principles?\"")
        print(f"  • Use keywords: \"Docker containers deployment\"{Colors.END}")
        
        print(f"\n{Colors.PURPLE}🎯 Sample searches to try:{Colors.END}")
        suggestions = self.get_search_suggestions()
        for i, suggestion in enumerate(suggestions[:5], 1):
            print(f"{Colors.BLUE}  {i}. {suggestion}{Colors.END}")
    
    def interactive_search_loop(self):
        """Main interactive search loop"""
        print(f"\n{Colors.GREEN}🎮 Welcome to Interactive Search Mode!{Colors.END}")
        print(f"{Colors.CYAN}Type your search queries below, or 'help' for tips{Colors.END}")
        print(f"{Colors.YELLOW}Commands: 'help', 'tips', 'quit' or 'exit'{Colors.END}\n")
        
        while True:
            try:
                # Get user input with fancy prompt
                query = input(f"{Colors.BOLD}{Colors.PURPLE}🔍 Search> {Colors.END}").strip()
                
                if not query:
                    continue
                
                # Handle commands
                if query.lower() in ['quit', 'exit', 'q']:
                    print(f"{Colors.CYAN}👋 Thanks for using Memory Vault Search! Happy memory keeping!{Colors.END}")
                    break
                elif query.lower() in ['help', 'tips']:
                    self.display_search_tips()
                    continue
                elif query.lower() == 'clear':
                    print("\033[2J\033[H")  # Clear screen
                    self.print_banner()
                    continue
                
                # Show search in progress
                print(f"{Colors.YELLOW}🔄 Searching for: \"{query}\"...{Colors.END}")
                
                # Perform search
                self.search_count += 1
                results = self.search_memories(query, limit=5)
                
                # Display results
                self.display_search_results(results, query)
                
                # Achievement tracking
                if self.search_count == 1:
                    print(f"\n{Colors.PURPLE}🏆 Achievement Unlocked: Vault Explorer - First semantic search!{Colors.END}")
                elif self.search_count == 5:
                    print(f"\n{Colors.PURPLE}🏆 Achievement Unlocked: Search Master - 5 searches completed!{Colors.END}")
                elif self.search_count == 10:
                    print(f"\n{Colors.PURPLE}🏆 Achievement Unlocked: Memory Detective - 10 searches completed!{Colors.END}")
                
                print()  # Extra spacing
                
            except KeyboardInterrupt:
                print(f"\n{Colors.CYAN}👋 Search interrupted. Thanks for using Memory Vault!{Colors.END}")
                break
            except Exception as e:
                print(f"{Colors.RED}❌ An error occurred: {str(e)}{Colors.END}")
                print(f"{Colors.YELLOW}Please try again or type 'quit' to exit{Colors.END}")
    
    def run_demo_searches(self):
        """Run a few demo searches to showcase the system"""
        demo_queries = [
            "Python decorators and functions",
            "time management productivity techniques", 
            "React hooks state management"
        ]
        
        print(f"\n{Colors.YELLOW}🎭 Running demo searches to showcase semantic search...{Colors.END}\n")
        
        for i, query in enumerate(demo_queries, 1):
            print(f"{Colors.PURPLE}Demo {i}/3:{Colors.END} Searching for \"{query}\"")
            print("─" * 50)
            
            results = self.search_memories(query, limit=2)
            self.display_search_results(results, query)
            
            if i < len(demo_queries):
                input(f"\n{Colors.CYAN}Press Enter to continue to next demo...{Colors.END}")
        
        print(f"\n{Colors.GREEN}🎉 Demo complete! Now try your own searches.{Colors.END}")

def main():
    """Main function"""
    search_engine = MemoryVaultSearch()
    search_engine.print_banner()
    
    # Check server health
    print(f"{Colors.YELLOW}🔍 Checking Memory Vault connection...{Colors.END}")
    if not search_engine.check_server_health():
        print(f"{Colors.RED}❌ Error: Memory Vault server not running!{Colors.END}")
        print(f"{Colors.YELLOW}💡 Run 'make start' first to awaken the vault{Colors.END}")
        sys.exit(1)
    
    print(f"{Colors.GREEN}✅ Connected to Memory Vault!{Colors.END}")
    
    # Ask user preference
    print(f"\n{Colors.CYAN}Choose your adventure:{Colors.END}")
    print(f"{Colors.GREEN}  1. Run demo searches (see examples){Colors.END}")
    print(f"{Colors.GREEN}  2. Start interactive search immediately{Colors.END}")
    
    while True:
        try:
            choice = input(f"{Colors.YELLOW}Enter choice (1 or 2): {Colors.END}").strip()
            
            if choice == "1":
                search_engine.run_demo_searches()
                search_engine.interactive_search_loop()
                break
            elif choice == "2":
                search_engine.interactive_search_loop()
                break
            else:
                print(f"{Colors.RED}Please enter 1 or 2{Colors.END}")
        except KeyboardInterrupt:
            print(f"\n{Colors.CYAN}👋 Goodbye!{Colors.END}")
            sys.exit(0)

if __name__ == "__main__":
    main()
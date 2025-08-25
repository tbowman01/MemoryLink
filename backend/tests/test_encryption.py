"""Tests for encryption utilities."""

import pytest
from src.utils.encryption import EncryptionService


@pytest.fixture
def encryption_service():
    """Create an encryption service for testing."""
    return EncryptionService("test-encryption-key-123")


def test_encrypt_decrypt_text(encryption_service):
    """Test basic text encryption and decryption."""
    original_text = "This is a test message for encryption"
    
    # Encrypt the text
    encrypted_text = encryption_service.encrypt(original_text)
    
    # Verify encryption changes the text
    assert encrypted_text != original_text
    assert isinstance(encrypted_text, str)
    assert len(encrypted_text) > 0
    
    # Decrypt the text
    decrypted_text = encryption_service.decrypt(encrypted_text)
    
    # Verify decryption restores original text
    assert decrypted_text == original_text


def test_encrypt_empty_string(encryption_service):
    """Test encryption of empty string."""
    empty_text = ""
    encrypted_text = encryption_service.encrypt(empty_text)
    decrypted_text = encryption_service.decrypt(encrypted_text)
    
    assert decrypted_text == empty_text


def test_encrypt_unicode_text(encryption_service):
    """Test encryption of unicode text."""
    unicode_text = "Hello 世界! 🌍 Ñiño café"
    
    encrypted_text = encryption_service.encrypt(unicode_text)
    decrypted_text = encryption_service.decrypt(encrypted_text)
    
    assert decrypted_text == unicode_text


def test_encrypt_dict(encryption_service):
    """Test dictionary encryption."""
    original_dict = {
        "id": "123",
        "text": "Secret message",
        "metadata": {
            "note": "Private note",
            "public": "Public info"
        },
        "tags": ["secret", "test"]
    }
    
    encrypted_dict = encryption_service.encrypt_dict(original_dict)
    
    # Verify text is encrypted
    assert encrypted_dict["text"] != original_dict["text"]
    assert encrypted_dict["id"] == original_dict["id"]  # ID not encrypted
    assert encrypted_dict["tags"] == original_dict["tags"]  # Tags not encrypted
    
    # Verify metadata is encrypted
    assert encrypted_dict["metadata"]["note"] != original_dict["metadata"]["note"]
    assert encrypted_dict["metadata"]["public"] != original_dict["metadata"]["public"]


def test_decrypt_dict(encryption_service):
    """Test dictionary decryption."""
    original_dict = {
        "id": "123",
        "text": "Secret message",
        "metadata": {
            "note": "Private note",
            "count": 42  # Non-string value
        },
        "tags": ["secret", "test"]
    }
    
    # Encrypt then decrypt
    encrypted_dict = encryption_service.encrypt_dict(original_dict)
    decrypted_dict = encryption_service.decrypt_dict(encrypted_dict)
    
    # Verify decryption restores original values
    assert decrypted_dict["text"] == original_dict["text"]
    assert decrypted_dict["metadata"]["note"] == original_dict["metadata"]["note"]
    assert decrypted_dict["metadata"]["count"] == original_dict["metadata"]["count"]
    assert decrypted_dict["id"] == original_dict["id"]
    assert decrypted_dict["tags"] == original_dict["tags"]


def test_invalid_decryption(encryption_service):
    """Test decryption of invalid data."""
    invalid_encrypted_text = "invalid-encrypted-data"
    
    with pytest.raises(ValueError, match="Decryption failed"):
        encryption_service.decrypt(invalid_encrypted_text)


def test_different_keys_fail():
    """Test that different keys can't decrypt each other's data."""
    service1 = EncryptionService("key1")
    service2 = EncryptionService("key2")
    
    text = "Test message"
    encrypted_text = service1.encrypt(text)
    
    # Different service should not be able to decrypt
    with pytest.raises(ValueError):
        service2.decrypt(encrypted_text)


def test_generate_key():
    """Test key generation."""
    key = EncryptionService.generate_key()
    
    assert isinstance(key, str)
    assert len(key) > 0
    
    # Should be able to create service with generated key
    service = EncryptionService(key)
    test_text = "Test with generated key"
    encrypted = service.encrypt(test_text)
    decrypted = service.decrypt(encrypted)
    
    assert decrypted == test_text
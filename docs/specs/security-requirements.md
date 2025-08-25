# MemoryLink Security Requirements Specification

## Document Information
- **Version**: 1.0
- **Date**: 2025-08-24
- **Classification**: Internal Use
- **Compliance**: Local-First Privacy Standards

## 1. Security Objectives

### 1.1 Primary Goals
- **Data Privacy**: Personal memory data never leaves user's device without explicit consent
- **Encryption at Rest**: All sensitive content encrypted using industry-standard algorithms
- **Access Control**: Unauthorized access prevented through multiple layers
- **Audit Trail**: Complete logging of security-relevant operations
- **Zero Trust**: No implicit trust in storage or network layers

### 1.2 Threat Model

#### Assets to Protect
- **Personal Memory Content**: Text, conversations, notes, code snippets
- **Metadata**: Tags, timestamps, source information
- **User Identities**: User IDs and session information
- **Encryption Keys**: Master keys and derived keys
- **System Configuration**: API keys, database connections

#### Threat Actors
- **Malicious Software**: Malware accessing local files
- **Unauthorized Users**: Others with access to the device
- **Network Attackers**: If API exposed beyond localhost
- **Cloud Providers**: If sync features enabled in future
- **System Administrators**: With file system access

#### Attack Vectors
- Direct file system access to database files
- Memory dumps and process inspection
- Network traffic interception
- API abuse and injection attacks
- Social engineering for encryption keys

## 2. Encryption Requirements

### 2.1 Data at Rest Encryption

#### SR-001: Content Encryption
**Requirement**: All memory text content SHALL be encrypted before storage  
**Algorithm**: AES-256-GCM (Galois/Counter Mode)  
**Key Size**: 256 bits (32 bytes)  
**Implementation**: Python `cryptography` library

**Acceptance Criteria**:
- ✅ Plain text content never stored unencrypted
- ✅ Encryption key derived using PBKDF2 with 100,000+ iterations
- ✅ Unique IV/nonce generated for each encryption operation
- ✅ Authentication tag validates data integrity
- ✅ Encrypted data unreadable without proper decryption key

#### SR-002: Key Management
**Requirement**: Encryption keys SHALL be securely generated and stored  
**Key Derivation**: PBKDF2-SHA256 from user passphrase  
**Salt**: Random 32-byte salt per user  
**Storage**: Environment variable or secure key file

**Implementation Specification**:
```python
# Key derivation parameters
PBKDF2_ITERATIONS = 100_000
SALT_LENGTH = 32  # bytes
KEY_LENGTH = 32   # bytes for AES-256

# Key derivation function
def derive_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(passphrase.encode('utf-8'))
```

#### SR-003: Vector Embeddings Security
**Requirement**: Vector embeddings SHALL remain unencrypted for search functionality  
**Justification**: Embeddings required for similarity search operations  
**Mitigation**: Embeddings don't contain readable text content  
**Risk Assessment**: Low - embeddings are mathematical representations

### 2.2 Data in Transit Encryption

#### SR-004: API Communication Security
**Requirement**: All API communication SHALL use HTTPS when accessible over network  
**Default**: HTTP on localhost (127.0.0.1) for MVP  
**Network Deployment**: HTTPS required with valid TLS certificates  
**Minimum TLS Version**: TLS 1.2 or higher

#### SR-005: Internal Communication Security
**Requirement**: Communication between components SHALL be secured  
**MVP**: All components in same container (no network communication)  
**Future**: mTLS for inter-service communication in distributed deployment

## 3. Access Control Requirements

### 3.1 Authentication

#### SR-006: Local Access Control
**Requirement**: Default configuration SHALL bind to localhost only  
**Implementation**: Server listens on 127.0.0.1:8080  
**Network Access**: Explicitly configured via environment variable  
**MVP Scope**: Single-user authentication not required locally

#### SR-007: API Key Authentication (Optional)
**Requirement**: Network deployments SHALL support API key authentication  
**Implementation**: X-API-Key header validation  
**Key Format**: Base64-encoded random 256-bit key  
**Storage**: Environment variable or secure configuration

**API Key Specification**:
```python
# API key generation
import secrets
import base64

def generate_api_key() -> str:
    """Generate cryptographically secure API key"""
    key_bytes = secrets.token_bytes(32)  # 256 bits
    return base64.b64encode(key_bytes).decode('ascii')

# API key validation middleware
async def validate_api_key(request: Request) -> bool:
    if not config.api_key_required:
        return True
    
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        raise HTTPException(401, "API key required")
    
    return secrets.compare_digest(api_key, config.api_key)
```

### 3.2 Authorization

#### SR-008: User Scope Isolation
**Requirement**: Memory data SHALL be isolated by user scope  
**MVP Implementation**: Single user scope with user_id field  
**Future**: Multi-user isolation with proper access controls  
**Database**: User ID included in all queries as filter

#### SR-009: Resource Access Controls
**Requirement**: API endpoints SHALL validate resource access  
**Implementation**: Memory ownership validation before operations  
**Error Handling**: 404 responses for unauthorized resource access  
**Audit**: All access attempts logged

## 4. Data Protection Requirements

### 4.1 Sensitive Data Handling

#### SR-010: Memory Content Classification
**Content Types**:
- **Highly Sensitive**: API keys, passwords, personal information
- **Sensitive**: Code snippets, internal discussions, meeting notes
- **Public**: Documentation, general notes

**Protection Requirements**:
- All content encrypted regardless of sensitivity level
- Metadata encryption for highly sensitive content
- Selective masking in logs and error messages

#### SR-011: Metadata Protection
**Requirement**: Sensitive metadata SHALL be encrypted  
**Scope**: Custom metadata fields may contain sensitive information  
**Implementation**: Optional metadata encryption based on field classification  
**Configuration**: Configurable sensitive field patterns

```python
# Sensitive metadata field patterns
SENSITIVE_METADATA_PATTERNS = [
    r'.*password.*',
    r'.*secret.*', 
    r'.*key.*',
    r'.*token.*',
    r'.*credential.*'
]

def is_sensitive_metadata(key: str) -> bool:
    """Check if metadata key contains sensitive information"""
    key_lower = key.lower()
    return any(re.match(pattern, key_lower) for pattern in SENSITIVE_METADATA_PATTERNS)
```

### 4.2 Data Retention and Deletion

#### SR-012: Secure Deletion
**Requirement**: Deleted memories SHALL be securely removed  
**Implementation**: Cryptographic erasure through key deletion  
**Database**: Hard delete from database tables  
**Vector Store**: Embedding removal from vector index  
**Audit**: Deletion operations logged

#### SR-013: Data Backup Security
**Requirement**: Backup data SHALL maintain encryption protection  
**Implementation**: Encrypted database files in backup  
**Key Management**: Separate backup key derivation  
**Storage**: Backup encryption keys stored separately

## 5. Audit and Monitoring Requirements

### 5.1 Security Logging

#### SR-014: Operation Audit Trail
**Requirement**: All security-relevant operations SHALL be logged  
**Events to Log**:
- Authentication attempts (success/failure)
- Memory add/delete operations
- Search queries (without content)
- Configuration changes
- Error conditions and exceptions

**Log Format**:
```json
{
  "timestamp": "2025-08-24T20:11:46.174Z",
  "event_type": "memory_added",
  "user_id": "alice",
  "memory_id": "mem_12345",
  "source_ip": "127.0.0.1",
  "user_agent": "curl/7.68.0",
  "success": true,
  "metadata": {
    "content_length": 156,
    "tags_count": 3,
    "encryption_enabled": true
  }
}
```

#### SR-015: Security Monitoring
**Requirement**: Anomalous activity SHALL be detected and alerted  
**Metrics to Monitor**:
- Failed authentication attempts
- High-volume API requests
- Unusual memory access patterns
- Encryption/decryption failures
- Database connection errors

### 5.2 Privacy Protection in Logs

#### SR-016: Log Content Privacy
**Requirement**: Logs SHALL NOT contain sensitive memory content  
**Implementation**: Content hashing instead of full text  
**Metadata**: Only non-sensitive metadata fields logged  
**Search Queries**: Query patterns logged, not actual queries

```python
def log_memory_operation(memory_id: str, operation: str, content: str) -> None:
    """Log memory operation without exposing content"""
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
    
    log_entry = {
        "memory_id": memory_id,
        "operation": operation,
        "content_hash": content_hash,
        "content_length": len(content),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    security_logger.info(json.dumps(log_entry))
```

## 6. Configuration Security

### 6.1 Secure Configuration Management

#### SR-017: Environment Variable Security
**Requirement**: Sensitive configuration SHALL use secure environment variables  
**Implementation**: No secrets in code or configuration files  
**Validation**: Required environment variables checked at startup  
**Documentation**: Clear guidance on secure configuration

**Required Environment Variables**:
```bash
# Encryption configuration
MEMORYLINK_ENCRYPTION_KEY=""          # Base64-encoded encryption key
MEMORYLINK_ENCRYPTION_SALT=""         # Base64-encoded salt

# API security configuration  
MEMORYLINK_API_KEY=""                 # Optional API key
MEMORYLINK_API_KEY_REQUIRED=false     # Enable API key auth

# Database configuration
MEMORYLINK_DATABASE_URL="sqlite:///data/memorylink.db"
MEMORYLINK_VECTOR_STORE_PATH="data/vectors"

# Network configuration
MEMORYLINK_HOST="127.0.0.1"           # Localhost binding by default
MEMORYLINK_PORT=8080
MEMORYLINK_ENABLE_HTTPS=false
```

#### SR-018: Configuration Validation
**Requirement**: All security configuration SHALL be validated at startup  
**Checks**: Key strength, proper formatting, required dependencies  
**Failures**: Application refuses to start with invalid security config  
**Logging**: Configuration validation results logged (without sensitive values)

### 6.2 Docker Security

#### SR-019: Container Security
**Requirement**: Docker containers SHALL follow security best practices  
**Base Image**: Official Python slim images with security updates  
**User**: Non-root user inside container  
**Capabilities**: Minimal Linux capabilities  
**Secrets**: No secrets in Docker images or layers

**Dockerfile Security Configuration**:
```dockerfile
# Use official Python runtime with security updates
FROM python:3.11-slim-bookworm

# Create non-root user
RUN groupadd -r memorylink && useradd -r -g memorylink memorylink

# Set up directories with proper permissions
RUN mkdir -p /app/data && chown memorylink:memorylink /app/data

# Switch to non-root user
USER memorylink

# Copy application code
COPY --chown=memorylink:memorylink . /app/
WORKDIR /app

# Expose port (non-privileged)
EXPOSE 8080

# Run application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## 7. Incident Response Requirements

### 7.1 Security Incident Handling

#### SR-020: Incident Detection
**Requirement**: Security incidents SHALL be detected and classified  
**Detection**: Automated monitoring of security events  
**Classification**: Critical, High, Medium, Low severity levels  
**Response Time**: Immediate alert for critical incidents

#### SR-021: Breach Response
**Requirement**: Data breach response procedure SHALL be documented  
**Steps**:
1. Incident containment and system isolation
2. Impact assessment and affected data identification
3. Key rotation and re-encryption procedures
4. User notification and guidance
5. Post-incident analysis and improvements

### 7.2 Recovery Procedures

#### SR-022: Key Recovery
**Requirement**: Encryption key recovery procedures SHALL be available  
**Backup**: Secure key backup mechanism  
**Recovery**: Step-by-step key restoration process  
**Testing**: Regular recovery procedure testing

#### SR-023: Data Recovery
**Requirement**: Encrypted data recovery SHALL be possible with valid keys  
**Backup**: Regular encrypted database backups  
**Restore**: Data restoration from encrypted backups  
**Validation**: Data integrity verification after recovery

## 8. Compliance and Standards

### 8.1 Privacy Compliance

#### SR-024: GDPR Compliance (Future)
**Requirement**: Design SHALL support GDPR compliance requirements  
**Right to Access**: User can export all their memory data  
**Right to Deletion**: Complete data removal capability  
**Data Portability**: Standard export formats available  
**Privacy by Design**: Default settings protect user privacy

#### SR-025: Local Data Protection
**Requirement**: Data protection SHALL not depend on external services  
**Implementation**: All encryption and security locally managed  
**Cloud Independence**: No mandatory cloud components  
**User Control**: User maintains complete control over their data

### 8.2 Security Standards

#### SR-026: Cryptographic Standards
**Requirement**: All cryptographic operations SHALL use approved algorithms  
**Standards**: NIST-approved algorithms and key lengths  
**Libraries**: Well-maintained cryptographic libraries  
**Updates**: Regular security update procedures

**Approved Cryptographic Algorithms**:
- **Symmetric Encryption**: AES-256-GCM
- **Key Derivation**: PBKDF2-SHA256 (100,000+ iterations)
- **Hashing**: SHA-256, SHA-512
- **Random Generation**: OS cryptographically secure random
- **TLS**: TLS 1.2+ with strong cipher suites

## 9. Security Testing Requirements

### 9.1 Security Test Cases

#### SR-027: Encryption Testing
**Test Cases**:
- Verify encrypted data is unreadable without key
- Confirm key derivation produces consistent results
- Validate IV/nonce uniqueness for each encryption
- Test key rotation and data re-encryption
- Verify secure deletion removes all traces

#### SR-028: Access Control Testing
**Test Cases**:
- Verify localhost-only binding prevents network access
- Confirm API key authentication works correctly
- Test unauthorized access returns appropriate errors
- Validate user scope isolation
- Check audit logging captures all events

### 9.2 Penetration Testing

#### SR-029: Security Assessment
**Requirement**: Regular security assessments SHALL be conducted  
**Scope**: API endpoints, encryption implementation, access controls  
**Tools**: Automated security scanning and manual testing  
**Reporting**: Detailed findings with remediation guidance

## 10. Security Checklist

### 10.1 Implementation Checklist
- [ ] AES-256-GCM encryption implemented for memory content
- [ ] PBKDF2 key derivation with 100,000+ iterations
- [ ] Unique salt and IV generation for each operation
- [ ] Localhost binding configured by default
- [ ] API key authentication available for network deployment
- [ ] Security logging implemented without content exposure
- [ ] Environment variable configuration for secrets
- [ ] Docker container runs as non-root user
- [ ] Error messages don't leak sensitive information
- [ ] Secure deletion removes data from all storage

### 10.2 Security Review Checklist
- [ ] Cryptographic implementation reviewed by security expert
- [ ] Threat model validated against design
- [ ] Security controls tested and verified
- [ ] Documentation includes security guidance
- [ ] Incident response procedures defined
- [ ] Regular security update process established

This security requirements specification ensures MemoryLink MVP maintains strong protection for user data while supporting the local-first architecture and developer-friendly experience goals.
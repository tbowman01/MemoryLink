# 🪝 Hooks & Automation Guide

This guide explains how to create and use hooks for automating MemoryLink workflows in your development environment.

## 📋 Overview

Hooks are automated triggers that execute when specific events occur in your development workflow. They enable automatic memory capture, context preservation, and intelligent code assistance.

## 🎯 Hook Types

### File Hooks
Triggered by file system events:
- `pre-save` - Before file is saved
- `post-save` - After file is saved
- `pre-open` - Before file is opened
- `post-open` - After file is opened
- `pre-close` - Before file is closed
- `file-change` - When file content changes

### Git Hooks
Triggered by version control events:
- `pre-commit` - Before git commit
- `post-commit` - After git commit
- `pre-push` - Before git push
- `post-merge` - After git merge
- `pre-rebase` - Before git rebase

### Development Hooks
Triggered by development activities:
- `pre-build` - Before build process
- `post-build` - After build process
- `pre-test` - Before running tests
- `post-test` - After running tests
- `pre-debug` - Before debug session
- `post-debug` - After debug session

### AI Interaction Hooks
Triggered by AI assistant events:
- `pre-ai-query` - Before AI query
- `post-ai-response` - After AI response
- `code-suggestion` - When code is suggested
- `code-accepted` - When suggestion is accepted

## 🛠️ Setting Up Hooks

### Basic Hook Structure

Create `.memorylink/hooks/config.json`:

```json
{
  "version": "1.0",
  "hooks": {
    "post-save": {
      "enabled": true,
      "script": "./hooks/post-save.js",
      "patterns": ["**/*.{js,ts,py}"],
      "exclude": ["**/node_modules/**", "**/dist/**"]
    },
    "pre-commit": {
      "enabled": true,
      "script": "./hooks/pre-commit.sh",
      "captureContext": true,
      "storeDecisions": true
    },
    "post-test": {
      "enabled": true,
      "script": "./hooks/post-test.js",
      "onlyOnFailure": false,
      "captureOutput": true
    }
  },
  "global": {
    "timeout": 30000,
    "retryOnFailure": true,
    "maxRetries": 3,
    "logLevel": "info"
  }
}
```

### JavaScript Hook Example

Create `.memorylink/hooks/post-save.js`:

```javascript
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Hook configuration
const config = {
  apiUrl: process.env.MEMORYLINK_API_URL || 'http://localhost:8000',
  apiKey: process.env.MEMORYLINK_API_KEY,
  contextLines: 10,
  enableAnalysis: true
};

// Main hook function
async function postSaveHook() {
  const file = process.argv[2];
  
  if (!file) {
    console.error('No file provided');
    process.exit(1);
  }
  
  try {
    // 1. Capture file context
    const context = await captureContext(file);
    
    // 2. Analyze changes
    const analysis = await analyzeChanges(file);
    
    // 3. Store memory
    await storeMemory({
      type: 'file-save',
      file: path.basename(file),
      path: file,
      context,
      analysis,
      timestamp: new Date().toISOString(),
      tags: generateTags(file)
    });
    
    // 4. Trigger additional workflows
    await triggerWorkflows(file, analysis);
    
    console.log(`✓ Post-save hook completed for ${file}`);
  } catch (error) {
    console.error(`✗ Hook failed: ${error.message}`);
    process.exit(1);
  }
}

// Capture file context
async function captureContext(file) {
  const content = fs.readFileSync(file, 'utf8');
  const lines = content.split('\n');
  
  // Get git diff if available
  let gitDiff = '';
  try {
    gitDiff = execSync(`git diff ${file}`, { encoding: 'utf8' });
  } catch (e) {
    // Not in git repo or no changes
  }
  
  return {
    totalLines: lines.length,
    language: detectLanguage(file),
    gitDiff: gitDiff || null,
    functions: extractFunctions(content),
    imports: extractImports(content),
    complexity: calculateComplexity(content)
  };
}

// Analyze code changes
async function analyzeChanges(file) {
  if (!config.enableAnalysis) return null;
  
  try {
    // Run Claude Flow analysis
    const analysis = execSync(
      `npx claude-flow analyze "${file}" --json`,
      { encoding: 'utf8' }
    );
    return JSON.parse(analysis);
  } catch (e) {
    return null;
  }
}

// Store memory via API
async function storeMemory(data) {
  const response = await fetch(`${config.apiUrl}/api/memories`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${config.apiKey}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    throw new Error(`Failed to store memory: ${response.statusText}`);
  }
  
  return response.json();
}

// Trigger additional workflows
async function triggerWorkflows(file, analysis) {
  // Auto-generate tests if needed
  if (shouldGenerateTests(file, analysis)) {
    execSync(`npx claude-flow sparc tdd "${file}"`, { stdio: 'inherit' });
  }
  
  // Auto-document if needed
  if (shouldDocument(file, analysis)) {
    execSync(`npx claude-flow sparc run docs-writer "document ${file}"`, { stdio: 'inherit' });
  }
  
  // Check for security issues
  if (analysis?.security?.issues) {
    execSync(`npx claude-flow security scan "${file}"`, { stdio: 'inherit' });
  }
}

// Helper functions
function detectLanguage(file) {
  const ext = path.extname(file).toLowerCase();
  const langMap = {
    '.js': 'javascript',
    '.ts': 'typescript',
    '.py': 'python',
    '.java': 'java',
    '.go': 'go',
    '.rs': 'rust'
  };
  return langMap[ext] || 'unknown';
}

function extractFunctions(content) {
  const patterns = {
    javascript: /function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[^=]*)=>/g,
    python: /def\s+(\w+)\s*\(/g,
    java: /(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(/g
  };
  
  // Extract based on detected language
  const functions = [];
  // ... extraction logic
  return functions;
}

function extractImports(content) {
  const patterns = {
    javascript: /import\s+.*\s+from\s+['"]([^'"]+)['"]/g,
    python: /(?:from\s+(\S+)\s+)?import\s+(\S+)/g,
    java: /import\s+([\w.]+);/g
  };
  
  const imports = [];
  // ... extraction logic
  return imports;
}

function calculateComplexity(content) {
  // Simple cyclomatic complexity
  let complexity = 1;
  const decisionPoints = [
    /if\s*\(/g,
    /else\s+if\s*\(/g,
    /for\s*\(/g,
    /while\s*\(/g,
    /case\s+/g,
    /catch\s*\(/g
  ];
  
  decisionPoints.forEach(pattern => {
    const matches = content.match(pattern);
    if (matches) complexity += matches.length;
  });
  
  return complexity;
}

function generateTags(file) {
  const tags = [];
  const ext = path.extname(file);
  const dir = path.dirname(file);
  
  // Language tag
  tags.push(detectLanguage(file));
  
  // Directory-based tags
  if (dir.includes('test')) tags.push('test');
  if (dir.includes('src')) tags.push('source');
  if (dir.includes('docs')) tags.push('documentation');
  
  // File-based tags
  if (file.includes('.test.')) tags.push('test-file');
  if (file.includes('.spec.')) tags.push('spec-file');
  
  return tags;
}

function shouldGenerateTests(file, analysis) {
  // Check if tests are missing
  const testFile = file.replace(/\.(js|ts|py)$/, '.test.$1');
  return !fs.existsSync(testFile) && !file.includes('.test.');
}

function shouldDocument(file, analysis) {
  // Check if documentation is needed
  return analysis?.documentation?.coverage < 50;
}

// Run the hook
postSaveHook().catch(console.error);
```

### Shell Script Hook Example

Create `.memorylink/hooks/pre-commit.sh`:

```bash
#!/bin/bash

# Pre-commit hook for MemoryLink
set -e

echo "🪝 Running MemoryLink pre-commit hook..."

# Configuration
MEMORY_API="${MEMORYLINK_API_URL:-http://localhost:8000}"
API_KEY="${MEMORYLINK_API_KEY}"

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
  echo "No files staged for commit"
  exit 0
fi

# Function to store memory
store_memory() {
  local data="$1"
  curl -X POST "${MEMORY_API}/api/memories" \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "${data}" \
    --silent --fail
}

# Capture commit context
COMMIT_MSG=$(cat .git/COMMIT_EDITMSG 2>/dev/null || echo "")
BRANCH=$(git branch --show-current)
AUTHOR=$(git config user.name)

# Analyze each staged file
for FILE in $STAGED_FILES; do
  echo "  Analyzing: $FILE"
  
  # Get file stats
  ADDITIONS=$(git diff --cached --numstat "$FILE" | awk '{print $1}')
  DELETIONS=$(git diff --cached --numstat "$FILE" | awk '{print $2}')
  
  # Store file change memory
  MEMORY_DATA=$(cat <<EOF
{
  "type": "commit-file-change",
  "file": "$FILE",
  "branch": "$BRANCH",
  "author": "$AUTHOR",
  "additions": $ADDITIONS,
  "deletions": $DELETIONS,
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "tags": ["git", "commit", "pre-commit"]
}
EOF
)
  
  store_memory "$MEMORY_DATA"
done

# Run code quality checks
echo "  Running code quality checks..."

# Check for sensitive data
if grep -r "password\|secret\|token\|key" $STAGED_FILES 2>/dev/null | grep -v "^Binary"; then
  echo "⚠️  Warning: Possible sensitive data detected"
  read -p "Continue with commit? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Run linting
if command -v eslint &> /dev/null; then
  eslint $STAGED_FILES --quiet || true
fi

# Run type checking
if command -v tsc &> /dev/null; then
  tsc --noEmit || true
fi

# Store commit summary
COMMIT_MEMORY=$(cat <<EOF
{
  "type": "commit-summary",
  "message": "$COMMIT_MSG",
  "branch": "$BRANCH",
  "author": "$AUTHOR",
  "filesChanged": $(echo "$STAGED_FILES" | wc -l),
  "files": $(echo "$STAGED_FILES" | jq -R -s -c 'split("\n")[:-1]'),
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "tags": ["git", "commit", "summary"]
}
EOF
)

store_memory "$COMMIT_MEMORY"

echo "✓ Pre-commit hook completed successfully"
exit 0
```

## 🤖 Automated Workflows

### Continuous Memory Capture

Create `.memorylink/workflows/continuous-capture.js`:

```javascript
// Continuous memory capture workflow
const chokidar = require('chokidar');
const debounce = require('lodash.debounce');

class ContinuousCapture {
  constructor(config) {
    this.config = config;
    this.watcher = null;
    this.memoryQueue = [];
  }
  
  start() {
    // Watch for file changes
    this.watcher = chokidar.watch(this.config.paths, {
      ignored: this.config.ignore,
      persistent: true,
      ignoreInitial: true
    });
    
    // Set up event handlers
    this.watcher
      .on('change', debounce(this.onFileChange.bind(this), 1000))
      .on('add', this.onFileAdd.bind(this))
      .on('unlink', this.onFileDelete.bind(this));
    
    // Process memory queue periodically
    setInterval(() => this.processQueue(), 5000);
    
    console.log('Continuous capture started');
  }
  
  async onFileChange(path) {
    const memory = {
      type: 'file-change',
      path,
      timestamp: new Date().toISOString(),
      context: await this.captureContext(path),
      tags: ['auto-capture', 'file-change']
    };
    
    this.queueMemory(memory);
  }
  
  async onFileAdd(path) {
    const memory = {
      type: 'file-created',
      path,
      timestamp: new Date().toISOString(),
      tags: ['auto-capture', 'file-new']
    };
    
    this.queueMemory(memory);
  }
  
  async onFileDelete(path) {
    const memory = {
      type: 'file-deleted',
      path,
      timestamp: new Date().toISOString(),
      tags: ['auto-capture', 'file-deleted']
    };
    
    this.queueMemory(memory);
  }
  
  queueMemory(memory) {
    this.memoryQueue.push(memory);
  }
  
  async processQueue() {
    if (this.memoryQueue.length === 0) return;
    
    const batch = this.memoryQueue.splice(0, 10);
    
    try {
      await this.storeBatch(batch);
    } catch (error) {
      console.error('Failed to store memory batch:', error);
      // Re-queue on failure
      this.memoryQueue.unshift(...batch);
    }
  }
  
  async captureContext(path) {
    // Capture relevant context
    return {
      // ... context extraction logic
    };
  }
  
  async storeBatch(memories) {
    // Store memories in batch
    // ... API call logic
  }
  
  stop() {
    if (this.watcher) {
      this.watcher.close();
    }
    this.processQueue(); // Process remaining
  }
}

// Start continuous capture
const capture = new ContinuousCapture({
  paths: ['src/**/*', 'tests/**/*'],
  ignore: ['**/node_modules/**', '**/dist/**']
});

capture.start();

// Graceful shutdown
process.on('SIGINT', () => {
  capture.stop();
  process.exit(0);
});
```

### Smart Context Builder

Create `.memorylink/workflows/context-builder.js`:

```javascript
// Smart context builder for enhanced AI interactions
class SmartContextBuilder {
  constructor(memoryApi) {
    this.memoryApi = memoryApi;
    this.contextCache = new Map();
  }
  
  async buildContext(request) {
    const { file, line, query, maxMemories = 10 } = request;
    
    // Check cache
    const cacheKey = `${file}:${line}:${query}`;
    if (this.contextCache.has(cacheKey)) {
      return this.contextCache.get(cacheKey);
    }
    
    // Build multi-layer context
    const context = {
      immediate: await this.getImmediateContext(file, line),
      related: await this.getRelatedMemories(query),
      patterns: await this.getPatterns(file),
      decisions: await this.getArchitecturalDecisions(),
      recent: await this.getRecentChanges(file)
    };
    
    // Rank and filter memories
    const rankedContext = this.rankContext(context, query);
    
    // Cache for 5 minutes
    this.contextCache.set(cacheKey, rankedContext);
    setTimeout(() => this.contextCache.delete(cacheKey), 300000);
    
    return rankedContext;
  }
  
  async getImmediateContext(file, line) {
    // Get context around current position
    // ... implementation
  }
  
  async getRelatedMemories(query) {
    // Search for related memories
    return this.memoryApi.search(query);
  }
  
  async getPatterns(file) {
    // Get code patterns for file type
    // ... implementation
  }
  
  async getArchitecturalDecisions() {
    // Get architectural decisions
    return this.memoryApi.search('architecture decision');
  }
  
  async getRecentChanges(file) {
    // Get recent changes to file
    // ... implementation
  }
  
  rankContext(context, query) {
    // Rank memories by relevance
    // ... ranking algorithm
    return context;
  }
}
```

## 📝 Hook Registration

### Manual Registration

```bash
# Register hooks manually
memorylink hooks register .memorylink/hooks/config.json

# Verify hooks
memorylink hooks list

# Test specific hook
memorylink hooks test post-save

# Disable hook temporarily
memorylink hooks disable pre-commit

# Enable hook
memorylink hooks enable pre-commit
```

### Automatic Registration

Create `.memorylink/install.sh`:

```bash
#!/bin/bash

echo "Installing MemoryLink hooks..."

# Create hooks directory
mkdir -p .git/hooks

# Link git hooks
ln -sf ../../.memorylink/hooks/pre-commit.sh .git/hooks/pre-commit
ln -sf ../../.memorylink/hooks/post-commit.sh .git/hooks/post-commit

# Install npm hooks
npm install --save-dev husky
npx husky install
npx husky add .husky/pre-commit "node .memorylink/hooks/pre-commit.js"

# Install file watchers
npm install --save-dev chokidar

# Start continuous capture
nohup node .memorylink/workflows/continuous-capture.js &

echo "✓ Hooks installed successfully"
```

## 🔧 Configuration Examples

### Development Environment

```json
{
  "environment": "development",
  "hooks": {
    "post-save": {
      "enabled": true,
      "debounce": 1000,
      "captureAll": true
    },
    "pre-commit": {
      "enabled": true,
      "runTests": true,
      "runLinting": true
    }
  },
  "capture": {
    "verbose": true,
    "includeDebugInfo": true,
    "storeErrors": true
  }
}
```

### Production Environment

```json
{
  "environment": "production",
  "hooks": {
    "post-save": {
      "enabled": false
    },
    "pre-commit": {
      "enabled": true,
      "strict": true,
      "blockOnFailure": true
    }
  },
  "capture": {
    "verbose": false,
    "sanitizeSensitive": true,
    "compressionLevel": 9
  }
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Hooks not executing**
   ```bash
   # Check hook permissions
   ls -la .git/hooks/
   chmod +x .git/hooks/*
   
   # Verify hook registration
   git config --list | grep hook
   ```

2. **Memory storage failing**
   ```bash
   # Test API connection
   curl -X POST http://localhost:8000/api/memories \
     -H "Authorization: Bearer $MEMORYLINK_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"test": true}'
   ```

3. **Performance issues**
   ```bash
   # Check hook execution time
   time .memorylink/hooks/post-save.js test.js
   
   # Monitor memory queue
   node -e "require('.memorylink/monitor').showQueue()"
   ```

## 🔗 Related Documentation

- [VSCode Integration](./vscode-integration.md)
- [Cursor Integration](./cursor-integration.md)
- [Custom Rules Guide](./custom-rules.md)
- [API Documentation](./api.md)

---

*For more information, see the [main documentation](./README.md)*
# 🔧 VSCode Integration Guide

This guide explains how to integrate MemoryLink with Visual Studio Code for enhanced development workflows, automated memory capture, and intelligent code assistance.

## 📋 Prerequisites

- VSCode 1.80.0 or later
- Node.js 18+ and npm
- MemoryLink backend running locally or accessible
- Claude Flow installed (`npm install -g claude-flow@alpha`)

## 🚀 Installation

### Step 1: Install Required Extensions

```bash
# Install from VSCode marketplace or command palette
code --install-extension ms-python.python
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension redhat.vscode-yaml
```

### Step 2: Configure VSCode Settings

Create or update `.vscode/settings.json`:

```json
{
  "memorylink": {
    "apiUrl": "http://localhost:8000",
    "apiKey": "${env:MEMORYLINK_API_KEY}",
    "autoCapture": true,
    "captureInterval": 300000,
    "enableHooks": true
  },
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true,
    "source.fixAll": true
  },
  "files.watcherExclude": {
    "**/memory/**": true,
    "**/.claude-flow/**": true
  }
}
```

## 🎯 Custom Rules Configuration

### Creating Custom Rules

Create `.vscode/memorylink-rules.json`:

```json
{
  "rules": [
    {
      "name": "auto-document-functions",
      "trigger": "onSave",
      "pattern": "**/*.{js,ts,py}",
      "action": "captureContext",
      "config": {
        "contextLines": 10,
        "includeImports": true,
        "tags": ["function", "auto-documented"]
      }
    },
    {
      "name": "capture-debug-sessions",
      "trigger": "onDebugStart",
      "action": "createMemory",
      "config": {
        "type": "debug-session",
        "includeBreakpoints": true,
        "includeWatchExpressions": true
      }
    },
    {
      "name": "track-refactoring",
      "trigger": "onRefactor",
      "pattern": "**/*.{js,ts}",
      "action": "compareAndStore",
      "config": {
        "storeDiff": true,
        "tags": ["refactoring", "code-evolution"]
      }
    }
  ]
}
```

### Rule Triggers

Available triggers for custom rules:

- `onSave` - When a file is saved
- `onOpen` - When a file is opened
- `onChange` - When file content changes
- `onDebugStart` - When debugging starts
- `onDebugEnd` - When debugging ends
- `onRefactor` - When refactoring is detected
- `onCommit` - Before git commit
- `onPush` - Before git push
- `interval` - At specified time intervals

### Rule Actions

Available actions for rules:

- `captureContext` - Store code context
- `createMemory` - Create a new memory entry
- `updateMemory` - Update existing memory
- `compareAndStore` - Store code differences
- `runCommand` - Execute a shell command
- `invokeHook` - Trigger a custom hook

## 🪝 Hooks Configuration

### Setting Up Hooks

Create `.vscode/memorylink-hooks.js`:

```javascript
// memorylink-hooks.js
const { exec } = require('child_process');
const axios = require('axios');

const MEMORY_API = process.env.MEMORYLINK_API_URL || 'http://localhost:8000';
const API_KEY = process.env.MEMORYLINK_API_KEY;

// Pre-save hook - Analyze code before saving
exports.preSave = async (document) => {
  const filePath = document.fileName;
  const content = document.getText();
  
  // Analyze code complexity
  if (filePath.endsWith('.js') || filePath.endsWith('.ts')) {
    const complexity = analyzeComplexity(content);
    if (complexity > 10) {
      // Store high-complexity code for review
      await storeMemory({
        type: 'high-complexity-code',
        file: filePath,
        complexity,
        content: content.substring(0, 500),
        tags: ['review-needed', 'complexity']
      });
    }
  }
  
  return true; // Allow save to continue
};

// Post-save hook - Capture context after saving
exports.postSave = async (document) => {
  const filePath = document.fileName;
  
  // Run Claude Flow analysis
  exec(`npx claude-flow analyze "${filePath}"`, async (error, stdout) => {
    if (!error && stdout) {
      await storeMemory({
        type: 'code-analysis',
        file: filePath,
        analysis: stdout,
        timestamp: new Date().toISOString()
      });
    }
  });
};

// Debug hook - Capture debug context
exports.onDebugSession = async (session) => {
  const breakpoints = session.breakpoints;
  const variables = session.variables;
  
  await storeMemory({
    type: 'debug-session',
    sessionId: session.id,
    breakpoints,
    variables: sanitizeVariables(variables),
    timestamp: new Date().toISOString(),
    tags: ['debug', 'development']
  });
};

// Git commit hook - Capture commit context
exports.preCommit = async (files, message) => {
  const changes = await getGitDiff(files);
  
  await storeMemory({
    type: 'commit-context',
    message,
    files: files.map(f => f.path),
    changes: changes.substring(0, 2000),
    timestamp: new Date().toISOString(),
    tags: ['git', 'commit']
  });
  
  // Run SPARC code review
  exec('npx claude-flow sparc run reviewer "review staged changes"');
};

// Helper functions
async function storeMemory(data) {
  try {
    await axios.post(`${MEMORY_API}/api/memories`, data, {
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
      }
    });
  } catch (error) {
    console.error('Failed to store memory:', error);
  }
}

function analyzeComplexity(code) {
  // Simple cyclomatic complexity calculation
  const patterns = [/if\s*\(/g, /else\s+if\s*\(/g, /for\s*\(/g, /while\s*\(/g, /case\s+/g];
  let complexity = 1;
  patterns.forEach(pattern => {
    const matches = code.match(pattern);
    if (matches) complexity += matches.length;
  });
  return complexity;
}

function sanitizeVariables(variables) {
  // Remove sensitive data from variables
  const sanitized = {};
  for (const [key, value] of Object.entries(variables)) {
    if (!key.match(/password|token|secret|key/i)) {
      sanitized[key] = typeof value === 'object' ? '[Object]' : value;
    }
  }
  return sanitized;
}

async function getGitDiff(files) {
  return new Promise((resolve) => {
    exec('git diff --cached', (error, stdout) => {
      resolve(error ? '' : stdout);
    });
  });
}
```

### Registering Hooks

Create `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "MemoryLink: Register Hooks",
      "type": "shell",
      "command": "node",
      "args": [
        "${workspaceFolder}/.vscode/register-hooks.js"
      ],
      "problemMatcher": [],
      "runOptions": {
        "runOn": "folderOpen"
      }
    },
    {
      "label": "MemoryLink: Capture Context",
      "type": "shell",
      "command": "npx",
      "args": [
        "claude-flow",
        "memory",
        "store",
        "vscode-context",
        "${file}:${lineNumber}",
        "--namespace",
        "vscode"
      ],
      "problemMatcher": []
    }
  ]
}
```

## 🤖 Automation Examples

### Automatic Documentation Generation

```json
{
  "name": "auto-document",
  "trigger": "onSave",
  "pattern": "**/*.{js,ts}",
  "condition": "hasUndocumentedFunctions",
  "action": "runCommand",
  "config": {
    "command": "npx claude-flow sparc run docs-writer 'document ${file}'"
  }
}
```

### Test Generation on Save

```json
{
  "name": "generate-tests",
  "trigger": "onSave",
  "pattern": "**/src/**/*.{js,ts}",
  "condition": "noTestFile",
  "action": "runCommand",
  "config": {
    "command": "npx claude-flow sparc tdd '${file}'"
  }
}
```

### Performance Monitoring

```json
{
  "name": "monitor-performance",
  "trigger": "interval",
  "interval": 3600000,
  "action": "runCommand",
  "config": {
    "command": "npx claude-flow analyze performance --store-memory"
  }
}
```

## 🎮 Keyboard Shortcuts

Add to `.vscode/keybindings.json`:

```json
[
  {
    "key": "ctrl+shift+m",
    "command": "memorylink.captureContext",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+s",
    "command": "memorylink.searchMemories",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+a",
    "command": "memorylink.analyzeCode",
    "when": "editorTextFocus"
  }
]
```

## 📝 VSCode Command Palette Integration

Available commands (Ctrl+Shift+P):

- `MemoryLink: Capture Current Context`
- `MemoryLink: Search Memories`
- `MemoryLink: Analyze Current File`
- `MemoryLink: Show Related Memories`
- `MemoryLink: Export Memory Session`
- `MemoryLink: Configure Rules`
- `MemoryLink: Run SPARC Analysis`

## 🔍 Debugging Integration

Configure `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug with MemoryLink",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/app.js",
      "preLaunchTask": "MemoryLink: Capture Context",
      "postDebugTask": "MemoryLink: Store Debug Session",
      "env": {
        "MEMORYLINK_CAPTURE": "true",
        "MEMORYLINK_API_URL": "http://localhost:8000"
      }
    }
  ]
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Hooks not triggering**
   ```bash
   # Check hook registration
   node .vscode/register-hooks.js --verify
   
   # Enable debug logging
   export MEMORYLINK_DEBUG=true
   ```

2. **API connection failed**
   ```bash
   # Test API connection
   curl http://localhost:8000/health
   
   # Check API key
   echo $MEMORYLINK_API_KEY
   ```

3. **Rules not applying**
   ```bash
   # Validate rules file
   npx claude-flow validate-rules .vscode/memorylink-rules.json
   ```

## 📚 Advanced Configuration

### Custom Memory Providers

```javascript
// .vscode/memory-provider.js
class CustomMemoryProvider {
  async store(memory) {
    // Custom storage logic
  }
  
  async search(query) {
    // Custom search logic
  }
  
  async getRelated(context) {
    // Custom relationship logic
  }
}

module.exports = CustomMemoryProvider;
```

### Integration with Git Hooks

```bash
# .git/hooks/pre-commit
#!/bin/sh
npx claude-flow hooks pre-commit --vscode
```

## 🔗 Related Documentation

- [Cursor Integration Guide](./cursor-integration.md)
- [Custom Rules Guide](./custom-rules.md)
- [Hooks & Automation](./hooks-automation.md)
- [API Documentation](./api.md)

---

*For more information, see the [main documentation](./README.md)*
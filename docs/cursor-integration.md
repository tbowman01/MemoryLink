# 🖱️ Cursor Integration Guide

This guide explains how to integrate MemoryLink with Cursor IDE for AI-powered development with automatic memory capture and intelligent code assistance.

## 📋 Prerequisites

- Cursor IDE (latest version)
- Node.js 18+ and npm
- MemoryLink backend running
- Claude Flow installed (`npm install -g claude-flow@alpha`)
- Active Cursor Pro subscription (for AI features)

## 🚀 Installation

### Step 1: Configure Cursor Settings

Open Cursor Settings (Cmd/Ctrl + ,) and add to `settings.json`:

```json
{
  "cursor.aiProvider": "claude-3",
  "cursor.memoryLink": {
    "enabled": true,
    "apiUrl": "http://localhost:8000",
    "apiKey": "${env:MEMORYLINK_API_KEY}",
    "autoSync": true,
    "syncInterval": 300000,
    "captureAIInteractions": true
  },
  "cursor.customRules": {
    "enabled": true,
    "rulesPath": ".cursor/rules",
    "autoLoad": true
  },
  "cursor.chat.defaultContext": {
    "includeMemories": true,
    "memoryLimit": 10,
    "relevanceThreshold": 0.7
  }
}
```

### Step 2: Create Cursor Rules Directory

```bash
mkdir -p .cursor/rules
```

## 🎯 Custom Rules for Cursor

### Basic Rule Structure

Create `.cursor/rules/memorylink.md`:

```markdown
# MemoryLink Integration Rules

You are integrated with MemoryLink, a personal memory layer system. Follow these rules:

## Context Awareness
- Always check for existing memories related to the current file/function
- Reference previous decisions and patterns stored in memory
- Maintain consistency with past implementations

## Memory Capture
- After significant code changes, store a memory with:
  - What was changed
  - Why it was changed
  - Any decisions made
  - Related context

## Code Generation
- When generating code, search memories for:
  - Similar implementations
  - Project conventions
  - Past decisions on architecture
  - Previous bug fixes

## Commands
When the user asks about memories or context, use these commands:
- Search memories: `npx claude-flow memory search "[query]"`
- Store memory: `npx claude-flow memory store "[key]" "[value]"`
- Get related: `curl -X POST http://localhost:8000/api/memories/search`
```

### Advanced Rule Configuration

Create `.cursor/rules/automation.md`:

```markdown
# Automated Memory Capture Rules

## On File Save
When a file is saved, automatically:
1. Capture the context around changed lines
2. Store any new function signatures
3. Track refactoring patterns

## On Debug Session
When debugging:
1. Capture error context and stack traces
2. Store successful fixes with explanations
3. Link related memories to the debug session

## On Code Review
During code review:
1. Store review comments as memories
2. Link suggestions to implementation
3. Track accepted/rejected changes

## Pattern Recognition
Identify and store:
- Repeated code patterns
- Common bug fixes
- Refactoring opportunities
- Performance optimizations

## Integration Commands
\`\`\`bash
# Store current context
npx claude-flow hooks post-edit --file "$CURRENT_FILE" --memory-key "cursor/edit/$(date +%s)"

# Search related memories
npx claude-flow memory search "$CURRENT_SELECTION" --limit 5

# Analyze code pattern
npx claude-flow sparc run analyzer "analyze $CURRENT_FILE for patterns"
\`\`\`
```

### Project-Specific Rules

Create `.cursor/rules/project.md`:

```markdown
# Project-Specific MemoryLink Rules

## Architecture Decisions
- Follow the microservices pattern established in memory ID: arch-001
- Use FastAPI for all new endpoints (decision: mem-fastapi-001)
- Implement vector search using the pattern in mem-vector-001

## Coding Standards
- Follow PEP 8 for Python code
- Use TypeScript for frontend components
- Implement error handling as per mem-error-pattern-001

## Testing Requirements
- Write tests before implementation (TDD)
- Minimum 80% code coverage
- Use pytest for Python, Jest for JavaScript

## Memory Tagging Convention
Tag all memories with:
- Component: [backend|frontend|api|database]
- Type: [feature|bugfix|refactor|optimization]
- Priority: [high|medium|low]

## Automation Triggers
- On import changes: Store dependency updates
- On function creation: Generate and store documentation
- On error: Capture context and search for similar past issues
```

## 🪝 Cursor-Specific Hooks

### Setting Up Cursor Hooks

Create `.cursor/hooks.js`:

```javascript
// Cursor-specific hooks for MemoryLink integration
const axios = require('axios');
const { exec } = require('child_process');

const MEMORY_API = 'http://localhost:8000';
const API_KEY = process.env.MEMORYLINK_API_KEY;

class CursorMemoryLinkHooks {
  constructor() {
    this.sessionMemories = [];
    this.aiInteractions = [];
  }

  // Capture AI chat interactions
  async onAIChat(prompt, response) {
    const memory = {
      type: 'ai-interaction',
      prompt: prompt.substring(0, 500),
      response: response.substring(0, 1000),
      timestamp: new Date().toISOString(),
      context: this.getCurrentContext(),
      tags: ['cursor', 'ai-chat']
    };
    
    await this.storeMemory(memory);
    this.aiInteractions.push(memory);
    
    // Learn from the interaction
    if (response.includes('function') || response.includes('class')) {
      await this.extractAndStorePattern(response);
    }
  }

  // Capture code completions
  async onCodeCompletion(trigger, completion, accepted) {
    if (accepted) {
      await this.storeMemory({
        type: 'code-completion',
        trigger,
        completion,
        file: this.getCurrentFile(),
        line: this.getCurrentLine(),
        accepted: true,
        tags: ['cursor', 'completion', 'accepted']
      });
    }
  }

  // Capture inline edits
  async onInlineEdit(original, edited, reason) {
    const memory = {
      type: 'inline-edit',
      original: original.substring(0, 500),
      edited: edited.substring(0, 500),
      reason,
      diff: this.computeDiff(original, edited),
      file: this.getCurrentFile(),
      timestamp: new Date().toISOString(),
      tags: ['cursor', 'edit', 'ai-assisted']
    };
    
    await this.storeMemory(memory);
    
    // Trigger SPARC analysis if significant change
    if (this.isSignificantChange(original, edited)) {
      exec(`npx claude-flow sparc run analyzer "analyze edit in ${this.getCurrentFile()}"`);
    }
  }

  // Capture terminal commands
  async onTerminalCommand(command, output) {
    if (this.shouldCaptureCommand(command)) {
      await this.storeMemory({
        type: 'terminal-command',
        command,
        output: output.substring(0, 1000),
        exitCode: output.exitCode,
        timestamp: new Date().toISOString(),
        tags: ['cursor', 'terminal']
      });
    }
  }

  // Search memories for context
  async searchMemories(query, limit = 5) {
    try {
      const response = await axios.post(
        `${MEMORY_API}/api/memories/search`,
        { query, limit },
        { headers: { 'Authorization': `Bearer ${API_KEY}` } }
      );
      return response.data.memories;
    } catch (error) {
      console.error('Memory search failed:', error);
      return [];
    }
  }

  // Store memory
  async storeMemory(data) {
    try {
      await axios.post(
        `${MEMORY_API}/api/memories`,
        { ...data, source: 'cursor' },
        { headers: { 'Authorization': `Bearer ${API_KEY}` } }
      );
    } catch (error) {
      console.error('Failed to store memory:', error);
    }
  }

  // Helper methods
  getCurrentContext() {
    return {
      file: process.env.CURSOR_CURRENT_FILE,
      line: process.env.CURSOR_CURRENT_LINE,
      selection: process.env.CURSOR_SELECTION,
      project: process.env.CURSOR_PROJECT_NAME
    };
  }

  getCurrentFile() {
    return process.env.CURSOR_CURRENT_FILE || 'unknown';
  }

  getCurrentLine() {
    return parseInt(process.env.CURSOR_CURRENT_LINE || '0');
  }

  computeDiff(original, edited) {
    // Simple diff for demonstration
    const lines1 = original.split('\n');
    const lines2 = edited.split('\n');
    const changes = [];
    
    for (let i = 0; i < Math.max(lines1.length, lines2.length); i++) {
      if (lines1[i] !== lines2[i]) {
        changes.push({
          line: i + 1,
          original: lines1[i],
          edited: lines2[i]
        });
      }
    }
    
    return changes;
  }

  isSignificantChange(original, edited) {
    // Detect significant changes
    const originalLines = original.split('\n').length;
    const editedLines = edited.split('\n').length;
    const lineDiff = Math.abs(originalLines - editedLines);
    
    return lineDiff > 10 || edited.length > original.length * 1.5;
  }

  shouldCaptureCommand(command) {
    // Filter commands to capture
    const capturePatterns = [
      /git /,
      /npm /,
      /docker/,
      /kubectl/,
      /python/,
      /claude-flow/
    ];
    
    return capturePatterns.some(pattern => pattern.test(command));
  }

  async extractAndStorePattern(code) {
    // Extract and store code patterns
    const patterns = [];
    
    // Function patterns
    const funcMatches = code.match(/function\s+(\w+)\s*\([^)]*\)/g);
    if (funcMatches) {
      patterns.push(...funcMatches.map(m => ({
        type: 'function-signature',
        pattern: m
      })));
    }
    
    // Class patterns
    const classMatches = code.match(/class\s+(\w+)/g);
    if (classMatches) {
      patterns.push(...classMatches.map(m => ({
        type: 'class-definition',
        pattern: m
      })));
    }
    
    if (patterns.length > 0) {
      await this.storeMemory({
        type: 'code-pattern',
        patterns,
        source: 'ai-generated',
        timestamp: new Date().toISOString(),
        tags: ['pattern', 'cursor', 'ai']
      });
    }
  }
}

// Export for Cursor integration
module.exports = new CursorMemoryLinkHooks();
```

## 🤖 AI Context Enhancement

### Configure AI Context

Create `.cursor/ai-context.json`:

```json
{
  "memoryLink": {
    "enabled": true,
    "contextBuilder": {
      "includeRelatedMemories": true,
      "maxMemories": 10,
      "relevanceThreshold": 0.7,
      "priorityTags": ["architecture", "decision", "pattern"],
      "excludeTags": ["deprecated", "experimental"]
    },
    "prompts": {
      "codeGeneration": "Check MemoryLink for similar implementations before generating code.",
      "debugging": "Search MemoryLink for previous occurrences of this error.",
      "refactoring": "Maintain consistency with patterns stored in MemoryLink.",
      "documentation": "Reference relevant memories in documentation."
    }
  }
}
```

## 📝 Cursor Commands

### Custom Command Registration

Create `.cursor/commands.json`:

```json
{
  "commands": [
    {
      "name": "Search Memories",
      "command": "memorylink.search",
      "shortcut": "cmd+shift+m",
      "action": "searchMemories"
    },
    {
      "name": "Store Selection as Memory",
      "command": "memorylink.store",
      "shortcut": "cmd+shift+s",
      "action": "storeSelection"
    },
    {
      "name": "Get Related Memories",
      "command": "memorylink.related",
      "shortcut": "cmd+shift+r",
      "action": "getRelated"
    },
    {
      "name": "Analyze with SPARC",
      "command": "memorylink.sparc",
      "shortcut": "cmd+shift+a",
      "action": "runSparcAnalysis"
    }
  ]
}
```

## 🎮 Keyboard Shortcuts

Add to Cursor's keyboard shortcuts:

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Cmd+Shift+M` | Search Memories | Search MemoryLink for context |
| `Cmd+Shift+S` | Store Memory | Save current selection |
| `Cmd+Shift+R` | Related Memories | Get related context |
| `Cmd+Shift+A` | SPARC Analysis | Run code analysis |
| `Cmd+Shift+D` | Debug with Memory | Start debug with context |

## 🔄 Automatic Workflows

### Auto-Documentation Flow

```javascript
// .cursor/workflows/auto-doc.js
async function autoDocument() {
  const file = getCurrentFile();
  const undocumented = await findUndocumentedFunctions(file);
  
  for (const func of undocumented) {
    // Search for similar functions in memory
    const similar = await searchMemories(`function similar to ${func.name}`);
    
    // Generate documentation using AI + memories
    const doc = await generateDocumentation(func, similar);
    
    // Store the documentation pattern
    await storeMemory({
      type: 'documentation-pattern',
      function: func.name,
      documentation: doc,
      tags: ['auto-generated', 'documentation']
    });
  }
}
```

### Test Generation Flow

```javascript
// .cursor/workflows/test-gen.js
async function generateTests() {
  const file = getCurrentFile();
  
  // Search for existing test patterns
  const testPatterns = await searchMemories('test patterns');
  
  // Generate tests using patterns
  const tests = await generateTestsWithPatterns(file, testPatterns);
  
  // Store successful test patterns
  await storeMemory({
    type: 'test-pattern',
    file,
    tests,
    coverage: await calculateCoverage(tests),
    tags: ['testing', 'auto-generated']
  });
}
```

## 🚨 Troubleshooting

### Common Issues and Solutions

1. **AI suggestions not using memories**
   ```bash
   # Verify memory integration
   curl http://localhost:8000/health
   
   # Check Cursor AI settings
   cat .cursor/ai-context.json
   ```

2. **Hooks not triggering**
   ```bash
   # Test hook registration
   node .cursor/hooks.js --test
   
   # Enable debug mode
   export CURSOR_DEBUG=true
   export MEMORYLINK_DEBUG=true
   ```

3. **Memory search not working**
   ```bash
   # Test memory API
   curl -X POST http://localhost:8000/api/memories/search \
     -H "Authorization: Bearer $MEMORYLINK_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"query": "test"}'
   ```

## 📚 Advanced Features

### Memory-Augmented Code Generation

```javascript
// Use memories to improve code generation
async function generateWithMemory(prompt) {
  // Search relevant memories
  const memories = await searchMemories(prompt);
  
  // Build enhanced context
  const context = buildContext(memories);
  
  // Generate code with memory context
  const enhancedPrompt = `
    ${prompt}
    
    Relevant context from memory:
    ${context}
    
    Follow patterns and decisions from the context.
  `;
  
  return await cursor.ai.generate(enhancedPrompt);
}
```

### Intelligent Refactoring

```javascript
// Refactor with consistency checking
async function refactorWithMemory(code, target) {
  // Get architectural decisions
  const architecture = await searchMemories('architecture decisions');
  
  // Get coding patterns
  const patterns = await searchMemories('code patterns');
  
  // Refactor maintaining consistency
  const refactored = await refactor(code, {
    target,
    constraints: architecture,
    patterns
  });
  
  // Store refactoring decision
  await storeMemory({
    type: 'refactoring',
    original: code,
    refactored,
    reason: target,
    tags: ['refactoring', 'architecture']
  });
  
  return refactored;
}
```

## 🔗 Related Documentation

- [VSCode Integration Guide](./vscode-integration.md)
- [Custom Rules Guide](./custom-rules.md)
- [Hooks & Automation](./hooks-automation.md)
- [API Documentation](./api.md)

---

*For more information, see the [main documentation](./README.md)*
# 📏 Custom Rules Guide

This guide explains how to create, configure, and use custom rules for MemoryLink automation in VSCode, Cursor, and other development environments.

## 📋 Overview

Custom rules define automated behaviors triggered by specific events or conditions in your development workflow. They enable intelligent memory capture, code generation, and workflow automation.

## 🎯 Rule Structure

### Basic Rule Format

```json
{
  "name": "rule-name",
  "description": "What this rule does",
  "enabled": true,
  "trigger": {
    "type": "event|pattern|condition",
    "value": "specific-trigger-value"
  },
  "conditions": [
    {
      "type": "condition-type",
      "operator": "equals|contains|matches|greater|less",
      "value": "expected-value"
    }
  ],
  "actions": [
    {
      "type": "action-type",
      "config": {
        "param1": "value1",
        "param2": "value2"
      }
    }
  ],
  "metadata": {
    "priority": 1,
    "tags": ["category", "type"],
    "cooldown": 5000
  }
}
```

## 🔧 Trigger Types

### Event Triggers

```json
{
  "trigger": {
    "type": "event",
    "value": "file.save|file.open|git.commit|test.run|debug.start"
  }
}
```

Available events:
- `file.save` - File saved
- `file.open` - File opened
- `file.close` - File closed
- `file.change` - File modified
- `git.commit` - Git commit
- `git.push` - Git push
- `git.pull` - Git pull
- `test.run` - Tests executed
- `test.pass` - Tests passed
- `test.fail` - Tests failed
- `debug.start` - Debug session started
- `debug.end` - Debug session ended
- `build.start` - Build started
- `build.complete` - Build completed

### Pattern Triggers

```json
{
  "trigger": {
    "type": "pattern",
    "value": "**/*.{js,ts}",
    "recursive": true
  }
}
```

Pattern examples:
- `**/*.js` - All JavaScript files
- `src/**/*.py` - Python files in src
- `**/test_*.py` - Test files
- `**/*.(spec|test).js` - Test/spec files

### Condition Triggers

```json
{
  "trigger": {
    "type": "condition",
    "expression": "file.lines > 500 && complexity > 10"
  }
}
```

## 📝 Condition Types

### File Conditions

```json
{
  "conditions": [
    {
      "type": "file.size",
      "operator": "greater",
      "value": 10000
    },
    {
      "type": "file.lines",
      "operator": "greater",
      "value": 500
    },
    {
      "type": "file.extension",
      "operator": "equals",
      "value": ".js"
    }
  ]
}
```

### Code Conditions

```json
{
  "conditions": [
    {
      "type": "code.complexity",
      "operator": "greater",
      "value": 10
    },
    {
      "type": "code.coverage",
      "operator": "less",
      "value": 80
    },
    {
      "type": "code.hasTests",
      "operator": "equals",
      "value": false
    }
  ]
}
```

### Time Conditions

```json
{
  "conditions": [
    {
      "type": "time.hour",
      "operator": "between",
      "value": [9, 17]
    },
    {
      "type": "time.dayOfWeek",
      "operator": "in",
      "value": ["Mon", "Tue", "Wed", "Thu", "Fri"]
    }
  ]
}
```

## 🎬 Action Types

### Memory Actions

```json
{
  "actions": [
    {
      "type": "memory.store",
      "config": {
        "key": "${file.name}_${timestamp}",
        "value": "${file.content}",
        "tags": ["auto-capture"],
        "ttl": 86400
      }
    },
    {
      "type": "memory.search",
      "config": {
        "query": "similar to ${file.name}",
        "limit": 5,
        "useForContext": true
      }
    }
  ]
}
```

### Code Actions

```json
{
  "actions": [
    {
      "type": "code.generate",
      "config": {
        "template": "test",
        "target": "${file.path}.test.js",
        "useMemories": true
      }
    },
    {
      "type": "code.refactor",
      "config": {
        "pattern": "optimize-loops",
        "preserveTests": true
      }
    }
  ]
}
```

### Command Actions

```json
{
  "actions": [
    {
      "type": "command.run",
      "config": {
        "command": "npx claude-flow sparc tdd '${file.path}'",
        "workingDir": "${workspace}",
        "timeout": 30000
      }
    },
    {
      "type": "command.spawn",
      "config": {
        "agent": "tester",
        "task": "generate tests for ${file.name}"
      }
    }
  ]
}
```

## 🚀 Complete Rule Examples

### Auto-Test Generation Rule

```json
{
  "name": "auto-generate-tests",
  "description": "Automatically generate tests for new functions",
  "enabled": true,
  "trigger": {
    "type": "event",
    "value": "file.save"
  },
  "conditions": [
    {
      "type": "file.extension",
      "operator": "in",
      "value": [".js", ".ts", ".py"]
    },
    {
      "type": "file.hasTests",
      "operator": "equals",
      "value": false
    },
    {
      "type": "code.functions.new",
      "operator": "greater",
      "value": 0
    }
  ],
  "actions": [
    {
      "type": "memory.search",
      "config": {
        "query": "test patterns for ${file.language}",
        "storeAs": "testPatterns"
      }
    },
    {
      "type": "code.generate",
      "config": {
        "template": "test",
        "useContext": ["testPatterns"],
        "target": "${file.dir}/__tests__/${file.name}.test${file.ext}"
      }
    },
    {
      "type": "memory.store",
      "config": {
        "key": "test-generation_${file.name}",
        "value": {
          "file": "${file.path}",
          "testsGenerated": true,
          "timestamp": "${timestamp}"
        },
        "tags": ["auto-test", "generated"]
      }
    }
  ],
  "metadata": {
    "priority": 5,
    "tags": ["testing", "automation"],
    "cooldown": 60000
  }
}
```

### Documentation Enforcement Rule

```json
{
  "name": "enforce-documentation",
  "description": "Ensure all public functions are documented",
  "enabled": true,
  "trigger": {
    "type": "event",
    "value": "file.save"
  },
  "conditions": [
    {
      "type": "code.undocumentedFunctions",
      "operator": "greater",
      "value": 0
    },
    {
      "type": "file.isPublicAPI",
      "operator": "equals",
      "value": true
    }
  ],
  "actions": [
    {
      "type": "code.analyze",
      "config": {
        "findUndocumented": true,
        "storeAs": "undocumented"
      }
    },
    {
      "type": "command.run",
      "config": {
        "command": "npx claude-flow sparc run docs-writer 'document ${undocumented}'"
      }
    },
    {
      "type": "notification.show",
      "config": {
        "message": "Added documentation for ${undocumented.count} functions",
        "type": "info"
      }
    }
  ]
}
```

### Performance Monitoring Rule

```json
{
  "name": "monitor-performance",
  "description": "Track performance degradation",
  "enabled": true,
  "trigger": {
    "type": "event",
    "value": "test.complete"
  },
  "conditions": [
    {
      "type": "test.performance.degraded",
      "operator": "equals",
      "value": true
    }
  ],
  "actions": [
    {
      "type": "memory.store",
      "config": {
        "key": "perf-degradation_${timestamp}",
        "value": {
          "metrics": "${test.metrics}",
          "comparison": "${test.comparison}",
          "file": "${file.path}"
        },
        "tags": ["performance", "degradation", "alert"]
      }
    },
    {
      "type": "command.spawn",
      "config": {
        "agent": "perf-analyzer",
        "task": "analyze performance degradation in ${file.path}"
      }
    },
    {
      "type": "git.createIssue",
      "config": {
        "title": "Performance degradation in ${file.name}",
        "body": "Performance tests show ${test.degradation}% decrease",
        "labels": ["performance", "automated"]
      }
    }
  ]
}
```

### Security Scanning Rule

```json
{
  "name": "security-scan",
  "description": "Scan for security vulnerabilities",
  "enabled": true,
  "trigger": {
    "type": "event",
    "value": "git.pre-commit"
  },
  "conditions": [
    {
      "type": "file.changed",
      "operator": "contains",
      "value": ["auth", "security", "crypto", "password"]
    }
  ],
  "actions": [
    {
      "type": "security.scan",
      "config": {
        "deep": true,
        "patterns": ["owasp-top-10", "cwe-top-25"]
      }
    },
    {
      "type": "conditional",
      "config": {
        "if": "security.issues.found",
        "then": [
          {
            "type": "git.blockCommit",
            "config": {
              "message": "Security issues found: ${security.issues}"
            }
          },
          {
            "type": "memory.store",
            "config": {
              "key": "security-blocked_${timestamp}",
              "value": "${security.report}",
              "tags": ["security", "blocked", "critical"]
            }
          }
        ]
      }
    }
  ]
}
```

## 🛠️ Rule Configuration Files

### VSCode Rules

Create `.vscode/memorylink-rules.json`:

```json
{
  "version": "2.0",
  "rules": [
    // Your rules here
  ],
  "global": {
    "enabled": true,
    "logLevel": "info",
    "maxConcurrent": 5,
    "timeout": 30000
  },
  "variables": {
    "projectName": "${workspaceFolderBasename}",
    "userName": "${env:USER}",
    "apiUrl": "${env:MEMORYLINK_API_URL}"
  }
}
```

### Cursor Rules

Create `.cursor/rules/memorylink.json`:

```json
{
  "version": "2.0",
  "extends": "../.vscode/memorylink-rules.json",
  "cursorSpecific": {
    "aiIntegration": true,
    "useMemoriesInChat": true,
    "autoSuggestFromMemories": true
  },
  "rules": [
    // Cursor-specific rules
  ]
}
```

## 📊 Rule Variables

Available variables for use in rules:

| Variable | Description | Example |
|----------|-------------|---------|
| `${file.path}` | Full file path | `/home/user/project/src/app.js` |
| `${file.name}` | File name without extension | `app` |
| `${file.ext}` | File extension | `.js` |
| `${file.dir}` | Directory path | `/home/user/project/src` |
| `${file.content}` | File content | `function main() {...}` |
| `${file.lines}` | Number of lines | `150` |
| `${workspace}` | Workspace root | `/home/user/project` |
| `${timestamp}` | Current timestamp | `1693526400000` |
| `${date}` | Current date | `2024-08-25` |
| `${time}` | Current time | `14:30:00` |
| `${user}` | Current user | `john.doe` |
| `${branch}` | Git branch | `feature/new-feature` |
| `${commit}` | Latest commit hash | `abc123def456` |

## 🔍 Rule Testing

### Test Individual Rules

```bash
# Test a specific rule
memorylink rules test "auto-generate-tests" --file src/app.js

# Dry run to see what would happen
memorylink rules dry-run --file src/app.js

# Debug rule execution
memorylink rules debug "enforce-documentation" --verbose
```

### Rule Validation

```javascript
// validate-rules.js
const { validateRules } = require('memorylink-sdk');

async function validateRuleFile(path) {
  const rules = require(path);
  
  const validation = await validateRules(rules);
  
  if (validation.errors.length > 0) {
    console.error('Validation errors:');
    validation.errors.forEach(err => {
      console.error(`  - ${err.rule}: ${err.message}`);
    });
    process.exit(1);
  }
  
  console.log('✓ All rules are valid');
}

validateRuleFile('./.vscode/memorylink-rules.json');
```

## 🎮 Rule Management CLI

```bash
# List all rules
memorylink rules list

# Enable/disable rules
memorylink rules enable "auto-generate-tests"
memorylink rules disable "enforce-documentation"

# Import/export rules
memorylink rules export > my-rules.json
memorylink rules import my-rules.json

# Rule statistics
memorylink rules stats

# Clear rule cache
memorylink rules clear-cache
```

## 📈 Advanced Rule Features

### Composite Rules

```json
{
  "name": "composite-workflow",
  "type": "composite",
  "rules": [
    {
      "ref": "security-scan",
      "continueOnFailure": false
    },
    {
      "ref": "auto-generate-tests",
      "parallel": true
    },
    {
      "ref": "enforce-documentation",
      "parallel": true
    }
  ],
  "aggregateResults": true
}
```

### Machine Learning Rules

```json
{
  "name": "ml-pattern-detection",
  "type": "ml-powered",
  "trigger": {
    "type": "event",
    "value": "file.save"
  },
  "mlConfig": {
    "model": "code-pattern-detector",
    "threshold": 0.85,
    "trainOnSuccess": true
  },
  "actions": [
    {
      "type": "ml.predict",
      "config": {
        "input": "${file.content}",
        "storeAs": "prediction"
      }
    },
    {
      "type": "conditional",
      "config": {
        "if": "prediction.confidence > 0.85",
        "then": [
          {
            "type": "memory.store",
            "config": {
              "key": "pattern_${prediction.type}",
              "value": "${prediction.details}"
            }
          }
        ]
      }
    }
  ]
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Rules not triggering**
   ```bash
   # Check rule status
   memorylink rules status "rule-name"
   
   # View rule logs
   memorylink rules logs "rule-name" --tail 50
   ```

2. **Performance issues**
   ```bash
   # Profile rule execution
   memorylink rules profile "rule-name"
   
   # Optimize rule conditions
   memorylink rules optimize
   ```

3. **Conflicts between rules**
   ```bash
   # Detect conflicts
   memorylink rules conflicts
   
   # Set rule priorities
   memorylink rules priority "rule-1" 10
   memorylink rules priority "rule-2" 5
   ```

## 🔗 Related Documentation

- [VSCode Integration](./vscode-integration.md)
- [Cursor Integration](./cursor-integration.md)
- [Hooks & Automation](./hooks-automation.md)
- [API Documentation](./api.md)

---

*For more information, see the [main documentation](./README.md)*
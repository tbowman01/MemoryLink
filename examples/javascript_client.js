#!/usr/bin/env node

/**
 * 🌐 MemoryLink JavaScript/Node.js Client Examples
 * Complete examples for integrating MemoryLink into JavaScript applications
 */

const https = require('https');
const http = require('http');

// ANSI colors for beautiful console output
const Colors = {
    GREEN: '\x1b[32m',
    BLUE: '\x1b[34m',
    PURPLE: '\x1b[35m',
    CYAN: '\x1b[36m',
    YELLOW: '\x1b[33m',
    RED: '\x1b[31m',
    BOLD: '\x1b[1m',
    END: '\x1b[0m'
};

class MemoryLinkError extends Error {
    constructor(message, status = null) {
        super(message);
        this.name = 'MemoryLinkError';
        this.status = status;
    }
}

/**
 * Production-ready MemoryLink JavaScript client
 * 
 * Features:
 * - Promise-based API
 * - Comprehensive error handling
 * - TypeScript-style JSDoc annotations
 * - Request timeout support
 * - Connection reuse
 */
class MemoryVaultClient {
    /**
     * Create a new MemoryLink client
     * @param {string} baseUrl - Base URL of the MemoryLink server
     * @param {Object} options - Configuration options
     * @param {number} options.timeout - Request timeout in milliseconds
     * @param {Object} options.headers - Default headers to send with requests
     */
    constructor(baseUrl = 'http://localhost:8000', options = {}) {
        this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
        this.timeout = options.timeout || 30000;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'User-Agent': 'MemoryLink-JS-Client/1.0',
            ...options.headers
        };
    }

    /**
     * Make HTTP request with error handling
     * @private
     */
    async _request(method, path, data = null) {
        const url = `${this.baseUrl}${path}`;
        const isHttps = url.startsWith('https:');
        const requestModule = isHttps ? https : http;

        return new Promise((resolve, reject) => {
            const urlObj = new URL(url);
            const options = {
                hostname: urlObj.hostname,
                port: urlObj.port,
                path: urlObj.pathname + urlObj.search,
                method: method.toUpperCase(),
                headers: { ...this.defaultHeaders },
                timeout: this.timeout
            };

            if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
                const jsonData = JSON.stringify(data);
                options.headers['Content-Length'] = Buffer.byteLength(jsonData);
                
                const req = requestModule.request(options, (res) => {
                    let responseData = '';
                    
                    res.on('data', (chunk) => {
                        responseData += chunk;
                    });
                    
                    res.on('end', () => {
                        try {
                            const parsed = responseData ? JSON.parse(responseData) : {};
                            
                            if (res.statusCode >= 200 && res.statusCode < 300) {
                                resolve(parsed);
                            } else {
                                reject(new MemoryLinkError(
                                    parsed.detail || parsed.error || `HTTP ${res.statusCode}`,
                                    res.statusCode
                                ));
                            }
                        } catch (err) {
                            reject(new MemoryLinkError(`Failed to parse response: ${err.message}`));
                        }
                    });
                });
                
                req.on('timeout', () => {
                    req.destroy();
                    reject(new MemoryLinkError(`Request timeout after ${this.timeout}ms`));
                });
                
                req.on('error', (err) => {
                    if (err.code === 'ECONNREFUSED') {
                        reject(new MemoryLinkError('Cannot connect to MemoryLink server. Is it running?'));
                    } else {
                        reject(new MemoryLinkError(`Network error: ${err.message}`));
                    }
                });
                
                req.write(jsonData);
                req.end();
                
            } else {
                const req = requestModule.request(options, (res) => {
                    let responseData = '';
                    
                    res.on('data', (chunk) => {
                        responseData += chunk;
                    });
                    
                    res.on('end', () => {
                        try {
                            const parsed = responseData ? JSON.parse(responseData) : {};
                            
                            if (res.statusCode >= 200 && res.statusCode < 300) {
                                resolve(parsed);
                            } else {
                                reject(new MemoryLinkError(
                                    parsed.detail || parsed.error || `HTTP ${res.statusCode}`,
                                    res.statusCode
                                ));
                            }
                        } catch (err) {
                            reject(new MemoryLinkError(`Failed to parse response: ${err.message}`));
                        }
                    });
                });
                
                req.on('timeout', () => {
                    req.destroy();
                    reject(new MemoryLinkError(`Request timeout after ${this.timeout}ms`));
                });
                
                req.on('error', (err) => {
                    if (err.code === 'ECONNREFUSED') {
                        reject(new MemoryLinkError('Cannot connect to MemoryLink server. Is it running?'));
                    } else {
                        reject(new MemoryLinkError(`Network error: ${err.message}`));
                    }
                });
                
                req.end();
            }
        });
    }

    /**
     * Check if the Memory Vault server is healthy
     * @returns {Promise<boolean>} True if server is healthy
     */
    async healthCheck() {
        try {
            await this._request('GET', '/health');
            return true;
        } catch (error) {
            return false;
        }
    }

    /**
     * Store a new memory in the vault
     * @param {string} content - The memory content
     * @param {Object} metadata - Optional metadata object
     * @returns {Promise<Object>} The stored memory object
     */
    async storeMemory(content, metadata = {}) {
        if (!content || typeof content !== 'string' || !content.trim()) {
            throw new MemoryLinkError('Memory content cannot be empty');
        }

        const payload = {
            content: content.trim(),
            metadata: metadata || {}
        };

        return await this._request('POST', '/memories/', payload);
    }

    /**
     * Search memories using semantic similarity
     * @param {string} query - Natural language search query
     * @param {Object} options - Search options
     * @param {number} options.limit - Maximum number of results (1-100)
     * @param {number} options.threshold - Similarity threshold (0.0-1.0)
     * @returns {Promise<Array>} Array of search results with similarity scores
     */
    async searchMemories(query, options = {}) {
        if (!query || typeof query !== 'string' || !query.trim()) {
            throw new MemoryLinkError('Search query cannot be empty');
        }

        const { limit = 10, threshold = 0.3 } = options;

        if (limit < 1 || limit > 100) {
            throw new MemoryLinkError('Limit must be between 1 and 100');
        }

        if (threshold < 0.0 || threshold > 1.0) {
            throw new MemoryLinkError('Threshold must be between 0.0 and 1.0');
        }

        const payload = {
            query: query.trim(),
            limit,
            threshold
        };

        return await this._request('POST', '/search/', payload);
    }

    /**
     * Retrieve all stored memories
     * @param {Object} options - Retrieval options
     * @param {number} options.limit - Maximum number of memories to return
     * @param {number} options.offset - Number of memories to skip
     * @returns {Promise<Array>} Array of memory objects
     */
    async getAllMemories(options = {}) {
        const { limit = 100, offset = 0 } = options;
        const queryParams = new URLSearchParams({ limit, offset }).toString();
        
        return await this._request('GET', `/memories/?${queryParams}`);
    }

    /**
     * Get a specific memory by ID
     * @param {string} memoryId - UUID of the memory
     * @returns {Promise<Object>} Memory object
     */
    async getMemoryById(memoryId) {
        if (!memoryId) {
            throw new MemoryLinkError('Memory ID is required');
        }

        return await this._request('GET', `/memories/${memoryId}`);
    }
}

/**
 * High-level wrapper for building intelligent applications
 */
class SmartMemoryApp {
    constructor(vaultClient) {
        this.vault = vaultClient;
    }

    /**
     * Add a note with automatic metadata enrichment
     */
    async addNote(title, content, tags = [], category = 'general') {
        const metadata = {
            type: 'note',
            title,
            tags: Array.isArray(tags) ? tags : [tags],
            category,
            created_at: new Date().toISOString(),
            word_count: content.split(/\s+/).length
        };

        const enrichedContent = `# ${title}\n\n${content}`;
        
        return await this.vault.storeMemory(enrichedContent, metadata);
    }

    /**
     * Add a web bookmark with metadata
     */
    async addBookmark(url, title, description = '', tags = []) {
        const metadata = {
            type: 'bookmark',
            url,
            title,
            tags: Array.isArray(tags) ? tags : [tags],
            bookmarked_at: new Date().toISOString()
        };

        const content = `# ${title}\n\n${description}\n\n**URL:** ${url}`;
        
        return await this.vault.storeMemory(content, metadata);
    }

    /**
     * Add a task or todo item
     */
    async addTask(task, priority = 'medium', dueDate = null, project = null) {
        const metadata = {
            type: 'task',
            priority,
            due_date: dueDate,
            project,
            status: 'pending',
            created_at: new Date().toISOString()
        };

        let content = `# Task: ${task}`;
        if (priority) content += `\n\n**Priority:** ${priority}`;
        if (dueDate) content += `\n**Due:** ${dueDate}`;
        if (project) content += `\n**Project:** ${project}`;

        return await this.vault.storeMemory(content, metadata);
    }

    /**
     * Intelligent search with context awareness
     */
    async smartSearch(query, context = {}) {
        const { contentType, limit = 10, includeContent = true } = context;

        let results = await this.vault.searchMemories(query, { limit: limit * 2 });

        // Filter by content type if specified
        if (contentType) {
            results = results.filter(result => 
                result.memory.metadata && result.memory.metadata.type === contentType
            );
        }

        // Limit results
        results = results.slice(0, limit);

        // Optionally include full content
        if (!includeContent) {
            results = results.map(result => ({
                ...result,
                memory: {
                    ...result.memory,
                    content: result.memory.content.substring(0, 200) + '...'
                }
            }));
        }

        return results;
    }

    /**
     * Get content statistics
     */
    async getStatistics() {
        try {
            const memories = await this.vault.getAllMemories({ limit: 1000 });
            
            const stats = {
                totalMemories: memories.length,
                byType: {},
                byCategory: {},
                recentActivity: 0
            };

            const oneWeekAgo = new Date();
            oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);

            memories.forEach(memory => {
                const metadata = memory.metadata || {};
                
                // Count by type
                const type = metadata.type || 'unknown';
                stats.byType[type] = (stats.byType[type] || 0) + 1;

                // Count by category
                const category = metadata.category || 'general';
                stats.byCategory[category] = (stats.byCategory[category] || 0) + 1;

                // Count recent activity
                if (memory.created_at && new Date(memory.created_at) > oneWeekAgo) {
                    stats.recentActivity++;
                }
            });

            return stats;
        } catch (error) {
            console.error('Failed to get statistics:', error);
            return null;
        }
    }
}

/**
 * Memory export utilities
 */
class MemoryExporter {
    constructor(vaultClient) {
        this.vault = vaultClient;
    }

    /**
     * Export memories as JSON
     */
    async exportAsJSON(filename = 'memories-export.json', options = {}) {
        const fs = require('fs').promises;
        const { limit = 1000, contentType = null } = options;

        try {
            let memories = await this.vault.getAllMemories({ limit });

            if (contentType) {
                memories = memories.filter(m => 
                    m.metadata && m.metadata.type === contentType
                );
            }

            const exportData = {
                exported_at: new Date().toISOString(),
                total_memories: memories.length,
                memories: memories
            };

            await fs.writeFile(filename, JSON.stringify(exportData, null, 2));
            console.log(`${Colors.GREEN}✅ Exported ${memories.length} memories to ${filename}${Colors.END}`);
            
            return filename;
        } catch (error) {
            console.error(`${Colors.RED}❌ Export failed: ${error.message}${Colors.END}`);
            throw error;
        }
    }

    /**
     * Export memories as Markdown
     */
    async exportAsMarkdown(filename = 'memories-export.md', options = {}) {
        const fs = require('fs').promises;
        const { limit = 1000, contentType = null } = options;

        try {
            let memories = await this.vault.getAllMemories({ limit });

            if (contentType) {
                memories = memories.filter(m => 
                    m.metadata && m.metadata.type === contentType
                );
            }

            let markdown = `# Memory Export\n\n`;
            markdown += `Exported on: ${new Date().toISOString()}\n`;
            markdown += `Total memories: ${memories.length}\n\n`;
            markdown += `---\n\n`;

            memories.forEach((memory, index) => {
                markdown += `## Memory ${index + 1}\n\n`;
                markdown += `**ID:** ${memory.id}\n`;
                markdown += `**Created:** ${memory.created_at}\n`;
                
                if (memory.metadata && Object.keys(memory.metadata).length > 0) {
                    markdown += `**Metadata:** ${JSON.stringify(memory.metadata, null, 2)}\n`;
                }
                
                markdown += `\n${memory.content}\n\n`;
                markdown += `---\n\n`;
            });

            await fs.writeFile(filename, markdown);
            console.log(`${Colors.GREEN}✅ Exported ${memories.length} memories to ${filename}${Colors.END}`);
            
            return filename;
        } catch (error) {
            console.error(`${Colors.RED}❌ Export failed: ${error.message}${Colors.END}`);
            throw error;
        }
    }
}

// Demo Functions

async function demoBasicUsage() {
    console.log(`${Colors.CYAN}🌐 JavaScript Client Basic Usage Demo${Colors.END}`);
    console.log('─'.repeat(50));

    const vault = new MemoryVaultClient();

    try {
        // Check connection
        const isHealthy = await vault.healthCheck();
        if (!isHealthy) {
            console.log(`${Colors.RED}❌ Cannot connect to MemoryLink server${Colors.END}`);
            return;
        }

        console.log(`${Colors.GREEN}✅ Connected to Memory Vault${Colors.END}`);

        // Store a memory
        console.log(`\n${Colors.YELLOW}📝 Storing a memory...${Colors.END}`);
        const memory = await vault.storeMemory(
            'React Context API provides a way to share state between components without prop drilling.',
            {
                topic: 'web_development',
                framework: 'react',
                concept: 'context_api',
                difficulty: 'intermediate'
            }
        );
        console.log(`   Stored memory with ID: ${memory.id.substring(0, 8)}...`);

        // Search for memories
        console.log(`\n${Colors.YELLOW}🔍 Searching for React state management...${Colors.END}`);
        const results = await vault.searchMemories('React state management patterns', { limit: 3 });

        results.forEach((result, index) => {
            console.log(`   ${index + 1}. Similarity: ${(result.similarity * 100).toFixed(1)}%`);
            console.log(`      Content: ${result.memory.content.substring(0, 80)}...`);
        });

    } catch (error) {
        console.error(`${Colors.RED}❌ Demo error: ${error.message}${Colors.END}`);
    }
}

async function demoSmartMemoryApp() {
    console.log(`\n${Colors.CYAN}🧠 Smart Memory App Demo${Colors.END}`);
    console.log('─'.repeat(50));

    const vault = new MemoryVaultClient();
    const app = new SmartMemoryApp(vault);

    try {
        if (!(await vault.healthCheck())) {
            console.log(`${Colors.RED}❌ Cannot connect to MemoryLink server${Colors.END}`);
            return;
        }

        // Add different types of content
        console.log(`${Colors.YELLOW}📚 Adding a note...${Colors.END}`);
        await app.addNote(
            'JavaScript Promises vs Async/Await',
            'Promises provide a cleaner way to handle asynchronous operations compared to callbacks. Async/await is syntactic sugar over promises that makes asynchronous code look synchronous.',
            ['javascript', 'async', 'promises'],
            'programming'
        );

        console.log(`${Colors.YELLOW}🔖 Adding a bookmark...${Colors.END}`);
        await app.addBookmark(
            'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises',
            'MDN: Using Promises',
            'Comprehensive guide to JavaScript promises from Mozilla Developer Network',
            ['javascript', 'documentation', 'promises']
        );

        console.log(`${Colors.YELLOW}✅ Adding a task...${Colors.END}`);
        await app.addTask(
            'Implement promise-based data fetching in the user dashboard',
            'high',
            '2024-01-20',
            'user-dashboard-v2'
        );

        // Smart search
        console.log(`\n${Colors.YELLOW}🎯 Smart search for async JavaScript...${Colors.END}`);
        const results = await app.smartSearch('asynchronous JavaScript patterns', {
            limit: 3,
            includeContent: false
        });

        results.forEach((result, index) => {
            const metadata = result.memory.metadata || {};
            const title = metadata.title || 'Untitled';
            const type = metadata.type || 'unknown';
            console.log(`   ${index + 1}. [${type.toUpperCase()}] ${title} (${(result.similarity * 100).toFixed(1)}%)`);
        });

        // Show statistics
        console.log(`\n${Colors.YELLOW}📊 Getting statistics...${Colors.END}`);
        const stats = await app.getStatistics();
        if (stats) {
            console.log(`   Total memories: ${stats.totalMemories}`);
            console.log(`   By type: ${JSON.stringify(stats.byType, null, 2)}`);
            console.log(`   Recent activity: ${stats.recentActivity} memories in the past week`);
        }

    } catch (error) {
        console.error(`${Colors.RED}❌ Demo error: ${error.message}${Colors.END}`);
    }
}

async function demoMemoryExport() {
    console.log(`\n${Colors.CYAN}📤 Memory Export Demo${Colors.END}`);
    console.log('─'.repeat(50));

    const vault = new MemoryVaultClient();
    const exporter = new MemoryExporter(vault);

    try {
        if (!(await vault.healthCheck())) {
            console.log(`${Colors.RED}❌ Cannot connect to MemoryLink server${Colors.END}`);
            return;
        }

        console.log(`${Colors.YELLOW}📄 Exporting memories as JSON...${Colors.END}`);
        await exporter.exportAsJSON('demo-export.json', { limit: 10 });

        console.log(`${Colors.YELLOW}📝 Exporting memories as Markdown...${Colors.END}`);
        await exporter.exportAsMarkdown('demo-export.md', { limit: 10 });

    } catch (error) {
        console.error(`${Colors.RED}❌ Export demo error: ${error.message}${Colors.END}`);
    }
}

async function demoErrorHandling() {
    console.log(`\n${Colors.CYAN}⚠️ Error Handling Demo${Colors.END}`);
    console.log('─'.repeat(50));

    // Test with invalid URL
    const vault = new MemoryVaultClient('http://localhost:9999'); // Wrong port

    try {
        await vault.healthCheck();
    } catch (error) {
        console.log(`${Colors.RED}Caught expected connection error: ${error.message}${Colors.END}`);
    }

    // Test with empty content
    const validVault = new MemoryVaultClient();
    
    try {
        await validVault.storeMemory(''); // Empty content
    } catch (error) {
        console.log(`${Colors.YELLOW}Caught validation error: ${error.message}${Colors.END}`);
    }
}

async function main() {
    console.log(`${Colors.BOLD}${Colors.PURPLE}`);
    console.log('🌐' + '═'.repeat(60) + '🌐');
    console.log('        MEMORYLINK JAVASCRIPT CLIENT EXAMPLES');
    console.log('          Complete Integration Demos');
    console.log('🌐' + '═'.repeat(60) + '🌐');
    console.log(`${Colors.END}`);

    try {
        await demoBasicUsage();
        await demoSmartMemoryApp();
        await demoMemoryExport();
        await demoErrorHandling();

        console.log(`\n${Colors.GREEN}🎉 All demos completed successfully!${Colors.END}`);
        console.log(`${Colors.CYAN}Ready to integrate MemoryLink into your JavaScript applications!${Colors.END}`);

    } catch (error) {
        console.error(`\n${Colors.RED}Demo suite failed: ${error.message}${Colors.END}`);
    }
}

// Export classes for use as module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        MemoryVaultClient,
        SmartMemoryApp,
        MemoryExporter,
        MemoryLinkError
    };
}

// Run demos if executed directly
if (require.main === module) {
    main().catch(console.error);
}
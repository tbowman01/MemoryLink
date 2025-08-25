# ❓ MemoryLink Frequently Asked Questions

> Quick answers to common Memory Keeper questions

## 🚀 Getting Started

### Q: What is MemoryLink exactly?

**A:** MemoryLink is a local-first, AI-powered personal memory system that lets you store and search through your knowledge using natural language. Think of it as a smart notebook that understands the meaning behind your notes, not just keywords.

### Q: How is this different from a regular database or note-taking app?

**A:** Traditional systems require exact keyword matches. MemoryLink uses AI embeddings to understand semantic similarity. For example, searching for "Python function decorators" will find notes about "function wrappers" or "decorator patterns" even if they don't contain your exact search terms.

### Q: Do I need technical knowledge to use MemoryLink?

**A:** Not at all! Run `make tutorial` for a guided setup experience. The gamified interface makes it fun for non-technical users, while developers get powerful API integration options.

### Q: Is my data private and secure?

**A:** Yes! MemoryLink runs entirely on your machine. Your memories are stored in a local PostgreSQL database. Only the text embeddings are sent to OpenAI for processing (no personal data leaves your computer except for the embedding generation).

## 🔧 Installation & Setup

### Q: What do I need to install MemoryLink?

**A:** You need:
- Docker and Docker Compose
- Python 3.8+ 
- Make utility
- OpenAI API key

The `make tutorial` command guides you through everything.

### Q: Why do I need an OpenAI API key?

**A:** MemoryLink uses OpenAI's text embedding models to understand the semantic meaning of your memories. This enables the intelligent search functionality. You can get a free API key at [platform.openai.com](https://platform.openai.com).

### Q: Can I use a different embedding provider instead of OpenAI?

**A:** Currently, MemoryLink is optimized for OpenAI embeddings, but the architecture supports custom embedding providers. Check the [Development Guide](./development.md) for implementation details.

### Q: The server won't start. What should I do?

**A:** Common solutions:
1. Make sure Docker is running: `docker --version`
2. Check if ports are available: `docker-compose down`
3. Verify your `.env` file has `OPENAI_API_KEY` set
4. Try a clean restart: `make cleanup` then `make start`

### Q: I get permission errors on Linux/Mac

**A:** You might need to make scripts executable:
```bash
chmod +x scripts/*.py
# or
sudo make start
```

## 💾 Using MemoryLink

### Q: What kind of content should I store in MemoryLink?

**A:** Anything you want to remember and find later:
- Meeting notes and project updates
- Learning materials and tutorials
- Code snippets and documentation
- Research findings and ideas
- Personal reflections and insights

### Q: How much content can I store?

**A:** MemoryLink can handle thousands of memories. Each memory can be up to ~100KB of text. The local PostgreSQL database can scale to gigabytes of content.

### Q: How does the semantic search work?

**A:** When you store a memory, MemoryLink creates a vector embedding (numerical representation) that captures its semantic meaning. When you search, it compares your query's embedding with stored embeddings to find the most similar content.

### Q: Why don't I see exact matches for my search terms?

**A:** MemoryLink prioritizes semantic similarity over exact keyword matching. If you search for "database performance" and have notes about "SQL optimization," MemoryLink will find the connection even without exact word matches.

### Q: Can I search by metadata or tags?

**A:** Currently, MemoryLink focuses on content-based semantic search. Metadata filtering is on the roadmap. You can include important metadata in the content itself for now.

### Q: How accurate is the search?

**A:** Search accuracy depends on:
- Content quality and detail
- Similarity threshold (lower = more results, higher = more precise)
- How well your query describes what you're looking for

Typical accuracy is 80-90% for well-described queries.

## 🎮 Gamification & Interface

### Q: What are achievements and how do I unlock them?

**A:** Achievements are unlocked as you use MemoryLink:
- **Vault Keeper**: Start the server (`make start`)
- **Memory Scribe**: Add your first memories (`make add_sample`)
- **Vault Explorer**: Perform semantic search (`make search`)
- **Integration Master**: Complete the full tutorial
- **Groove Master**: Find the dance easter egg (`make dance`)

### Q: What do the different levels mean?

**A:** Your Memory Keeper level increases with achievements:
- Level 1: Memory Apprentice (getting started)
- Level 2: Vault Keeper (server running)
- Level 3: Memory Scribe (storing memories)
- Level 4: Vault Explorer (searching memories)
- Level 5+: Memory Keeper Master (full integration)

### Q: Can I use MemoryLink without the gamification?

**A:** Absolutely! The API works independently. Just use direct HTTP requests or the Python/JavaScript clients shown in the [API documentation](./api.md).

### Q: What's the point of the gamification?

**A:** It makes learning fun and guides you through all features systematically. Many users find the quest structure more engaging than traditional documentation.

## 🔌 Integration & Development

### Q: How do I integrate MemoryLink into my application?

**A:** MemoryLink provides a REST API. Check the [API Reference](./api.md) for complete details. Basic integration:

```python
import requests

# Store a memory
requests.post('http://localhost:8000/memories/', json={
    'content': 'Your memory content',
    'metadata': {'source': 'my_app'}
})

# Search memories
results = requests.post('http://localhost:8000/search/', json={
    'query': 'what you are looking for'
}).json()
```

### Q: Can I build a web interface for MemoryLink?

**A:** Yes! MemoryLink provides a complete REST API. Build any frontend you want - React, Vue, plain JavaScript, mobile apps, etc. The API supports CORS for web applications.

### Q: How do I deploy MemoryLink for production use?

**A:** Check the [Development Guide](./development.md) for production deployment options including:
- Docker Compose with proper security
- Kubernetes deployment
- Environment configuration
- Monitoring and logging

### Q: Can multiple users share the same MemoryLink instance?

**A:** Currently, MemoryLink is designed for single-user personal use. Multi-user support with authentication and data isolation is planned for future versions.

## ⚡ Performance & Troubleshooting

### Q: MemoryLink feels slow. How can I improve performance?

**A:** Performance optimization tips:
1. Use specific search queries instead of vague ones
2. Set appropriate similarity thresholds
3. Limit result counts to what you need
4. Ensure Docker has adequate RAM allocated (4GB recommended)
5. Consider SSD storage for database

### Q: I'm getting timeout errors during search

**A:** Search timeouts usually indicate:
- OpenAI API rate limiting (wait a few minutes)
- Large database with many memories (normal, but takes time)
- Network connectivity issues
- Server overload

Try increasing request timeouts or reducing search result limits.

### Q: Can I back up my MemoryLink data?

**A:** Yes! Your data is stored in PostgreSQL. Options:
1. **Docker volumes**: `docker-compose down` preserves data
2. **Database backup**: Use `pg_dump` to create SQL backups
3. **Full backup**: Copy the entire project directory
4. **API export**: Write a script to export all memories via API

### Q: I accidentally deleted important memories. Can I recover them?

**A:** If you used `make cleanup`, the data is permanently deleted. Always back up important data! For future protection:
- Regular database backups
- Export important memories to files
- Use version control for your MemoryLink setup

### Q: The search results don't seem relevant

**A:** Try these search optimization techniques:
- Use more descriptive queries: "Python web framework best practices" vs "Python web"
- Lower the similarity threshold for broader results
- Include context: "machine learning classification algorithms for beginners"
- Check that your stored content has enough detail

## 🔒 Security & Privacy

### Q: What data does MemoryLink send to external services?

**A:** Only the text content is sent to OpenAI for embedding generation. No metadata, search queries, or personal information is transmitted. The generated embeddings are stored locally.

### Q: Can I use MemoryLink completely offline?

**A:** MemoryLink needs internet connection for:
- Initial embedding generation (when storing memories)
- OpenAI API calls for new content

Once embeddings are generated, searching works offline. Consider self-hosted embedding solutions for complete offline operation.

### Q: How do I secure MemoryLink for production use?

**A:** Production security checklist:
- Use HTTPS with proper SSL certificates
- Implement API key authentication
- Configure CORS appropriately
- Use environment variables for secrets
- Regular security updates
- Firewall configuration

See [Development Guide](./development.md) for detailed security setup.

### Q: Can I encrypt my stored memories?

**A:** Currently, memories are stored in plain text in PostgreSQL. Database-level encryption and application-level encryption are planned features. For now, use disk encryption (BitLocker, FileVault, LUKS) to protect data at rest.

## 🔄 Updates & Maintenance

### Q: How do I update MemoryLink to a new version?

**A:** Update process:
1. Backup your data first!
2. Pull latest changes: `git pull origin main`
3. Rebuild containers: `docker-compose build`
4. Restart services: `make start`
5. Run any database migrations if needed

### Q: Will my data be preserved during updates?

**A:** Yes, as long as you don't run `make cleanup`. Docker volumes persist data between container updates. Always backup before major version updates.

### Q: How do I contribute to MemoryLink development?

**A:** We welcome contributions! See the [Development Guide](./development.md) for:
- Setting up development environment
- Code style guidelines
- Testing requirements
- Pull request process

## 🛠️ Advanced Usage

### Q: Can I customize the similarity threshold for different types of content?

**A:** Yes! Each search request can specify a custom threshold:
- Higher threshold (0.7-0.9): More precise, fewer results
- Lower threshold (0.2-0.5): Broader, more results
- Experiment to find what works best for your content

### Q: How do I bulk import existing notes into MemoryLink?

**A:** Write a script to process your existing files:

```python
import requests
import os

for file in os.listdir('my_notes'):
    with open(f'my_notes/{file}', 'r') as f:
        content = f.read()
        
    requests.post('http://localhost:8000/memories/', json={
        'content': content,
        'metadata': {'source': 'imported', 'filename': file}
    })
```

### Q: Can I export my memories to other formats?

**A:** Yes! Use the API to retrieve all memories and export:

```python
import json
import requests

memories = requests.get('http://localhost:8000/memories/').json()

# Export as JSON
with open('memories_backup.json', 'w') as f:
    json.dump(memories, f, indent=2)

# Export as Markdown
with open('memories_export.md', 'w') as f:
    for memory in memories:
        f.write(f"# {memory['metadata'].get('title', 'Memory')}\n\n")
        f.write(f"{memory['content']}\n\n")
        f.write("---\n\n")
```

## 📊 Analytics & Insights

### Q: Can I see statistics about my memory usage?

**A:** Basic statistics are available through `make status`. For detailed analytics, you can query the API:

```python
import requests
from collections import Counter

memories = requests.get('http://localhost:8000/memories/').json()

# Count memories by topic
topics = Counter(m['metadata'].get('topic', 'Unknown') for m in memories)
print(f"Total memories: {len(memories)}")
print(f"Topics: {dict(topics)}")
```

### Q: How can I identify gaps in my knowledge base?

**A:** Try searching for topics you know you should have information about. If results are sparse or irrelevant, you might need to add more content in those areas.

---

## 🤔 Still Have Questions?

**Can't find your answer here?** 

- Check the [API Reference](./api.md) for technical details
- Read the [Development Guide](./development.md) for advanced topics  
- Open an issue on GitHub for bugs or feature requests
- Start a discussion for general questions

**Remember**: `make help` shows all available commands, and `make tutorial` provides a guided walkthrough of all features!

---

<div align="center">

*Happy Memory Keeping! 🧠✨*

</div>
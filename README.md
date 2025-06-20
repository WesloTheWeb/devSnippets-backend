# DevSnippets Backend

> Semantic code search API that helps developers find and organize code snippets using natural language queries.

## 🎯 Project Overview

DevSnippets Backend is a FastAPI-powered REST API that enables intelligent code search using AI-powered semantic similarity. Users can upload code snippets and search through them using natural language queries like "how to sort an array" to find relevant code regardless of exact keyword matches.

For the front-end portion, [devSnippets - FrontEnd](https://github.com/WesloTheWeb/devSnippets)

## 🚀 Tech Stack

### **Currently Implemented**
- **FastAPI** - Modern Python web framework with automatic API documentation
- **PostgreSQL** - Production-ready relational database (via Supabase)
- **SQLAlchemy** - Python SQL toolkit and ORM
- **Sentence Transformers** - AI model for semantic text embeddings
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - Lightning-fast ASGI server

### **Planned Implementation** 
- **Vector Database** (Weaviate/Pinecone) - Dedicated vector storage for improved semantic search
- **Docker** - Containerization for easy deployment
- **GraphQL** - Alternative query interface (currently REST only)

### **Frontend** *(Separate Repository)*
[devSnippets - FrontEnd](https://github.com/WesloTheWeb/devSnippets)
- **Angular 18** - Modern TypeScript frontend framework
- **RxJS** - Reactive programming for HTTP operations

## 🛣️ Roadmap

### Phase 1 ✅ (Current)
- [x] FastAPI backend with PostgreSQL
- [x] Basic CRUD operations for snippets
- [x] AI-powered semantic search
- [x] RESTful API design
- [x] Auto-generated API documentation

### Phase 2 🔄 (In Progress)
- [ ] Angular frontend integration
- [ ] Advanced search filters
- [ ] User authentication
- [ ] Rate limiting

### Phase 3 📋 (Planned)
- [ ] Dedicated vector database (Weaviate/Pinecone)
- [ ] Docker containerization
- [ ] GraphQL API
- [ ] Advanced analytics

## ⚡ Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL database (or Supabase account)

### 1. Clone and Setup
```bash
git clone https://github.com/WesloTheWeb/devsnippets-backend.git
cd devsnippets-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the root directory:
```bash
DATABASE_URL=postgresql://username:password@host:port/database
```

**Example with Supabase:**
```bash
DATABASE_URL=postgresql://postgres:your_password@db.your_project.supabase.co:5432/postgres
```

### 3. Run the Server
```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API Server:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

## 📚 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/snippets` | Create a new code snippet |
| `GET` | `/api/snippets` | Retrieve all snippets (paginated) |
| `GET` | `/api/snippets/{id}` | Get specific snippet by ID |
| `PUT` | `/api/snippets/{id}` | Update an existing snippet |
| `DELETE` | `/api/snippets/{id}` | Delete a snippet |
| `POST` | `/api/search` | Semantic search through snippets |
| `GET` | `/api/languages` | Get list of available programming languages |

## 🔍 Usage Examples

### Create a Code Snippet
```bash
curl -X POST "http://localhost:8000/api/snippets" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Quick Sort Algorithm",
    "description": "Efficient divide-and-conquer sorting algorithm",
    "code": "def quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quicksort(left) + middle + quicksort(right)",
    "language": "python",
    "tags": ["sorting", "algorithm", "recursion"]
  }'
```

### Semantic Search
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how to arrange numbers in ascending order",
    "limit": 5
  }'
```

**The AI will find sorting algorithms even though the query doesn't contain the word "sort"!**

## 🧠 How Semantic Search Works

1. **Text Embedding**: When snippets are created, the AI model converts the code and description into numerical vectors (embeddings)
2. **Query Processing**: Search queries are converted into the same vector space
3. **Similarity Calculation**: Cosine similarity finds the most relevant code snippets
4. **Ranked Results**: Results are returned sorted by relevance score

**Example**: Searching for "iterate through items" will find:
- `for` loops
- `while` loops  
- `forEach` methods
- Any iteration-related code, regardless of exact keywords

## 🗄️ Database Schema

### Snippets Table
```sql
CREATE TABLE snippets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    code TEXT NOT NULL,
    language VARCHAR(50) NOT NULL,
    tags JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding JSON  -- AI-generated vectors stored as JSON array
);
```

## 🔧 Development

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Formatting
```bash
# Install formatting tools
pip install black isort

# Format code
black .
isort .
```

### Database Migrations
```bash
# Tables are auto-created on startup
# For manual migration:
python -c "from app.services.database import create_tables; create_tables()"
```

## 🚀 Deployment

### Environment Variables
```bash
DATABASE_URL=postgresql://...
PORT=8000
ENVIRONMENT=production
```

### Docker (Coming Soon)
```dockerfile
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```


- [ ] Deployment to cloud platforms


## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Further Documentation

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent Python web framework
- [Sentence Transformers](https://www.sbert.net/) for semantic text embeddings
- [Supabase](https://supabase.com/) for managed PostgreSQL hosting

---

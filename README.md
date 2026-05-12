# SafeTalk 🔒

A modern, secure messaging application featuring end-to-end encryption with asymmetric key exchange and symmetric encryption. SafeTalk ensures that only the intended recipients can read your messages through cryptographic security protocols.

## 🌟 Features

### Security
- **End-to-End Encryption**: Messages encrypted with AES-256-GCM before transmission
- **X25519 Key Exchange**: Elliptic curve cryptography for secure key establishment
- **Authentication**: JWT-based token authentication with Argon2 password hashing
- **Data Integrity**: GCM mode ensures message authenticity and tamper detection

### Application
- **Real-time Messaging**: WebSocket-based instant messaging
- **User Management**: Registration, login, and session management
- **Message History**: Persistent message storage with encryption
- **Responsive UI**: Modern React interface with Tailwind CSS styling
- **Type Safety**: Full TypeScript support on the frontend

## 🏗️ Architecture

### Backend Architecture
```
FastAPI Server
├── Authentication (JWT + OAuth2)
├── WebSocket Real-time Chat
├── Encryption/Decryption Pipeline
├── Key Exchange Management
├── Database (SQLAlchemy ORM)
└── Message Storage & Retrieval
```

### Frontend Architecture
```
React Application
├── Login/Auth Pages
├── Chat Interface
├── Message Management
├── User Navigation
└── Responsive Components (HeroUI)
```

### Security Flow
```
User A                              User B
  ↓                                   ↓
Generate X25519 Keypair       Generate X25519 Keypair
  ↓                                   ↓
Exchange Public Keys ←────────────────→
  ↓                                   ↓
Perform ECDH Exchange ←────────────────→
  ↓                                   ↓
Derive Shared Secret
  ↓                                   ↓
Encrypt with AES-GCM          Send Encrypted Message
  ↓                                   ↓
Send Ciphertext ──────────────────────→ Decrypt with Shared Key
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.136.1 (Python)
- **Database**: SQLAlchemy 2.0.49 with ORM
- **Authentication**: JWT (python-jose), Argon2 password hashing
- **Cryptography**: 
  - cryptography (for X25519 key exchange)
  - pycryptodome (for AES-GCM encryption)
  - ECDSA for digital signatures
- **Real-time**: WebSockets 16.0
- **API**: CORS-enabled REST endpoints
- **Environment**: python-dotenv for configuration

### Frontend
- **Framework**: React 19.2.6 with React Router 7.15.0
- **Language**: TypeScript 5.9.3
- **Styling**: TailwindCSS 4.2.2 with Tailwind Animate
- **UI Components**: HeroUI 3.0.4, React Aria Components 1.17.0
- **HTTP Client**: Axios 1.16.0
- **Build Tool**: Vite 8.0.3
- **Server**: React Router Node server

## 📋 Project Structure

```
safeTalk/
├── main.py                          # FastAPI application entry point
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables
│
├── client/                          # Client session management
│   ├── __init__.py
│   └── session.py                   # Session handling
│
├── crypto/                          # Cryptographic operations
│   ├── __init__.py
│   ├── encryption.py                # AES-GCM encryption/decryption
│   ├── key_exchange.py              # X25519 key exchange
│   ├── key_derivation.py            # Key derivation functions
│   └── test_crypto.py               # Crypto unit tests
│
├── models/                          # Database models
│   ├── __init__.py
│   └── db.py                        # SQLAlchemy models (User, Message)
│
├── server/                          # Server logic
│   ├── __init__.py
│   ├── auth.py                      # Authentication & JWT
│   ├── key_store.py                 # Key management
│   └── router.py                    # WebSocket & messaging router
│
├── tests/                           # Test suites
│   ├── test_crypto.py               # Crypto tests
│   ├── test_sandra.py               # Integration tests
│   └── test_ziad.py                 # Additional tests
│
└── frontend/                        # React TypeScript application
    ├── package.json                 # NPM dependencies
    ├── tsconfig.json                # TypeScript configuration
    ├── vite.config.ts               # Vite build configuration
    ├── react-router.config.ts       # React Router config
    ├── Dockerfile                   # Frontend Docker image
    │
    ├── app/                         # Application layout
    │   ├── root.tsx                 # Root layout component
    │   ├── app.css                  # Global styles
    │   ├── routes.ts                # Route definitions
    │   ├── routes/                  # Page components
    │   │   ├── home.tsx
    │   │   ├── login.tsx
    │   │   └── logout.tsx
    │   ├── webpages/                # Full page components
    │   │   ├── Login.tsx
    │   │   ├── welcome.tsx
    │   │   └── fragments/           # Reusable page fragments
    │   │       └── Loading.tsx
    │   ├── Model/                   # Data models/types
    │   │   ├── ChatPreview.ts
    │   │   └── User.ts
    │   └── CSS/                     # Component styles
    │       └── Universal.css
    │
    ├── components/                  # Reusable components
    │   ├── application/             # App-specific components
    │   │   └── app-navigation/      # Navigation & sidebar
    │   │       ├── config.ts
    │   │       ├── base-components/
    │   │       └── sidebar-navigation/
    │   │
    │   ├── base/                    # Base UI components
    │   │   ├── avatar/              # Avatar component
    │   │   ├── badges/              # Badge components
    │   │   ├── buttons/             # Button components
    │   │   ├── radio-buttons/       # Radio button components
    │   │   └── tooltip/             # Tooltip component
    │   │
    │   └── foundations/             # Design foundation components
    │       ├── dot-icon.tsx
    │       └── logo/                # Logo variants
    │
    ├── hooks/                       # React custom hooks
    │   └── use-breakpoint.ts        # Responsive breakpoint hook
    │
    ├── utils/                       # Utility functions
    │   ├── cx.ts                    # Class merge utility
    │   └── is-react-component.ts    # Component type checking
    │
    └── public/                      # Static assets
        └── images/
            └── assets/
```

## 🚀 Getting Started

### Prerequisites
- **Python** 3.9+ (Backend)
- **Node.js** 18+ (Frontend)
- **npm** or **yarn** (Frontend package manager)
- **SQLite** (default database) or configure DATABASE_URL in .env

### Backend Setup

1. **Clone the repository**
   ```bash
   cd /Users/sandraremon/Desktop/safeTalk
   ```

2. **Create Python virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables** (create `.env` file)
   ```env
   SECRET_KEY=your-secret-key-here-change-in-production
   DATABASE_URL=sqlite:///./safetalk.db
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Run the backend server**
   ```bash
   uvicorn main:app --reload
   ```
   Server will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run development server**
   ```bash
   npm run dev
   ```
   Application will be available at `http://localhost:5173`

4. **Build for production**
   ```bash
   npm run build
   ```

5. **Run production build**
   ```bash
   npm start
   ```

## 📡 API Endpoints

### Authentication Endpoints
```
POST   /login              - User login with credentials
POST   /register           - Create new user account
GET    /verify-token       - Verify JWT token validity
```

### Key Management Endpoints
```
POST   /key/upload         - Upload public key
GET    /key/{username}     - Retrieve user's public key
```

### WebSocket Endpoints
```
WS     /ws                 - WebSocket connection for real-time messaging
```

### Message Endpoints
```
GET    /messages/{user_id} - Retrieve message history
POST   /messages           - Send encrypted message
```

## 🔐 Cryptography Details

### Key Exchange (X25519)
- **Algorithm**: Elliptic Curve Diffie-Hellman (X25519)
- **Key Size**: 32 bytes (256 bits)
- **Use Case**: Establishing shared secrets between users
- **Implementation**: `crypto/key_exchange.py`

### Encryption (AES-256-GCM)
- **Algorithm**: Advanced Encryption Standard in Galois/Counter Mode
- **Key Size**: 32 bytes (256 bits)
- **Nonce Size**: 12 bytes (96 bits)
- **Authentication Tag**: 16 bytes (128 bits)
- **Format**: `[nonce(12) || ciphertext || tag(16)]`
- **Use Case**: Encrypting message content
- **Implementation**: `crypto/encryption.py`

### Password Hashing
- **Algorithm**: Argon2 (memory-hard)
- **Use Case**: Securely storing user passwords
- **Library**: passlib with argon2-cffi

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Suite
```bash
pytest tests/test_crypto.py          # Cryptography tests
pytest test_sandra.py                 # Integration tests
pytest test_ziad.py                   # Additional tests
```

### Test Coverage
The project includes unit tests for:
- AES-GCM encryption/decryption round-trips
- X25519 key exchange and ECDH computation
- Authentication token generation and validation
- WebSocket message handling
- Database operations

## 🐳 Docker Deployment

### Frontend Docker Build
```bash
cd frontend
docker build -t safetalk-frontend .
docker run -p 3000:3000 safetalk-frontend
```

### Backend Docker Setup (Optional)
Create a `Dockerfile` in the root directory:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t safetalk-backend .
docker run -p 8000:8000 safetalk-backend
```

## 🔄 Development Workflow

1. **Feature Development**
   - Create a new branch for your feature
   - Implement changes in backend (Python) and/or frontend (TypeScript)
   - Add tests for new functionality
   - Update documentation

2. **Code Standards**
   - Backend: Follow PEP 8 Python style guide
   - Frontend: Use TypeScript strict mode
   - Both: Use meaningful commit messages

3. **Testing Before Commit**
   ```bash
   # Backend
   pytest
   
   # Frontend
   npm run typecheck
   npm run build
   ```

## 🐛 Troubleshooting

### Backend Issues

**"ModuleNotFoundError" for crypto modules**
- Ensure you're in the correct directory
- Verify virtual environment is activated
- Run `pip install -r requirements.txt`

**Database connection errors**
- Check DATABASE_URL in `.env`
- Ensure SQLite file path is writable
- Verify database migration ran successfully

**WebSocket connection failed**
- Verify backend is running on correct port
- Check CORS configuration in main.py
- Ensure JWT token is valid in query parameters

### Frontend Issues

**Port 5173 already in use**
```bash
npm run dev -- --port 3000
```

**Build errors with TypeScript**
```bash
npm run typecheck
tsc --noEmit
```

**Component import errors**
- Verify component paths are correct
- Check that files are saved
- Restart dev server

## 📝 Environment Variables

### Backend (.env)
```env
# Security
SECRET_KEY=your-256-bit-secret-key

# Database
DATABASE_URL=sqlite:///./safetalk.db

# JWT Configuration
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
DEBUG=true
```

## 🔒 Security Considerations

1. **Secret Management**
   - Never commit `.env` file to version control
   - Use strong SECRET_KEY (at least 32 characters)
   - Rotate secrets periodically

2. **HTTPS in Production**
   - Deploy backend behind HTTPS proxy
   - Use WSS (WebSocket Secure) for real-time connections
   - Set secure CORS policies

3. **Password Security**
   - Passwords hashed with Argon2
   - Never transmit passwords in plaintext
   - Enforce minimum password requirements

4. **API Security**
   - JWT tokens expire after 30 minutes
   - CORS restricted in production
   - Rate limiting recommended
   - SQL injection protected via SQLAlchemy ORM

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Router Documentation](https://reactrouter.com/)
- [Cryptography Library Docs](https://cryptography.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [TailwindCSS Documentation](https://tailwindcss.com/)

## 📄 License

This project is provided as-is for educational and development purposes.

## 👥 Contributors

- Sandra Remon
- Ziad
- shimaa
- mina

## 🤝 Contributing

Contributions are welcome! Please ensure:
1. Code follows project style guidelines
2. Tests are added for new features
3. Documentation is updated
4. Commit messages are descriptive

## 📞 Support

For issues or questions, please refer to the troubleshooting section or review the source code comments for implementation details.

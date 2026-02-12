#!/bin/bash

echo "🚀 AI ClassGuard Pro - Setup Script"
echo "===================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check Node version
node_version=$(node --version 2>&1)
echo "✓ Node version: $node_version"

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your actual API keys!"
fi

# Setup frontend .env
if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend .env file..."
    cp frontend/.env.example frontend/.env
fi

# Setup agent .env
if [ ! -f agent/.env ]; then
    echo "📝 Creating agent .env file..."
    cp agent/.env.example agent/.env
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your Gemini API key"
echo "2. Start backend: source venv/bin/activate && python backend/app.py"
echo "3. Start frontend: cd frontend && npm run dev"
echo "4. Start agent on student computers: cd agent && python core/agent.py"
echo ""
echo "🎉 Happy coding!"

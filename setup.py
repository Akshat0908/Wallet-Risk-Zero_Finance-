#!/usr/bin/env python3
"""
Setup script for Compound Protocol Wallet Risk Scoring System
"""

import os
import subprocess
import sys

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def create_env_file():
    """Create .env file if it doesn't exist"""
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return
    
    print("🔧 Creating .env file...")
    try:
        with open('env.example', 'r') as example_file:
            example_content = example_file.read()
        
        with open('.env', 'w') as env_file:
            env_file.write(example_content)
        
        print("✅ .env file created from env.example")
        print("⚠️  Please edit .env file and add your API keys")
    except FileNotFoundError:
        print("❌ env.example file not found")
        sys.exit(1)

def check_env_file():
    """Check if .env file has been configured"""
    if not os.path.exists('.env'):
        print("❌ .env file not found. Run setup again.")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
    
    if 'your_etherscan_api_key_here' in content or 'your_alchemy_api_key_here' in content:
        print("⚠️  Please update .env file with your actual API keys")
        return False
    
    print("✅ .env file appears to be configured")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Compound Protocol Wallet Risk Scoring System")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create .env file
    create_env_file()
    
    # Check configuration
    configured = check_env_file()
    
    print("\n" + "=" * 60)
    if configured:
        print("✅ Setup completed successfully!")
        print("🎯 You can now run: python3 main.py")
    else:
        print("⚠️  Setup completed, but API keys need to be configured")
        print("📝 Edit .env file with your API keys, then run: python3 main.py")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 
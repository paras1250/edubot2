#!/usr/bin/env python3
"""
Simple test script to verify EduBot setup
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import flask
        print(f"✅ Flask: {flask.__version__}")
    except ImportError:
        print("❌ Flask not found. Run: pip install -r requirements.txt")
        return False
    
    try:
        import pymysql
        print(f"✅ PyMySQL: {pymysql.__version__}")
    except ImportError:
        print("❌ PyMySQL not found. Run: pip install -r requirements.txt")
        return False
    
    try:
        from app import create_app
        print("✅ App module imports successfully")
    except ImportError as e:
        print(f"❌ App import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test if Flask app can be created"""
    print("\n🏗️  Testing app creation...")
    
    try:
        from app import create_app
        app = create_app()
        print("✅ Flask app created successfully")
        print(f"✅ App name: {app.name}")
        print(f"✅ Debug mode: {app.debug}")
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n⚙️  Testing configuration...")
    
    try:
        from config.config import config
        dev_config = config['development']
        print("✅ Configuration loaded successfully")
        print(f"✅ Database URI configured: {'SQLALCHEMY_DATABASE_URI' in dir(dev_config)}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_models():
    """Test if models can be imported"""
    print("\n📊 Testing models...")
    
    try:
        from app.models.user import User
        from app.models.faculty import Faculty
        from app.models.chat_log import ChatLog
        print("✅ All main models import successfully")
        return True
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🤖 EduBot Setup Verification")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_config,
        test_models,
        test_app_creation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"\n❌ Test failed: {test.__name__}")
    
    print("\n" + "=" * 40)
    print(f"📈 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! EduBot is ready to run.")
        print("\n🚀 To start the application, run:")
        print("   python run.py")
        print("\n🌐 Then visit: http://127.0.0.1:5000")
    else:
        print("⚠️  Some tests failed. Please check the setup.")
        print("\n📋 Setup checklist:")
        print("   1. Install Python 3.8+")
        print("   2. Create virtual environment")
        print("   3. Run: pip install -r requirements.txt")
        print("   4. Setup MySQL database")
        print("   5. Configure .env file")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

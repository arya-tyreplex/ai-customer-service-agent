#!/usr/bin/env python3
"""
Deployment script for the AI Customer Service Agent.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    print(f"🚀 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Command failed: {result.stderr}")
        sys.exit(1)
    return result

def deploy_docker():
    """Deploy using Docker."""
    print("🐳 Deploying with Docker...")
    
    # Build image
    run_command("docker build -t customer-service-agent:latest .")
    
    # Run container
    run_command("docker run -d --name customer-agent -p 8000:8000 -e OPENAI_API_KEY=$OPENAI_API_KEY customer-service-agent:latest")
    
    print("✅ Docker deployment completed!")

def deploy_serverless():
    """Deploy using Serverless Framework."""
    print("⚡ Deploying with Serverless...")
    
    # Install serverless if not present
    run_command("npm list -g serverless || npm install -g serverless")
    
    # Deploy to AWS
    run_command("cd serverless && serverless deploy")
    
    print("✅ Serverless deployment completed!")

def deploy_fastapi():
    """Deploy FastAPI application."""
    print("🚀 Deploying FastAPI application...")
    
    # Install dependencies
    run_command("pip install fastapi uvicorn")
    
    # Start the server
    run_command("uvicorn src.customer_service_agent.api:app --host 0.0.0.0 --port 8000 --reload")
    
    print("✅ FastAPI deployment completed!")

def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="Deploy AI Customer Service Agent")
    parser.add_argument(
        '--method',
        choices=['docker', 'serverless', 'fastapi', 'all'],
        default='docker',
        help='Deployment method'
    )
    parser.add_argument(
        '--env',
        choices=['dev', 'staging', 'prod'],
        default='dev',
        help='Deployment environment'
    )
    
    args = parser.parse_args()
    
    print(f"🎯 Starting deployment: {args.method} to {args.env}")
    print("=" * 50)
    
    # Check environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable is required")
        sys.exit(1)
    
    # Run deployment
    deployments = {
        'docker': deploy_docker,
        'serverless': deploy_serverless,
        'fastapi': deploy_fastapi
    }
    
    if args.method == 'all':
        for name, deploy_func in deployments.items():
            print(f"\n📦 Deploying with {name}...")
            deploy_func()
    else:
        deployments[args.method]()
    
    print(f"\n✅ Deployment to {args.env} completed successfully!")

if __name__ == "__main__":
    main()
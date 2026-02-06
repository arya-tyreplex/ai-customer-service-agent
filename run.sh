#!/bin/bash

# TyrePlex AI System - Main Control Script
# Usage: ./run.sh [command]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Virtual environment settings
VENV_DIR="venv"

# Detect Python command (handle Windows paths)
if command -v python &> /dev/null && python --version &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null && python3 --version &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo -e "${RED}❌ Python is not installed or not in PATH${NC}"
    exit 1
fi

# Detect pip command in venv
if [ -f "$VENV_DIR/Scripts/pip.exe" ]; then
    # Windows
    PIP_CMD="$VENV_DIR/Scripts/pip.exe"
    PYTHON_VENV="$VENV_DIR/Scripts/python.exe"
elif [ -f "$VENV_DIR/Scripts/pip" ]; then
    # Windows (without .exe)
    PIP_CMD="$VENV_DIR/Scripts/pip"
    PYTHON_VENV="$VENV_DIR/Scripts/python"
elif [ -f "$VENV_DIR/bin/pip" ]; then
    # Linux/Mac
    PIP_CMD="$VENV_DIR/bin/pip"
    PYTHON_VENV="$VENV_DIR/bin/python"
else
    PIP_CMD="pip"
    PYTHON_VENV="$PYTHON_CMD"
fi

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Python already detected globally
    print_success "Python found: $($PYTHON_CMD --version)"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_success "Docker found: $(docker --version)"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_success "Docker Compose found: $(docker-compose --version)"
    
    # Check CSV file
    if [ ! -f "vehicle_tyre_mapping.csv" ]; then
        print_error "vehicle_tyre_mapping.csv not found in project root"
        exit 1
    fi
    print_success "CSV file found"
}

# Create virtual environment
create_venv() {
    print_header "Creating Virtual Environment"
    
    if [ -d "$VENV_DIR" ]; then
        print_info "Virtual environment already exists"
    else
        print_info "Creating virtual environment..."
        $PYTHON_CMD -m venv $VENV_DIR
        print_success "Virtual environment created"
    fi
    
    # Update pip (Windows-safe method)
    print_info "Updating pip..."
    $PYTHON_VENV -m pip install --upgrade pip setuptools wheel 2>/dev/null || {
        print_info "Pip upgrade skipped (permission issue - not critical)"
    }
    print_success "Virtual environment ready"
}

# Install Python dependencies
install_dependencies() {
    print_header "Installing Python Dependencies"
    
    # Ensure venv exists
    if [ ! -d "$VENV_DIR" ]; then
        create_venv
    fi
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi
    
    print_info "Installing dependencies in virtual environment..."
    print_info "This may take 5-10 minutes (downloading torch, TTS, etc.)"
    echo ""
    $PYTHON_VENV -m pip install -r requirements.txt
    echo ""
    print_success "Dependencies installed"
}

# Prepare datasets
prepare_datasets() {
    print_header "Preparing Datasets"
    
    check_prerequisites
    install_dependencies
    
    print_info "Processing CSV and creating datasets..."
    $PYTHON_VENV src/ml_system/dataset_builder.py
    
    print_success "Dataset preparation complete"
}

# Train ML models
train_models() {
    print_header "Training ML Models"
    
    if [ ! -d "data/processed" ]; then
        print_error "Datasets not found. Run './run.sh prepare' first"
        exit 1
    fi
    
    print_info "Training 4 ML models..."
    $PYTHON_VENV src/ml_system/model_trainer.py
    
    print_success "Model training complete"
}

# Start Docker services
start_services() {
    print_header "Starting Docker Services"
    
    print_info "Starting MongoDB and Elasticsearch..."
    docker-compose up -d mongodb elasticsearch kibana
    
    print_info "Waiting for services to be healthy..."
    sleep 10
    
    # Check MongoDB
    if docker-compose ps mongodb | grep -q "Up"; then
        print_success "MongoDB is running on port 27017"
    else
        print_error "MongoDB failed to start"
        exit 1
    fi
    
    # Check Elasticsearch
    if docker-compose ps elasticsearch | grep -q "Up"; then
        print_success "Elasticsearch is running on port 9200"
    else
        print_error "Elasticsearch failed to start"
        exit 1
    fi
    
    print_info "Services started successfully"
    print_info "MongoDB: mongodb://localhost:27017/"
    print_info "Elasticsearch: http://localhost:9200"
}

# Stop Docker services
stop_services() {
    print_header "Stopping Docker Services"
    
    docker-compose down
    print_success "Services stopped"
}

# Sync data to Elasticsearch
sync_elasticsearch() {
    print_header "Syncing Data to Elasticsearch"
    
    # Check if services are running
    if ! docker-compose ps mongodb | grep -q "Up"; then
        print_error "MongoDB is not running. Start services first: ./run.sh services"
        exit 1
    fi
    
    if ! docker-compose ps elasticsearch | grep -q "Up"; then
        print_error "Elasticsearch is not running. Start services first: ./run.sh services"
        exit 1
    fi
    
    # Wait a bit for ES to be fully ready
    print_info "Waiting for Elasticsearch to be ready..."
    sleep 5
    
    print_info "Syncing data from MongoDB to Elasticsearch..."
    $PYTHON_VENV src/inhouse_ml/elasticsearch_indexer.py
    
    if [ $? -eq 0 ]; then
        print_success "Elasticsearch sync complete"
    else
        print_error "Elasticsearch sync failed"
        print_info "Check if services are running: docker-compose ps"
        print_info "Check logs: docker-compose logs elasticsearch"
        exit 1
    fi
}

# Process CSV and load to MongoDB
process_csv() {
    print_header "Processing CSV Data"
    
    # Check if MongoDB is running
    if ! docker-compose ps mongodb | grep -q "Up"; then
        print_error "MongoDB is not running. Start services first: ./run.sh services"
        exit 1
    fi
    
    print_info "Processing CSV and loading to MongoDB..."
    $PYTHON_VENV process_csv.py
    
    print_success "CSV processing complete"
}

# Run application
run_application() {
    print_header "Running Application"
    
    # Ensure dependencies are installed
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Virtual environment not found. Creating..."
        create_venv
        install_dependencies
    fi
    
    # Check if services are running
    if ! docker-compose ps mongodb | grep -q "Up"; then
        print_error "MongoDB is not running. Start services first: ./run.sh services"
        exit 1
    fi
    
    print_info "Starting TyrePlex AI REST API..."
    print_info "API will be available at: http://localhost:5000"
    print_info "Press Ctrl+C to stop"
    $PYTHON_VENV src/api/rest_api.py
}

# Run tests
run_tests() {
    print_header "Running Tests"
    
    print_info "Running ML model tests..."
    $PYTHON_VENV src/ml_system/ml_inference.py
    
    print_info "Running CSV integration tests..."
    $PYTHON_VENV test_csv_integration.py
    
    print_info "Running complete demo..."
    $PYTHON_VENV examples/complete_ml_demo.py
    
    print_success "All tests passed"
}

# Run interactive demo
run_demo() {
    print_header "Running Interactive Demo"
    
    echo ""
    print_info "Choose demo type:"
    echo "  1. Text-based demo (default)"
    echo "  2. Voice demo - Robotic voice (pyttsx3)"
    echo "  3. Voice demo - Natural voice (Google TTS) ⭐"
    echo "  4. Voice demo - AWS Voice (uses Google TTS) 🌐"
    echo ""
    read -p "Enter choice (1/2/3/4): " choice
    
    case "$choice" in
        2)
            print_info "Starting voice demo (robotic voice)..."
            print_info "Make sure your microphone is connected!"
            
            # Check if voice dependencies are installed
            $PYTHON_VENV -c "import speech_recognition, pyttsx3" 2>/dev/null
            if [ $? -ne 0 ]; then
                print_error "Voice dependencies not installed!"
                print_info "Installing voice dependencies..."
                $PYTHON_VENV -m pip install SpeechRecognition pyttsx3 --quiet
            fi
            
            $PYTHON_VENV voice_demo_local.py
            ;;
        3)
            print_info "Starting voice demo (natural voice)..."
            print_info "Make sure your microphone is connected!"
            
            # Check if natural voice dependencies are installed
            $PYTHON_VENV -c "import speech_recognition, gtts, pygame" 2>/dev/null
            if [ $? -ne 0 ]; then
                print_error "Natural voice dependencies not installed!"
                print_info "Installing natural voice dependencies..."
                $PYTHON_VENV -m pip install SpeechRecognition gTTS pygame --quiet
            fi
            
            $PYTHON_VENV voice_demo_natural.py
            ;;
        4)
            print_info "Starting voice demo (AWS - uses Google TTS)..."
            print_info "Make sure your microphone is connected!"
            print_info "Note: Currently uses Google TTS (same as Option 3)"
            
            # Check if voice dependencies are installed
            $PYTHON_VENV -c "import speech_recognition, gtts, pygame" 2>/dev/null
            if [ $? -ne 0 ]; then
                print_error "Voice dependencies not installed!"
                print_info "Installing voice dependencies..."
                $PYTHON_VENV -m pip install SpeechRecognition gTTS pygame --quiet
            fi
            
            # Check if boto3 is installed
            $PYTHON_VENV -c "import boto3" 2>/dev/null
            if [ $? -ne 0 ]; then
                print_info "Installing boto3..."
                $PYTHON_VENV -m pip install boto3 --quiet
            fi
            
            $PYTHON_VENV voice_demo_aws.py
            ;;
        *)
            print_info "Starting text-based demo..."
            $PYTHON_VENV demo.py
            ;;
    esac
}

# Complete setup (all steps)
complete_setup() {
    print_header "Complete Setup - All Steps"
    
    echo ""
    print_info "Step 1/7: Checking prerequisites..."
    check_prerequisites
    
    echo ""
    print_info "Step 2/7: Creating virtual environment..."
    create_venv
    
    echo ""
    print_info "Step 3/7: Installing dependencies..."
    install_dependencies
    
    echo ""
    print_info "Step 4/7: Preparing datasets..."
    prepare_datasets
    
    echo ""
    print_info "Step 5/7: Training ML models..."
    train_models
    
    echo ""
    print_info "Step 6/7: Starting Docker services..."
    start_services
    
    echo ""
    print_info "Step 7/7: Processing CSV and syncing to Elasticsearch..."
    process_csv
    sync_elasticsearch
    
    echo ""
    print_header "Setup Complete!"
    print_success "All systems ready"
    print_info "Virtual environment: $VENV_DIR/"
    print_info "Run './run.sh test' to verify everything works"
    print_info "Run './run.sh run' to start the application"
}

# Clean virtual environment
clean_venv() {
    print_header "Cleaning Virtual Environment"
    
    if [ -d "$VENV_DIR" ]; then
        print_info "Removing virtual environment..."
        rm -rf $VENV_DIR
        print_success "Virtual environment removed"
    else
        print_info "No virtual environment found"
    fi
}

# Show usage
show_usage() {
    echo "TyrePlex AI System - Control Script"
    echo ""
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  venv      - Create virtual environment"
    echo "  prepare   - Prepare datasets from CSV"
    echo "  train     - Train ML models"
    echo "  services  - Start Docker services (MongoDB + Elasticsearch)"
    echo "  stop      - Stop Docker services"
    echo "  sync      - Sync data to Elasticsearch"
    echo "  process   - Process CSV and load to MongoDB"
    echo "  run       - Run REST API server (for testing)"
    echo "  test      - Run all tests"
    echo "  demo      - Run interactive demo (text or voice)"
    echo "  all       - Complete setup (all steps)"
    echo "  clean     - Remove virtual environment"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run.sh all       # Complete setup (recommended)"
    echo "  ./run.sh venv      # Create virtual environment"
    echo "  ./run.sh prepare   # Prepare datasets"
    echo "  ./run.sh train     # Train ML models"
    echo "  ./run.sh services  # Start Docker services"
    echo "  ./run.sh run       # Start REST API for testing"
    echo "  ./run.sh demo      # Run interactive demo (text or voice)"
    echo "  ./run.sh test      # Run tests"
    echo ""
    echo "Note: All Python commands run inside virtual environment (venv/)"
    echo "Note: No external APIs - everything runs on your laptop"
}

# Main script
main() {
    case "$1" in
        venv)
            create_venv
            ;;
        prepare)
            prepare_datasets
            ;;
        train)
            train_models
            ;;
        services)
            start_services
            ;;
        stop)
            stop_services
            ;;
        sync)
            sync_elasticsearch
            ;;
        process)
            process_csv
            ;;
        run)
            run_application
            ;;
        test)
            run_tests
            ;;
        demo)
            run_demo
            ;;
        all)
            complete_setup
            ;;
        clean)
            clean_venv
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

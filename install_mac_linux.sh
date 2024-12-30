#!/bin/bash

# Function to check if Python is installed
check_python_installed() {
    if command -v python3 &>/dev/null; then
        echo "Python is already installed."
        return 0
    else
        return 1
    fi
}

# Function to install Python using Homebrew
install_python() {
    echo "Installing Python..."
    if ! command -v brew &>/dev/null; then
        echo "Homebrew not found. Please install Homebrew first."
        exit 1
    fi
    brew update
    brew install python
    echo "Python installed successfully."
}

# Function to upgrade pip and install requirements
install_requirements() {
    echo "Upgrading pip and installing requirements..."
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install required packages."
        exit 1
    fi
}

# Function to run the Yon SS tool Python script
run_main_script() {
    echo "Running main.py..."
    python3 Yon SS tool.py
    if [ $? -ne 0 ]; then
        echo "Failed to execute main.py"
        exit 1
    fi
}

# Main execution
main() {
    check_python_installed || install_python
    install_requirements
    run_main_script
}

# Execute the Yon SS tool function
main

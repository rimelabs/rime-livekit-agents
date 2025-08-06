#!/usr/bin/env python3
"""
Rime LiveKit Agent Setup Script
This script sets up both the frontend and agent components of the Rime LiveKit Agent system.
It handles repository cloning, environment setup, and dependency installation.
"""

import os
import subprocess
import sys
from typing import Optional
import shutil
from pathlib import Path
import platform
import venv
import json
import datetime


CONFIG_FILE = "rime_config.json"


class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_colored(text: str, color: str) -> None:
    """Print colored text to terminal"""
    print(f"{color}{text}{Colors.ENDC}")


def check_pnpm() -> bool:
    """Check if pnpm is installed"""
    try:
        subprocess.run(
            ["pnpm", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return True
    except FileNotFoundError:
        return False


def get_user_input(prompt: str, default: Optional[str] = None) -> str:
    """Get user input with optional default value"""
    if default:
        prompt = f"{prompt} (default: {default}): "
    else:
        prompt = f"{prompt}: "

    value = input(prompt).strip()
    if not value and default:
        return default
    return value


def create_env_file(path: str, variables: dict) -> None:
    """Create .env file with provided variables"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for key, value in variables.items():
            f.write(f"{key}={value}\n")


def setup_virtual_env(path: str) -> str:
    """Create and activate virtual environment"""
    venv_path = os.path.join(path, "venv")

    # Remove existing venv if it exists
    if os.path.exists(venv_path):
        shutil.rmtree(venv_path)

    # Create new venv using python -m venv
    subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)

    # Get the activate script path based on OS
    if platform.system() == "Windows":
        activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
    else:
        activate_script = os.path.join(venv_path, "bin", "activate")

    return activate_script


def validate_env_vars(env_vars: dict) -> bool:
    """Validate that all environment variables have values"""
    missing_vars = [key for key, value in env_vars.items() if not value]
    if missing_vars:
        print_colored(
            "\nError: The following environment variables are required:", Colors.FAIL
        )
        for var in missing_vars:
            print(f"- {var}")
        return False
    return True


def setup_frontend_files(frontend_name: str) -> None:
    """Setup frontend configuration files and images"""
    # Get the script's directory (Rime-simple-agent)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Replace app-config.ts
    frontend_config_path = os.path.join(frontend_name, "app-config.ts")
    assets_config_path = os.path.join(script_dir, "assets", "app-config.ts")

    try:
        # Delete existing app-config.ts if it exists
        if os.path.exists(frontend_config_path):
            os.remove(frontend_config_path)
            print_colored("Removed existing app-config.ts", Colors.BLUE)

        # Copy new app-config.ts
        shutil.copy2(assets_config_path, frontend_config_path)
        print_colored("Copied new app-config.ts to frontend", Colors.GREEN)

        # Clean public folder and copy images
        public_dir = os.path.join(frontend_name, "public")
        assets_dir = os.path.join(script_dir, "assets")

        # Clean existing images in public folder
        for item in os.listdir(public_dir):
            if item.endswith((".svg", ".png", ".jpg", ".ico")):
                os.remove(os.path.join(public_dir, item))
        print_colored("Cleaned existing images from public folder", Colors.BLUE)

        # Copy new images
        for item in os.listdir(assets_dir):
            if item.endswith((".svg", ".png", ".jpg", ".ico")):
                shutil.copy2(
                    os.path.join(assets_dir, item), os.path.join(public_dir, item)
                )
        print_colored("Copied new images to public folder", Colors.GREEN)

    except Exception as e:
        print_colored(f"Error setting up frontend files: {e}", Colors.FAIL)
        sys.exit(1)


def save_config(config: dict) -> None:
    """Save configuration to file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, CONFIG_FILE)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)


def load_config() -> dict:
    """Load configuration from file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, CONFIG_FILE)
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def is_port_in_use(port: int) -> bool:
    """Check if a port is in use"""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def start_servers(frontend_name: str, agent_script_path: str, venv_activate: str):
    """Start both frontend and backend servers"""
    # Check if servers are already running
    if is_port_in_use(3000):  # Default Next.js port
        print_colored(
            "Frontend server is already running on port 3000!", Colors.WARNING
        )
        return

    print_colored("\n=== Starting Rime LiveKit Agent Services ===", Colors.HEADER)

    # Start frontend server
    print_colored("\n1. Starting frontend server...", Colors.BLUE)
    try:
        # Start frontend in background
        frontend_process = subprocess.Popen(
            ["pnpm", "run", "dev"],
            cwd=frontend_name,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print_colored("Frontend server started successfully!", Colors.GREEN)
    except subprocess.CalledProcessError as e:
        print_colored(f"Error starting frontend server: {e}", Colors.FAIL)
        sys.exit(1)

    # Start backend server
    print_colored("\n2. Starting agent-script server...", Colors.BLUE)
    try:
        if platform.system() == "Windows":
            backend_process = subprocess.Popen(
                [f"{venv_activate} && python rime_agent.py dev"],
                cwd=agent_script_path,
                shell=True,
            )
        else:
            backend_process = subprocess.Popen(
                f"source {venv_activate} && python rime_agent.py dev",
                cwd=agent_script_path,
                shell=True,
                executable="/bin/bash",
            )
        print_colored("Agent-script server started successfully!", Colors.GREEN)
    except Exception as e:
        print_colored(f"Error starting agent-script server: {e}", Colors.FAIL)
        frontend_process.terminate()
        sys.exit(1)

    print_colored(
        "\nBoth services are now running! Press Ctrl+C to stop both servers.",
        Colors.GREEN,
    )
    print_colored("\nOpen your browser and navigate to:", Colors.BLUE)
    print_colored("http://localhost:3000", Colors.GREEN)

    try:
        # Keep the main process running and handle Ctrl+C
        frontend_process.wait()
    except KeyboardInterrupt:
        print_colored("\nShutting down servers...", Colors.WARNING)
        frontend_process.terminate()
        backend_process.terminate()
        print_colored("Servers stopped successfully!", Colors.GREEN)


def main():
    print_colored("\n=== Rime LiveKit Agent ===", Colors.HEADER)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    agent_script_dir = os.path.join(script_dir, "agent-script")
    venv_path = os.path.join(agent_script_dir, "venv")

    # Load existing configuration
    config = load_config()
    frontend_name = config.get("frontend_name", "frontend")
    frontend_dir = os.path.join(script_dir, frontend_name)

    # Check if setup is already done
    if os.path.exists(frontend_dir) and os.path.exists(venv_path):
        print_colored(
            "Setup already completed. What would you like to do?", Colors.BLUE
        )
        print("1. Start servers")
        print("2. Reinstall everything")
        print("3. Exit")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == "1":
            # Get the activate script path
            if platform.system() == "Windows":
                activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
            else:
                activate_script = os.path.join(venv_path, "bin", "activate")

            start_servers(frontend_name, agent_script_dir, activate_script)
            return
        elif choice == "2":
            # Clean up existing directories
            print_colored("\nCleaning up existing installation...", Colors.BLUE)
            if os.path.exists(frontend_dir):
                shutil.rmtree(frontend_dir)
                print_colored(f"Removed {frontend_dir}", Colors.GREEN)
            if os.path.exists(venv_path):
                shutil.rmtree(venv_path)
                print_colored(f"Removed {venv_path}", Colors.GREEN)
        elif choice == "3":
            sys.exit(0)
        # invalid choice continues with full setup

    print_colored(
        "This script will set up both the frontend and agent components.", Colors.BLUE
    )

    # Check Python version
    if sys.version_info < (3, 8):
        print_colored("Error: Python 3.8 or higher is required", Colors.FAIL)
        sys.exit(1)

    # Check and ask about pnpm
    if not check_pnpm():
        print_colored("\nError: pnpm is not installed!", Colors.FAIL)
        print_colored(
            "Please install pnpm first. You can install it using npm:", Colors.WARNING
        )
        print("npm install -g pnpm")
        sys.exit(1)

    # Get frontend folder name
    frontend_name = get_user_input("Enter the frontend folder name", "frontend")
    print_colored(f"\nUsing frontend folder name: {frontend_name}", Colors.GREEN)

    # Save configuration
    config = {
        "frontend_name": frontend_name,
        "setup_date": str(datetime.datetime.now()),
    }
    save_config(config)

    # Clone the repository
    print_colored("\nCloning the agent-starter-react repository...", Colors.BLUE)
    if os.path.exists(frontend_name):
        print_colored(f"Error: Directory {frontend_name} already exists!", Colors.FAIL)
        sys.exit(1)

    try:
        subprocess.run(
            [
                "git",
                "clone",
                "https://github.com/livekit-examples/agent-starter-react.git",
                frontend_name,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print_colored(f"Error cloning repository: {e}", Colors.FAIL)
        sys.exit(1)

    # Setup frontend configuration and images
    print_colored("\nSetting up frontend configuration...", Colors.BLUE)
    setup_frontend_files(frontend_name)

    # Get environment variables
    print_colored(
        "\nPlease provide the following environment variables:", Colors.HEADER
    )

    # Common variables for both frontend and agent-script
    env_vars = {
        "LIVEKIT_URL": get_user_input("LIVEKIT_URL (your LiveKit server URL)"),
        "LIVEKIT_API_KEY": get_user_input("LIVEKIT_API_KEY"),
        "LIVEKIT_API_SECRET": get_user_input("LIVEKIT_API_SECRET"),
        "OPENAI_API_KEY": get_user_input("OPENAI_API_KEY"),
        "RIME_API_KEY": get_user_input("RIME_API_KEY"),
    }

    # Validate environment variables
    if not validate_env_vars(env_vars):
        sys.exit(1)

    # Create frontend .env file
    frontend_env = {
        "LIVEKIT_URL": env_vars["LIVEKIT_URL"],
        "LIVEKIT_API_KEY": env_vars["LIVEKIT_API_KEY"],
        "LIVEKIT_API_SECRET": env_vars["LIVEKIT_API_SECRET"],
    }
    frontend_env_path = os.path.join(frontend_name, ".env.local")
    create_env_file(frontend_env_path, frontend_env)
    print_colored(f"\nCreated frontend .env file at: {frontend_env_path}", Colors.GREEN)

    # Create agent-script .env file
    agent_script_env = {
        "LIVEKIT_URL": env_vars["LIVEKIT_URL"],
        "LIVEKIT_API_KEY": env_vars["LIVEKIT_API_KEY"],
        "LIVEKIT_API_SECRET": env_vars["LIVEKIT_API_SECRET"],
        "OPENAI_API_KEY": env_vars["OPENAI_API_KEY"],
        "RIME_API_KEY": env_vars["RIME_API_KEY"],
    }
    script_dir = os.path.dirname(os.path.abspath(__file__))
    agent_script_env_path = os.path.join(script_dir, "agent-script", ".env")
    create_env_file(agent_script_env_path, agent_script_env)
    print_colored(
        f"Created agent-script .env file at: {agent_script_env_path}", Colors.GREEN
    )

    # Setup agent-script virtual environment
    print_colored("\nSetting up agent-script virtual environment...", Colors.BLUE)
    agent_script_path = os.path.join(script_dir, "agent-script")
    venv_activate = setup_virtual_env(agent_script_path)

    # Install agent-script dependencies
    print_colored("\nInstalling agent-script dependencies...", Colors.BLUE)
    pip_cmd = "pip install -r requirements.txt"
    if platform.system() == "Windows":
        subprocess.run(
            f"{venv_activate} && {pip_cmd}", shell=True, cwd=agent_script_path
        )
    else:
        subprocess.run(
            f"source {venv_activate} && {pip_cmd}",
            shell=True,
            cwd=agent_script_path,
            executable="/bin/bash",
        )

    # Install frontend dependencies if needed
    print_colored("\nInstalling frontend dependencies...", Colors.BLUE)
    try:
        subprocess.run(["pnpm", "install"], cwd=frontend_name, check=True)
    except subprocess.CalledProcessError as e:
        print_colored(f"Error installing frontend dependencies: {e}", Colors.FAIL)
        sys.exit(1)

    # Start the services
    start_servers(frontend_name, agent_script_path, venv_activate)


if __name__ == "__main__":
    main()

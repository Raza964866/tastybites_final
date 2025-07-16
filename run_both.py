#!/usr/bin/env python3
"""
Script to run both the main TastyBites website and the admin panel separately.
This demonstrates that they have separate session management and authentication.
"""

import subprocess
import sys
import time
import threading

def run_main_app():
    """Run the main TastyBites website on port 5000"""
    print("Starting TastyBites Main Website on http://127.0.0.1:5000")
    try:
        subprocess.run([sys.executable, "-m", "tastybites.backend.app"], 
                      cwd=".", check=True)
    except KeyboardInterrupt:
        print("Main website stopped.")
    except Exception as e:
        print(f"Error running main app: {e}")

def run_admin_app():
    """Run the admin panel on port 5001"""
    print("Starting TastyBites Admin Panel on http://127.0.0.1:5001")
    try:
        subprocess.run([sys.executable, "-m", "tastybites.admin_panel.admin_app"], 
                      cwd=".", check=True)
    except KeyboardInterrupt:
        print("Admin panel stopped.")
    except Exception as e:
        print(f"Error running admin app: {e}")

def main():
    print("=" * 60)
    print("TastyBites - Running Both Applications")
    print("=" * 60)
    print()
    print("This script will run both applications separately:")
    print("1. Main Website: http://127.0.0.1:5000")
    print("2. Admin Panel: http://127.0.0.1:5001")
    print()
    print("KEY FEATURES:")
    print("- Separate session management (different session cookies)")
    print("- Admin login won't affect main website users")
    print("- Main website login won't affect admin panel")
    print("- Admin can access main site via 'View Site' link")
    print()
    print("Press Ctrl+C to stop both applications")
    print("=" * 60)
    
    # Give a moment for the user to read
    time.sleep(2)
    
    # Create threads for both applications
    main_thread = threading.Thread(target=run_main_app)
    admin_thread = threading.Thread(target=run_admin_app)
    
    # Start both threads
    main_thread.daemon = True
    admin_thread.daemon = True
    
    main_thread.start()
    time.sleep(1)  # Small delay to let main app start first
    admin_thread.start()
    
    try:
        # Keep the main thread alive
        while main_thread.is_alive() or admin_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping both applications...")
        sys.exit(0)

if __name__ == "__main__":
    main()

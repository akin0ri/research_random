#!/usr/bin/env python3
"""
Script to run onionscanv3 on a list of .onion URLs from a file.
Usage: python run_onionscan.py [input_file]
Default input file is 'target100.txt' if not specified.
"""

import subprocess
import sys
import time
import os
from datetime import datetime
import concurrent.futures

def run_onionscan(url):
    """
    Run onionscanv3 on the specified URL.
    
    Args:
        url (str): The .onion URL to scan
        
    Returns:
        bool: True if scan completed successfully, False otherwise
    """
    try:
        print(f"\n[*] Scanning: {url}")
        print(f"[*] Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Construct the command as a string
        cmd = f"onionscanv3 --torProxyAddress=127.0.0.1:9050 --verbose {url}"
        
        # Execute the command with shell=True to ensure output is displayed in console
        # stdout and stderr are not redirected, so they will display in the console
        process = subprocess.run(cmd, shell=True, check=False)
        
        # Get return code
        return_code = process.returncode
        
        if return_code == 0:
            print(f"[+] Scan completed successfully for {url}")
            return True
        else:
            print(f"[-] Error scanning {url}. Return code: {return_code}")
            return False
            
    except Exception as e:
        print(f"[-] Exception occurred while scanning {url}: {str(e)}")
        return False
    finally:
        print(f"[*] End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    # Get input file from command line argument or use default
    input_file = sys.argv[1] if len(sys.argv) > 1 else "target100.txt"
    
    if not os.path.exists(input_file):
        print(f"[-] Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    # Read URLs from the input file
    try:
        with open(input_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[-] Error reading input file: {str(e)}")
        sys.exit(1)
    
    print(f"[*] Loaded {len(urls)} URLs from {input_file}")
    
    # Track statistics
    successful = 0
    failed = 0

    # Use ThreadPoolExecutor to run scans in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Map the run_onionscan function to the URLs
        future_to_url = {executor.submit(run_onionscan, url): url for url in urls}
        
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                if future.result():
                    successful += 1
                else:
                    failed += 1
            except Exception as exc:
                print(f'[-] {url} generated an exception: {exc}')
                failed += 1

    # Print summary
    print("\n" + "="*50)
    print(f"[*] Scan Summary:")
    print(f"[*] Total URLs: {len(urls)}")
    print(f"[+] Successful scans: {successful}")
    print(f"[-] Failed scans: {failed}")
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Scan interrupted by user.")
        sys.exit(1)
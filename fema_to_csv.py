import os
import sys
import requests
import pandas as pd
import json

def check_file_permissions():
    """Check and print file permissions and location"""
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    
    print(f"Script location: {script_path}")
    print(f"Script directory: {script_dir}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if we have write permission in the current directory
    try:
        test_file = os.path.join(script_dir, 'test_permissions.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("Write permissions: OK")
    except PermissionError:
        print("Warning: No write permissions in current directory")
        print("Try running the script from a directory where you have write permissions")
        sys.exit(1)

def check_environment():
    """Check Python environment and dependencies"""
    print(f"Python version: {sys.version}")
    print(f"Python location: {sys.executable}")
    print("\nInstalled packages:")
    
    # Get the site-packages directory
    import site
    print(f"Packages location: {site.getsitepackages()}")
    
    try:
        print(f"Pandas version: {pd.__version__}")
        print(f"Requests version: {requests.__version__}")
    except NameError as e:
        print(f"Missing package: {e}")
    print("\n")

def fetch_fema_data():
    """Fetch data from FEMA API"""
    url = "https://www.fema.gov/api/open/v1/DeclarationDenials"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def convert_to_csv():
    """Convert FEMA data to CSV"""
    # Check permissions first
    check_file_permissions()
    
    # Check environment
    check_environment()
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.getcwd(), 'output')
    try:
        os.makedirs(output_dir, exist_ok=True)
    except PermissionError:
        print(f"Cannot create output directory at {output_dir}")
        output_dir = os.path.expanduser('~/Downloads')
        print(f"Will try to save to Downloads folder: {output_dir}")
    
    # Fetch the data
    data = fetch_fema_data()
    
    if not data or 'DeclarationDenials' not in data:
        print("No data found or invalid data structure")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data['DeclarationDenials'])
    
    # Convert dates to datetime format
    date_columns = [
        'declarationRequestDate',
        'requestedIncidentBeginDate',
        'requestedIncidentEndDate',
        'requestStatusDate',
        'incidentBeginDate'
    ]
    
    for col in date_columns:
        df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
        
    # Save to CSV
    output_file = os.path.join(output_dir, 'fema_declaration_denials.csv')
    try:
        df.to_csv(output_file, index=False)
        print(f"Data has been saved to {output_file}")
    except PermissionError:
        fallback_file = os.path.expanduser('~/Downloads/fema_declaration_denials.csv')
        print(f"Permission denied. Trying to save to Downloads folder: {fallback_file}")
        df.to_csv(fallback_file, index=False)
        print(f"Data has been saved to {fallback_file}")
    
    # Print some basic statistics
    print(f"\nTotal records: {len(df)}")
    print(f"\nColumns in dataset: {', '.join(df.columns)}")

if __name__ == "__main__":
    try:
        convert_to_csv()
    except Exception as e:
        print(f"Error: {e}")
        print("\nPlease try running the script with:")
        print("1. cd to the directory containing the script")
        print("2. python3 fema_to_csv.py")
        sys.exit(1) 

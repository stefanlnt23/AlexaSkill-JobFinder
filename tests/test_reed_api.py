import os
import sys
import requests
from base64 import b64encode
import json

def get_reed_auth_header(api_key):
    """Generate Basic Auth header for Reed API"""
    credentials = f"{api_key}:"
    encoded = b64encode(credentials.encode('utf-8')).decode('utf-8')
    return {'Authorization': f'Basic {encoded}'}

def test_search_jobs(api_key):
    """Test job search functionality"""
    print("\nTesting job search...")
    
    base_url = 'https://www.reed.co.uk/api/1.0'
    
    # Test parameters
    params = {
        'keywords': 'software engineer',
        'locationName': 'London',
        'resultsToTake': 3
    }
    
    try:
        response = requests.get(
            f"{base_url}/search",
            headers=get_reed_auth_header(api_key),
            params=params
        )
        
        if response.status_code == 200:
            print("✓ API connection successful")
            jobs = response.json()
            print(f"✓ Found {len(jobs.get('results', []))} jobs")
            
            # Print sample job data
            if jobs.get('results'):
                print("\nSample job data:")
                job = jobs['results'][0]
                print(json.dumps(job, indent=2))
            
            return True
        else:
            print(f"✗ API request failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing API: {str(e)}")
        return False

def test_job_details(api_key, job_id):
    """Test job details retrieval"""
    print("\nTesting job details retrieval...")
    
    base_url = 'https://www.reed.co.uk/api/1.0'
    
    try:
        response = requests.get(
            f"{base_url}/jobs/{job_id}",
            headers=get_reed_auth_header(api_key)
        )
        
        if response.status_code == 200:
            print("✓ Job details retrieved successfully")
            job = response.json()
            print("\nJob details:")
            print(json.dumps(job, indent=2))
            return True
        else:
            print(f"✗ Failed to retrieve job details: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error retrieving job details: {str(e)}")
        return False

def main():
    """Main test function"""
    print("Reed.co.uk API Test Script")
    print("=========================")
    
    # Get API key from environment variable or command line
    api_key = os.environ.get('REED_API_KEY')
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    if not api_key:
        print("Error: No API key provided")
        print("Please provide your Reed API key either:")
        print("1. As an environment variable: REED_API_KEY=your-key python test_reed_api.py")
        print("2. As a command line argument: python test_reed_api.py your-key")
        sys.exit(1)
    
    # Run tests
    search_success = test_search_jobs(api_key)
    
    if search_success and len(sys.argv) > 2:
        # If a job ID is provided as second argument, test job details
        test_job_details(api_key, sys.argv[2])

if __name__ == "__main__":
    main()

import sys
import requests

def send_request(prev, curr, x, y):
    DJANGO_ENDPOINT_URL = 'http://localhost:8000/physical_placement_action'
    params = {
        'prev': prev,
        'curr': curr,
        'x': x,
        'y': y
    }
    # Make the GET request
    response = requests.get(DJANGO_ENDPOINT_URL, params=params)
    
    # Check response status
    if response.status_code == 200:
        print(f"Request sent successfully. {response.text}")
    else:
        print(f"Failed to send request. Status code: {response.status_code} {response.text}")

if __name__ == "__main__":
    # Check if all required command-line arguments are provided
    if len(sys.argv) != 5:
        print("Usage: python make_move.py prev curr x y")
        sys.exit(1)
    
    # Extract command-line arguments
    prev = sys.argv[1]
    curr = sys.argv[2]
    x = sys.argv[3]
    y = sys.argv[4]
    
    # Send the request
    send_request(prev, curr, x, y)

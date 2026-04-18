import concurrent.futures
import requests

def send_query(i):
    response = requests.post(
        "http://localhost:8000/ask",
        json={"query": "What is Docker?", "top_k": 5}
    )
    return f"Request {i}: {response.status_code}"

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(send_query, i) for i in range(5)]
    for f in concurrent.futures.as_completed(futures):
        print(f.result())
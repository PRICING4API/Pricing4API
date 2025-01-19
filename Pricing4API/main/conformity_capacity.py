import asyncio
import os
import time
import httpx
from dotenv import load_dotenv
import requests


class ConformityCapacityTest:
    def __init__(self, rate_wait_period, total_requests, rate_value, url, params):
        self.rate_wait_period = rate_wait_period  # Wait time between batches of requests
        self.total_requests = total_requests  # Total number of requests to simulate
        self.rate_value = rate_value  # Number of requests allowed per rate period
        self.url = url  # API endpoint
        self.params = params  # Parameters for the API
        self.access_token = self.get_access_token()
        self.start_time = None
        self.error_counts = {"429": 0, "others": 0, "connection_errors": 0}

    @staticmethod
    def get_access_token():
        """Retrieve an access token using Amadeus credentials."""
        load_dotenv()

        AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
        AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

        AUTH_ENDPOINT = "https://test.api.amadeus.com/v1/security/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": AMADEUS_CLIENT_ID,
            "client_secret": AMADEUS_CLIENT_SECRET,
        }

        response = requests.post(AUTH_ENDPOINT, headers=headers, data=data)
        response.raise_for_status()  # Ensure the request succeeded
        return response.json()["access_token"]

    async def api_call(self, n, client):
        """Make an API call using a shared client."""
        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            call_time = time.time() - self.start_time
            print(f"[{n}] Request started at {call_time:.2f} seconds")

            response = await client.get(self.url, headers=headers, params=self.params)

            call_time = time.time() - self.start_time
            print(f"[{n}] Request completed at {call_time:.2f} seconds with status {response.status_code}")

            if response.status_code == 200:
                print(f"[{n}] Successful response: {response.headers}")  # Show headers only
            elif response.status_code == 429:
                print(f"[{n}] Error 429: Rate limit exceeded")
                self.error_counts["429"] += 1
            else:
                print(f"[{n}] Error {response.status_code}: {response.text}")
                self.error_counts["others"] += 1
        except httpx.RequestError as exc:
            print(f"[{n}] Connection error: {exc}")
            self.error_counts["connection_errors"] += 1

    async def release_tokens(self, semaphore):
        """Release a fixed number of tokens at regular intervals."""
        for _ in range(self.rate_value):
            semaphore.release()
        while True:
            await asyncio.sleep(self.rate_wait_period)
            for _ in range(self.rate_value):
                semaphore.release()

    async def controller(self):
        """Control the requests, ensuring the rate limit is respected."""
        semaphore = asyncio.Semaphore(0)
        asyncio.create_task(self.release_tokens(semaphore))

        async with httpx.AsyncClient() as client:  # Instantiate the HTTP client once
            tasks = []
            for i in range(self.total_requests):
                await semaphore.acquire()
                tasks.append(asyncio.create_task(self.api_call(i, client)))

            await asyncio.gather(*tasks)

        # Final summary
        print("\n--- Final Summary ---")
        print(f"Total requests: {self.total_requests}")
        print(f"429 Errors (Rate limit exceeded): {self.error_counts['429']}")
        print(f"Connection errors: {self.error_counts['connection_errors']}")
        print(f"Other errors: {self.error_counts['others']}")

    def execute(self):
        """Start the conformity test."""
        self.start_time = time.time()
        asyncio.run(self.controller())
        total_time = time.time() - self.start_time
        print(f"Total time: {total_time:.2f} seconds")


# Configuration
RATE_WAIT_PERIOD = 0.1  # Time interval between request batches (in seconds)
RATE_VALUE = 1  # Requests allowed per rate period
TOTAL_REQUESTS = 10  # Total number of requests to simulate
URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"  # API endpoint
PARAMS = {
    "originLocationCode": "MAD",
    "destinationLocationCode": "SVQ",
    "departureDate": "2025-01-16",
    "returnDate": "2025-01-17",
    "adults": 1,
    "max": 1,
}

# Execute the test
if __name__ == "__main__":
    test = ConformityCapacityTest(RATE_WAIT_PERIOD, TOTAL_REQUESTS, RATE_VALUE, URL, PARAMS)
    test.execute()

import requests
import threading
import time
import logging
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
from typing import List, Dict
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'stress_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class StressTest:
    def __init__(self, base_url: str, num_requests: int = 2000, concurrent_users: int = 100):
        self.base_url = base_url
        self.num_requests = num_requests
        self.concurrent_users = concurrent_users
        self.response_times: List[float] = []
        self.status_codes: Dict[int, int] = {}
        self.errors: List[str] = []
        self.start_time = None
        self.end_time = None

    def send_request(self) -> dict:
        start = time.time()
        result = {
            'success': False,
            'response_time': 0,
            'status_code': None,
            'error': None
        }

        try:
            response = requests.get(
                self.base_url,
                timeout=30,
                headers={'User-Agent': 'StressTest/1.0'}
            )
            result['response_time'] = time.time() - start
            result['status_code'] = response.status_code
            result['success'] = response.status_code == 200
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Request failed: {e}")

        return result

    def run_test(self):
        logger.info(f"Starting stress test on {self.base_url}")
        logger.info(f"Configurations:")
        logger.info(f"- Total Requests: {self.num_requests}")
        logger.info(f"- Concurrent Users: {self.concurrent_users}")

        self.start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.concurrent_users) as executor:
            future_to_url = {
                executor.submit(self.send_request): i 
                for i in range(self.num_requests)
            }

            completed = 0
            for future in as_completed(future_to_url):
                completed += 1
                result = future.result()
                
                if result['success']:
                    self.response_times.append(result['response_time'])
                    self.status_codes[result['status_code']] = \
                        self.status_codes.get(result['status_code'], 0) + 1
                else:
                    self.errors.append(result['error'])

                if completed % 100 == 0:
                    logger.info(f"Completed {completed}/{self.num_requests} requests")

        self.end_time = time.time()
        self.generate_report()

    def generate_report(self):
        total_time = self.end_time - self.start_time
        successful_requests = len(self.response_times)
        failed_requests = len(self.errors)

        report = {
            "Summary": {
                "Total Requests": self.num_requests,
                "Successful Requests": successful_requests,
                "Failed Requests": failed_requests,
                "Total Time": f"{total_time:.2f} seconds",
                "Requests/Second": f"{self.num_requests / total_time:.2f}",
            },
            "Response Times": {
                "Average": f"{statistics.mean(self.response_times):.3f}s" if self.response_times else "N/A",
                "Median": f"{statistics.median(self.response_times):.3f}s" if self.response_times else "N/A",
                "95th Percentile": f"{statistics.quantiles(self.response_times, n=20)[-1]:.3f}s" if self.response_times else "N/A",
                "Min": f"{min(self.response_times):.3f}s" if self.response_times else "N/A",
                "Max": f"{max(self.response_times):.3f}s" if self.response_times else "N/A",
            },
            "Status Codes": self.status_codes,
            "Errors": self.errors[:10]  # Show first 10 errors
        }

        # Log report
        logger.info("=== Stress Test Report ===")
        logger.info(json.dumps(report, indent=2))

        # Save report to file
        report_file = f'stress_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Full report saved to {report_file}")

if __name__ == "__main__":
    test = StressTest(
        base_url="http://206.189.134.228/",
        num_requests=2000,  # Increased from 1000
        concurrent_users=100  # Increased from 50
    )
    test.run_test()
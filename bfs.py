import requests
from bs4 import BeautifulSoup
from collections import deque
import time
import tracemalloc

class UniversityCrawler:
    def __init__(self):
        self.visited_links = set()
        self.total_requests = 0  # Track the number of requests made

    def crawl_courses(self, start_url, max_links):
        courses = []
        queue = deque([(start_url, 0)])  # Store (URL, depth) in the queue
        self.visited_links.add(start_url)

        tracemalloc.start()  # Start tracking memory usage
        start_time = time.time()  # Track total crawl time

        while queue and len(courses) < max_links:
            current_url, depth = queue.popleft()

            # Start time for the request
            req_start_time = time.time()

            try:
                response = requests.get(current_url, timeout=10)
                response.raise_for_status()  # Raise exception for 4xx/5xx

                req_end_time = time.time()
                self.total_requests += 1

                print(f"Fetched {current_url} in {req_end_time - req_start_time:.2f} seconds (Depth: {depth})")

                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract course-related content
                course_elements = soup.select(".course-title, .course-description")
                for course in course_elements:
                    if len(courses) < max_links:
                        courses.append(course.get_text(strip=True))

                # Add new links to the queue without filtering
                for link in soup.find_all('a', href=True):
                    next_url = requests.compat.urljoin(current_url, link['href'])

                    if next_url not in self.visited_links:
                        queue.append((next_url, depth + 1))
                        self.visited_links.add(next_url)

            except (requests.RequestException, requests.Timeout) as e:
                print(f"Error fetching {current_url}: {e}")

        # End of crawl
        total_time = time.time() - start_time
        current, peak = tracemalloc.get_traced_memory()  # Get memory usage
        tracemalloc.stop()

        print(f"\nTotal requests made: {self.total_requests}")
        print(f"Total time taken: {total_time:.2f} seconds")
        print(f"Peak memory usage: {peak / 10**6:.2f} MB")

        return courses

# Example usage
if __name__ == "__main__":
    crawler = UniversityCrawler()
    start_url = "https://umtc.catalog.prod.coursedog.com/courses?page=1&cq="
    max_links = 5  # Specify the max number of links to crawl

    courses = crawler.crawl_courses(start_url, max_links)
    print(f"\nCourses found: {len(courses)}")

import requests
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup

class WorkUaParser:
    BASE_URL = "https://www.work.ua/resumes"

    def __init__(self, job_position, location="", salary=None, experience=None, english_language=None, keywords=None):
        self.job_position = job_position
        self.location = location if location != "-" else ""
        self.salary = salary if salary != "-" else None
        self.experience = experience if experience != "-" else None
        self.english_language = english_language if english_language != "-" else None
        self.keywords = keywords if keywords != "-" else None
        self.resumes = []

    def fetch_multiple_pages(self, num_pages=10):
        all_resumes = []
        for page in range(1, num_pages + 1):
            self.log(f"Fetching page {page}...")
            page_resumes = self.fetch_resumes(page)
            if page_resumes:
                all_resumes.extend(page_resumes)
            else:
                self.log(f"No resumes found on page {page}. Stopping further fetches.")
                break
        return all_resumes

    def fetch_resumes(self, page=1):
        search_url = self.build_search_url(page)
        self.log(f"Fetching URL: {search_url}")
        try:
            response = requests.get(search_url)
            response.raise_for_status()
        except requests.RequestException as e:
            self.log(f"Error fetching resumes: {e}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        resumes = soup.find_all('div', class_='card card-hover card-search resume-link card-visited wordwrap')

        if not resumes:
            self.log(f"No resumes found on page {page}.")
            return []

        return [self.fetch_and_parse_resume(f"https://www.work.ua{resume.find('a', href=True)['href']}") for resume in resumes if resume.find('a', href=True)]

    def build_search_url(self, page=1):
        query_params = []
        search_url = f"{self.BASE_URL}-{self.location.replace(' ', '+').lower()}-{self.job_position.replace(' ', '+').lower()}" if self.location else f"{self.BASE_URL}-{self.job_position.replace(' ', '+').lower()}"

        if self.keywords:
            keyword_string = "+".join(self.keywords.split())
            search_url += f"+{keyword_string}"

        if self.salary:
            salary_code = self.get_salary_code(int(self.salary))
            query_params.append(f"salaryto={salary_code}")
            if salary_code >= 3:
                query_params.append(f"salaryfrom={salary_code - 2}")

        if self.experience is not None:
            query_params.append(f"experience={self.get_experience_code(self.experience)}")

        if self.english_language:
            query_params.append("language=1")

        search_url += f"?{'&'.join(query_params)}&page={page}"
        return search_url

    def fetch_and_parse_resume(self, url):
        self.log(f"Fetching resume: {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            self.log(f"Error fetching resume page: {e}")
            return None

        return self.parse_resume(BeautifulSoup(response.text, "html.parser"), url)

    def parse_resume(self, soup, link):
        return {
            "position": self.extract_text(soup, 'h2', 'mt-lg sm:mt-xl', "Not specified"),
            "salary_expectation": self.extract_text(soup, 'span', 'text-muted-print', "Not specified").replace('&nbsp;', ' '),
            "jobs_and_education": self.parse_experiences(soup),
            "skills": self.parse_skills(soup),
            "location": self.extract_location(soup),
            "add_info": self.extract_text(soup, tag='div', id="addInfo", default="Not specified"),
            "link": link
        }

    def parse_experiences(self, soup):
        experiences = []
        for job in soup.find_all('h2', class_='h4 strong-600 mt-lg sm:mt-xl'):
            if "Контактна інформація" not in job.text.strip():
                experiences.append(self.extract_experience_details(job))
        return experiences

    def extract_experience_details(self, job_element):
        title = job_element.text.strip() if job_element else "Not specified"
        company_element = job_element.find_next('p', class_='mb-0')
        name_with_duration = company_element.text.strip() if company_element else "Not specified"
        additional_info = company_element.find_next('p', class_='text-default-7 mb-0').text.strip() if company_element else "Not specified"
        duration = self.clean_duration(self.extract_text(job_element, 'span', 'text-default-7', "Not specified"))
        return {"title": title, "name": name_with_duration, "additional_info": additional_info, "duration": duration}

    def parse_skills(self, soup):
        return [skill.text.strip() for skill in soup.find_all('li', class_='no-style mr-sm mt-sm') if skill.find('span', class_='ellipsis')]

    def extract_location(self, soup):
        detail = next((d.find_next_sibling('dd').text.strip() for d in soup.find_all('dt') if "Місто проживання" in d.text.strip()), "Not specified")
        return detail

    def extract_text(self, soup, tag=None, class_name=None, id=None, default="Not specified"):
        element = soup.find(tag, class_=class_name) if class_name else soup.find(tag, id=id) if id else soup.find(tag)
        return element.text.strip() if element else default

    def get_salary_code(self, salary):
        return min(max((salary - 5000) // 5000 + 2, 2), 8)

    def get_experience_code(self, experience):
        if experience == 0:
            return 1
        elif experience <= 3:
            return 164
        return 165

    def clean_duration(self, duration):
        return duration.replace('(', '').replace(')', '').strip()

    def log(self, message):
        print(message)  # Replace with logging framework if needed

# Parser testing
# parser = WorkUaParser(job_position="designer", location="Kyiv", experience=3, english_language="yes")
# resumes = parser.fetch_multiple_pages(num_pages=6)

# if resumes:
#     for resume in resumes:
#         print(resume)
#         print("="*40)  # Just a separator for better readability
# else:
#     print("No resumes found!")

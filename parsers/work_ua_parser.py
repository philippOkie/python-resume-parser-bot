import requests
from bs4 import BeautifulSoup

class WorkUaParser:
    BASE_URL = "https://www.work.ua/resumes"
    salary_mapping = {
        10000: 2,
        15000: 3,
        20000: 4,
        30000: 5,
        40000: 6,
        50000: 7,
        100000: 8
    }

    def __init__(self, job_position, location="", salary=None, experience=None, english_language=None, keywords=None):
        self.job_position = job_position
        self.location = location
        self.salary = salary
        self.experience = experience  
        self.english_language = english_language
        self.keywords = keywords
        self.resumes = []

    def get_salary_code(self, salary):
        """Map salary to corresponding code."""
        for threshold, code in sorted(self.salary_mapping.items()):
            if salary <= threshold:
                return code
        return 2 

    def get_experience_code(self, experience):
        if experience == 0:
            return 1
        elif 1 <= experience <= 3:
            return 164  
        elif experience >= 5:
            return 165  
        else:
            return 166  

    def fetch_resumes(self):
        """Fetch resumes based on the initialized criteria."""
        search_url = self.build_search_url()
        print(f"Fetching resumes from URL: {search_url}")

        page_to_scrape = requests.get(search_url)
        if page_to_scrape.status_code != 200:
            print(f"Failed to retrieve data from work.ua: {search_url}")
            return []

        soup = BeautifulSoup(page_to_scrape.text, "html.parser")
        resumes = soup.find_all('div', class_='card card-hover card-search resume-link card-visited wordwrap')

        resume_data = []
        for resume in resumes:
            link_tag = resume.find('a', href=True)
            if link_tag:
                full_url = f"https://www.work.ua{link_tag['href']}"
                parsed_resume = self.fetch_and_parse_resume(full_url)
                if parsed_resume:
                    resume_data.append(parsed_resume)

        return resume_data
    
    def build_search_url(self):
            """Construct the search URL based on the user's criteria."""
            search_url = self.BASE_URL

            if self.location:
                search_url += f"-{self.location.replace(' ', '+').lower()}"

            search_url += f"-{self.job_position.replace(' ', '+').lower()}"

            if self.keywords:
                keyword_string = "+".join(self.keywords.split())
                search_url += f"+{keyword_string}"

            query_params = []

            query_params.append("notitle=1")

            if self.salary:
                salary_code = self.get_salary_code(int(self.salary))
                query_params.append(f"salaryto={salary_code}")
            
            if self.experience is not None:
                experience_code = self.get_experience_code(self.experience)
                query_params.append(f"experience={experience_code}")
            
            if self.english_language:
                query_params.append("language=1")

            if query_params:
                search_url += "/?" + "&".join(query_params)
            else:
                search_url += "/"

            return search_url
    
    def fetch_and_parse_resume(self, url):
        """Fetch a resume page and parse its contents."""
        resume_page = requests.get(url)
        if resume_page.status_code != 200:
            print(f"Failed to retrieve resume page: {url}")
            return None

        resume_soup = BeautifulSoup(resume_page.text, "html.parser")
        return self.parse_resume(resume_soup, url)

    def parse_resume(self, resume, link):
        """Extract information from the resume page."""
        position = self.get_text(resume, 'h2', 'mt-lg sm:mt-xl', "Not specified")
        salary_expectation = self.get_salary_expectation(resume)

        experiences = self.parse_experiences(resume)
        skills = self.parse_skills(resume)
        location = self.get_location(resume)
        add_info = self.get_text(resume, id="addInfo", default="Not specified")

        return {
            "position": position,
            "jobs_and_education": experiences,
            "skills": skills,
            "location": location,
            "salary_expectation": salary_expectation,
            "add_info": add_info,
            "link": link
        }

    def get_salary_expectation(self, resume):
        """Extract salary expectation from the resume."""
        salary_tag = resume.find('span', class_='text-muted-print')
        salary_text = salary_tag.text.strip().replace("&nbsp;", " ") if salary_tag else "Not specified"
        return salary_text.replace(',', '').strip()

    def parse_experiences(self, resume):
        """Extract job and education experiences from the resume."""
        experiences = []
        job_edu_titles = resume.find_all('h2', class_='h4 strong-600 mt-lg sm:mt-xl')

        for job_edu_title_element in job_edu_titles:
            if job_edu_title_element.text.strip() != "Контактна інформація":
                experiences.append(self.extract_experience_details(job_edu_title_element))

        return experiences

    def extract_experience_details(self, job_edu_title_element):
        """Extract details of a single job or education experience."""
        title = job_edu_title_element.text.strip() if job_edu_title_element else "Not specified"

        company_element = job_edu_title_element.find_next('p', class_='mb-0')
        name_with_duration = company_element.text.strip() if company_element else "Not specified"
        name = self.extract_company_name(name_with_duration)

        additional_info_element = company_element.find_next('p', class_='text-default-7 mb-0')
        additional_info = additional_info_element.text.strip() if additional_info_element else "Not specified"

        duration = self.get_text(job_edu_title_element, 'span', 'text-default-7', "Not specified")
        duration = self.clean_duration(duration)

        return {
            "title": title,
            "name": name,
            "additional_info": additional_info,
            "duration": duration
        }

    def extract_company_name(self, name_with_duration):
        """Extract the company name from the name with duration."""
        if '\n' in name_with_duration:
            return name_with_duration.split('\n')[-1].strip()
        return name_with_duration.strip()

    def clean_duration(self, duration):
        """Clean up the duration string."""
        if '(' in duration and ')' in duration:
            return duration.replace('(', '').replace(')', '').strip()
        return duration

    def parse_skills(self, resume):
        """Extract skills from the resume."""
        skills = []
        skill_items = resume.find_all('li', class_='no-style mr-sm mt-sm')

        for skill_item in skill_items:
            skill_name = skill_item.find('span', class_='ellipsis').text.strip() if skill_item.find('span', class_='ellipsis') else "Not specified"
            skills.append(skill_name)

        return skills

    def get_location(self, resume):
        """Extract the location from the resume."""
        details = resume.find_all('dt')
        for detail in details:
            if "Місто проживання" in detail.text.strip():
                return detail.find_next_sibling('dd').text.strip() if detail.find_next_sibling('dd') else "Not specified"
        return "Not specified"

    def get_text(self, soup, tag=None, class_name=None, id=None, default="Not specified"):
        """Helper function to extract text from HTML."""
        if tag and class_name:
            element = soup.find(tag, class_=class_name)
        elif tag and id:
            element = soup.find(tag, id=id)
        elif tag:
            element = soup.find(tag)
        else:
            element = None

        return element.text.strip() if element else default
    
def sort_resumes_by_relevance(resumes, keywords, salary, experience, english_language):
    """Sort resumes based on relevance to the job position."""
    def calculate_relevance(resume):
        score = 0

        # Add points for keyword matching in skills
        keyword_score = sum(1 for keyword in keywords if any(keyword.lower() in skill.lower() for skill in resume.get('skills', [])))
        score += keyword_score * 2  # Give double weight to keyword match

        # Salary score
        if resume.get("salary_expectation") == salary:
            score += 3  # Match with the expected salary

        # Add experience points
        if resume.get('experience', 0) >= experience:
            score += 5

        # Check if English language is mentioned
        if english_language == 'yes' and 'english' in [skill.lower() for skill in resume.get('skills', [])]:
            score += 2

        return score

    return sorted(resumes, key=lambda x: (calculate_relevance(x), x.get("position", "").lower()), reverse=True)

parser = WorkUaParser(job_position="Data Scientist", location="Kyiv", salary=80000, experience=3, english_language='yes', keywords="Python, SQL")
resumes = parser.fetch_resumes()
sorted_resumes = sort_resumes_by_relevance(resumes, keywords=["Python", "SQL"], salary=30000, experience=3, english_language='yes')

for resume in sorted_resumes:
    print(resume["position"], resume["salary_expectation"], resume["location"])
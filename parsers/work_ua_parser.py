import requests
from bs4 import BeautifulSoup
import json

class WorkUaParser:
    BASE_URL = "https://www.work.ua/resumes-"

    salary_mapping = {
        10000: 2,
        15000: 3,
        20000: 4,
        30000: 5,
        40000: 6,
        50000: 7,
        100000: 8
    }

    def get_salary_code(self, salary):
        for threshold, code in sorted(self.salary_mapping.items()):
            if salary <= threshold:
                return code
        return 8 

    def __init__(self, job_position, location="", salary=None):
        self.job_position = job_position
        self.location = location
        self.salary = salary
        self.resumes = []

    def fetch_resumes(self):
        search_url = f"{self.BASE_URL}{self.location}-{self.job_position}/".replace(" ", "+").lower()
        
        if self.salary:
            salary_code = self.get_salary_code(int(self.salary))
            search_url += f"?salaryfrom={salary_code}"
        
        print(f"Fetching resumes from URL: {search_url}")
        
        page_to_scrape = requests.get(search_url)
        

        if page_to_scrape.status_code == 200:
            soup = BeautifulSoup(page_to_scrape.text, "html.parser")
            resumes = soup.find_all('div', class_='card card-hover card-search resume-link card-visited wordwrap')
            
            resume_data = []

            for resume in resumes:
                link_tag = resume.find('a', href=True)
                
                if link_tag:
                    relative_url = link_tag['href']
                    full_url = "https://www.work.ua" + relative_url  
                    
                    resume_page = requests.get(full_url)
                    if resume_page.status_code == 200:  
                        resume_soup = BeautifulSoup(resume_page.text, "html.parser")
                        parsed_resume = self.parse_resume(resume_soup, full_url) 
                        resume_data.append(parsed_resume)
                    else:
                        print(f"Failed to retrieve resume page: {full_url}")
        else:
            print("Failed to retrieve data from work.ua")
        
        return resume_data  

    def parse_resume(self, resume, link):        
        position_tag = resume.find('h2', class_='mt-lg sm:mt-xl')  
        salary_tag = resume.find('span', class_='text-muted-print')

        position = position_tag.text.strip() if position_tag else "Not specified"
        
        salary_expectation = salary_tag.text.strip().replace("&nbsp;", " ") if salary_tag else "Not specified"
        salary_expectation = salary_expectation.replace(',', '').strip()
        
        experiences = []
        job_edu_titles = resume.find_all('h2', class_='h4 strong-600 mt-lg sm:mt-xl')

        for job_edu_title_element in job_edu_titles:
            title = job_edu_title_element.text.strip() if job_edu_title_element else "Not specified"
            
            company_element = job_edu_title_element.find_next('p', class_='mb-0')
            name_with_duration = company_element.text.strip() if company_element else "Not specified"
    
            if '\n' in name_with_duration:
                name = name_with_duration.split('\n')[-1].strip()
            else:
                name = name_with_duration.strip()

            name = ' '.join(name.split())
            
            additional_info_element = company_element.find_next('p', class_='text-default-7 mb-0')
            additional_info = additional_info_element.text.strip() if additional_info_element else "Not specified"

            duration_element = job_edu_title_element.find_next('span', class_='text-default-7')
            duration = duration_element.text.strip() if duration_element else "Not specified"

            if '(' in duration and ')' in duration:
                duration = duration.replace('(', '').replace(')', '').strip() 
            else:
                duration = "Not specified"  

            if title != "Контактна інформація":
                experiences.append({
                    "title": title,
                    "name": name,
                    "additional_info": additional_info,
                    "duration": duration  
                })
        
        skills = []
        skill_items = resume.find_all('li', class_='no-style mr-sm mt-sm')  

        for skill_item in skill_items:
            skill_name = skill_item.find('span', class_='ellipsis').text.strip() if skill_item.find('span', class_='ellipsis') else "Not specified"
            skills.append(skill_name)

        location = None
        details = resume.find_all('dt')

        for detail in details:
            key = detail.text.strip()
            value = detail.find_next_sibling('dd').text.strip() if detail.find_next_sibling('dd') else "Not specified"

            if "Місто проживання" in key:
                location = value

        add_info_element = resume.find(id="addInfo")
        add_info = add_info_element.text.strip() if add_info_element else "Not specified"

        return {
            "position": position,
            "jobs_and_education": experiences,
            "skills": skills,
            "location": location,
            "salary_expectation": salary_expectation,
            "add_info": add_info,
            "link": link
        }

parser = WorkUaParser()
resumes = parser.fetch_resumes()

for resume in resumes:
    print(json.dumps(resume, indent=4, ensure_ascii=False))
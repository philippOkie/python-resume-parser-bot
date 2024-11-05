import requests
from bs4 import BeautifulSoup

class WorkUaParser:
    BASE_URL = "https://www.work.ua/resumes-it/"

    def fetch_resumes(self):
        page_to_scrape = requests.get(self.BASE_URL)

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
                        parsed_resume = self.parse_resume(resume_soup) 
                        resume_data.append(parsed_resume)
                    else:
                        print(f"Failed to retrieve resume page: {full_url}")
        else:
            print("Failed to retrieve data from work.ua")
        
        return resume_data  

    def parse_resume(self, resume):        
        position_tag = resume.find('h2', class_='mt-lg sm:mt-xl')  
        salary_tag = resume.find('span', class_='text-muted-print')

        position = position_tag.text.strip() if position_tag else "Not specified"
        
        salary_expectation = salary_tag.text.strip().replace("&nbsp;", " ") if salary_tag else "Not specified"
        
        experiences = []
        experience_blocks = resume.find_all('div', class_="resume-experience-item") 

        for block in experience_blocks:
            role = block.find('h3').text.strip() if block.find('h3') else "Not specified"
            duration = block.find('span', class_="text-default-7").text.strip() if block.find('span', class_='text-default-7') else "Not specified"
            
            experiences.append({
                "role": role,
                "duration": duration
            })
        
        skills = []
        skill_items = resume.find_all('li', class_='no-style mr-sm mt-sm')  

        for skill_item in skill_items:
            skill_name = skill_item.find('span', class_='ellipsis').text.strip() if skill_item.find('span', class_='ellipsis') else "Not specified"
            skills.append(skill_name)

            if skill_name != "Not specified":
                skills.append(skill_name)

        location = {}
        details = resume.find_all('dt')  
        for detail in details:
            key = detail.text.strip()  
            value = detail.find_next_sibling('dd').text.strip() if detail.find_next_sibling('dd') else "Not specified"  
            
            if "Місто проживання" in key:
                location["city"] = value

        education = []
        education_blocks = resume.find_all('div', class_='resume-education-item') 
        
        for edu_block in education_blocks:
            edu_name = edu_block.find('p').text.strip() if edu_block.find('p') else "Not specified"
            duration = edu_block.find('span', class_='text-default-7').text.strip() if edu_block.find('span', class_='text-default-7') else "Not specified"

            education.append({
                "institution": edu_name,
                "duration": duration
            })
        
        link = "https://www.work.ua" + resume.find('a')['href']

        return {
            "position": position,
            "experience": experiences,
            "skills": skills,
            "location": location,
            "salary_expectation": salary_expectation,
            "link": link
        }

parser = WorkUaParser()
resumes = parser.fetch_resumes()

for resume in resumes:
    print(resume)
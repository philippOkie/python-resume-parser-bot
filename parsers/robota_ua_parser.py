import requests
import json
from pprint import pprint

class RobotaUaParser:
    BASE_URL = 'https://employer-api.robota.ua/cvdb/resumes'
    headers = {
        'Origin': 'https://robota.ua',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Content-Type': 'application/json'
    }

    city_mapping = {
        'kyiv': 1,
        'dnipro': 4,
        'kharkiv': 21,
        'zaporizhia': 9,
        'odesa': 3,
        'lviv': 2,
        'ukraine': 0
    }

    def __init__(self, job_position, location="-", salary=None, experience=None, english_language=None, keywords=None):
        self.job_position = job_position if job_position != "-" else "3D Designer"  # Default job position
        self.location = location if location != "-" else "ukraine"  # Default location
        self.salary = salary if salary and salary.get("from", 0) != "-" else {"from": 20000, "to": 40000}  # Default salary range
        self.experience = experience if experience != "-" else 2  # Default experience (1-2 years)
        self.english_language = english_language if english_language != "-" else True  # Default: English is required
        self.keywords = keywords if keywords != "-" else self.job_position # Default keyword for search

        self.resumes = []

        # Initialize payload
        self.payload = {
            "page": 0,
            "period": "ThreeMonths",
            "sort": "UpdateDate",
            "searchType": "default",
            "ukrainian": False,
            "onlyDisliked": False,
            "onlyFavorite": False,
            "onlyWithCurrentNotebookNotes": False,
            "showCvWithoutSalary": True,
            "sex": "Any",
            "cityId": 0,
            "inside": False,
            "onlyNew": False,
            "moveability": True,
            "onlyMoveability": False,
            "rubrics": [],
            "languages": [],
            "scheduleIds": [],
            "educationIds": [],
            "branchIds": [],
            "experienceIds": [],
            "keyWords": "3д дизайнер",
            "hasPhoto": False,
            "onlyViewed": False,
            "onlyWithOpenedContacts": False,
            "resumeFillingTypeIds": [],
            "districtIds": [],
            "onlyStudents": False,
            "searchContext": "Main"
        }

    def update_payload(self):
        self.payload["keyWords"] = self.keywords if self.keywords != self.job_position else self.job_position

        if self.location.lower() in self.city_mapping:
            self.payload["cityId"] = self.city_mapping[self.location.lower()]

        if self.salary:
            salary_from = self.salary.get("from", 0)
            if salary_from < 10000:
                salary_from = 20000 
            salary_to = self.salary.get("to", salary_from + 10000)  
            self.payload["salary"] = {
                "from": salary_from,
                "to": salary_to
            }

        if self.experience is not None:
            if self.experience < 1:
                self.payload["experienceIds"] = ["1"]
            elif 1 <= self.experience < 2:
                self.payload["experienceIds"] = ["2"]
            elif 2 <= self.experience < 5:
                self.payload["experienceIds"] = ["3"]
            elif 5 <= self.experience < 10:
                self.payload["experienceIds"] = ["4"]
            else:  # More than 10 years
                self.payload["experienceIds"] = ["5"]

        if self.english_language:
            self.payload["languages"] = ["1"] 
    
    def fetch_resumes(self, page=1):  # Default page is 1
        self.update_payload() 
        self.payload["page"] = page  
        
        response = requests.post(self.BASE_URL, headers=self.headers, json=self.payload)
        if response.status_code != 200:
            print(f"Failed to retrieve data from Robota.ua (Page {page}) - Status Code: {response.status_code}")
            print(f"Response Content: {response.text}")
            return []
        
        try:
            response_data = response.json()
        except requests.JSONDecodeError:
            print("Failed to parse JSON response.")
            return []
        
        print(f"Page {page} response data:")
        print(json.dumps(response_data, indent=4))

        return response_data.get("data", [])  
    
    def fetch_multiple_pages(self, num_pages=10):
        all_resumes = []
        for page in range(1, num_pages + 1):
            print(f"Fetching page {page}...")
            page_resumes = self.fetch_resumes(page)
            if page_resumes:
                all_resumes.extend(page_resumes)

        parsed_resumes = []
        for resume_data in all_resumes:
            # Ensure the fields are being accessed correctly based on the API response
            position = resume_data.get('position', 'N/A')
            salary_expectation = resume_data.get('salary', {}).get('from', 'N/A')  # Assuming salary is nested
            location = resume_data.get('locationName', 'N/A')  # Based on sample, location is in 'locationName'
            add_info = resume_data.get('addInfo', 'N/A')  # Adjust based on actual field name
            skills = resume_data.get('skills', [])
            jobs_and_education = resume_data.get('experience', [])  # Assuming 'experience' is the field for jobs
            resume_link = resume_data.get('url', 'N/A')  # Assuming 'url' holds the resume link

            resume = {
                'position': position,
                'salary_expectation': salary_expectation,
                'location': location,
                'add_info': add_info,
                'skills': skills,
                'jobs_and_education': jobs_and_education,
                'resume_link': resume_link
            }

            parsed_resumes.append(resume)

            # Print formatted resume
            resume_str = f"Position: {position}\n"
            resume_str += f"Salary Expectation: {salary_expectation}\n"
            resume_str += f"Location: {location}\n"
            resume_str += f"Additional Info: {add_info}\n"
            resume_str += f"Skills: {', '.join(skills)}\n"
            resume_str += f"Experience:\n"
            for exp in jobs_and_education:
                title = exp.get('position', 'N/A')
                company = exp.get('company', 'N/A')
                duration = exp.get('datesDiff', 'N/A')
                resume_str += f"\t{title} at {company} ({duration})\n"
            resume_str += f"Resume Link: {resume_link}\n"
            print(resume_str)

        return parsed_resumes


# Parser testing
job_position = "3д дизайнер"
location = "Kyiv"  
parser = RobotaUaParser(job_position, location=location)

all_resumes = parser.fetch_multiple_pages(num_pages=5)

for resume in all_resumes[:3]:
    print(resume)

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

    def __init__(self, job_position, location="", salary=None, experience=None, english_language=None, keywords=None):
        self.job_position = job_position
        self.location = location
        self.salary = salary
        self.experience = experience  
        self.english_language = english_language
        self.keywords = keywords
        self.resumes = []

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
        # Handle city selection
        if self.location.lower() in self.city_mapping:
            self.payload["cityId"] = self.city_mapping[self.location.lower()]

        # Handle salary expectations
        if self.salary:
            salary_from = self.salary.get("from", 0)
            if salary_from < 10000:
                salary_from = 20000  # Set the minimum salary "from" value
            salary_to = self.salary.get("to", salary_from + 10000)  # Default "to" value if not provided
            self.payload["salary"] = {
                "from": salary_from,
                "to": salary_to
            }

        # Handle experience selection
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

        # Handle English language selection
        if self.english_language:
            self.payload["languages"] = ["1"]  # Assuming "1" is for English
    
    def fetch_resumes(self, page):
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
        
        for i, resume in enumerate(all_resumes, 1):
            print(f"Resume {i}:")
            pprint(resume)  
        return all_resumes

job_position = "3д дизайнер"
location = "Kyiv"  
parser = RobotaUaParser(job_position, location=location)

all_resumes = parser.fetch_multiple_pages(num_pages=5)

for resume in all_resumes[:3]:
    print(resume)

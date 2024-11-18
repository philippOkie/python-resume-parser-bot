import requests

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
        self.keywords = keywords if keywords != "-" else self.job_position  # Default keyword for search

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

        try:
            response = requests.post(self.BASE_URL, headers=self.headers, json=self.payload)
            response.raise_for_status()  # Will raise an error for HTTP error codes

            response_data = response.json()
            print(f"Page {page} response data:")
            
            if 'documents' in response_data:
                documents = response_data['documents']
                if not documents:
                    print("No resumes found in the response.")
                return self.parse_documents(documents)
            else:
                print("No documents found in the response.")
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        except requests.exceptions.JSONDecodeError:
            print("Failed to parse JSON response.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        return []

    def parse_documents(self, documents):
        parsed_resumes = []
        for doc in documents:
            full_name = doc.get('fullName', 'N/A')
            city = doc.get('cityName', 'N/A')
            age = doc.get('age', 'N/A')
            speciality = doc.get('speciality', 'N/A')
            salary = doc.get('salary', 'N/A')
            experience = doc.get('experience', [])
            resume_id = doc.get('resumeId', 'N/A')
            
            experience_info = []
            for exp in experience:
                position = exp.get('position', 'N/A')
                company = exp.get('company', 'N/A')
                duration = exp.get('datesDiff', 'N/A')
                experience_info.append(f"{position} at {company} ({duration})")

            resume = {
                'position': speciality,
                'location': city,
                'salary_expectation': salary,
                'skills': experience_info,
                'link': f"https://robota.ua/ru/candidates/{resume_id}"
            }

            parsed_resumes.append(resume)

            # Print formatted resume
            resume_str = f"Full Name: {full_name}\n"
            resume_str += f"Speciality: {speciality}\n"
            resume_str += f"City: {city}\n"
            resume_str += f"Age: {age}\n"
            resume_str += f"Salary: {salary}\n"
            resume_str += f"Experience:\n"
            for exp in experience_info:
                resume_str += f"\t{exp}\n"
            resume_str += f"Resume url: https://robota.ua/ru/candidates/{resume_id}\n"
            print(resume_str)

        return parsed_resumes

    def fetch_multiple_pages(self, num_pages=10):
        all_resumes = []
        for page in range(1, num_pages + 1):
            print(f"Fetching page {page}...")
            page_resumes = self.fetch_resumes(page)
            if page_resumes:
                all_resumes.extend(page_resumes)

        return all_resumes

# Parser testing
# job_position = "3д дизайнер"
# location = "Kyiv"  
# parser = RobotaUaParser(job_position, location=location)

# all_resumes = parser.fetch_multiple_pages(num_pages=5)

# for resume in all_resumes[:3]:
#     print(resume)

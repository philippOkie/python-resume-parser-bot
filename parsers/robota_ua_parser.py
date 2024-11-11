import requests

url = 'https://employer-api.robota.ua/cvdb/resumes'

headers = {
    'Origin': 'https://robota.ua',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0',
    'Content-Type': 'application/json'
}

cookies = {'session_cookie_name': 'your_session_cookie_value'}

payload = {
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

response = requests.post(url, headers=headers, cookies=cookies, json=payload)

if response.status_code == 200:
    try:
        data = response.json()  
        print(data) 
    except requests.JSONDecodeError:
        print("Failed to parse JSON response.")
else:
    print(f"Request failed with status code: {response.status_code}")

from parsers.work_ua_parser import WorkUaParser
from parsers.robota_ua_parser import RobotaUaParser

def get_user_criteria():
    """Prompt the user to enter criteria for filtering resumes."""
    job_position = input("Enter the job position (e.g., Data Scientist, Web Developer): ").strip()
    location = input("Enter the location (e.g., Kyiv, Lviv or leave blank): ").strip()
    salary = input("Enter minimum salary expectation (e.g., 20000 or leave blank for no preference): ").strip()
    
    return {
        "job_position": job_position,
        "location": location,
        "salary": salary if salary else None,
    }

def choose_parser():
    """Prompt user to choose the site to parse resumes from."""
    print("Select job site to parse resumes from:")
    print("1. work.ua")
    print("2. robota.ua")
    site_choice = input("Enter your choice (1 or 2): ").strip()
    
    if site_choice == "1":
        return WorkUaParser, "work.ua"
    elif site_choice == "2":
        return RobotaUaParser, "robota.ua"
    else:
        print("Invalid choice. Please select 1 or 2.")
        return None, None

def display_resumes(resumes):
    """Display the parsed resumes in a readable format."""
    if resumes:
        print(f"\nFound {len(resumes)} resumes:")
        for idx, resume in enumerate(resumes, start=1):
            print(f"\nResume {idx}:")
            print(f"Name: {resume.get('name', 'N/A')}")
            print(f"Position: {resume.get('position', 'N/A')}")
            print(f"Experience: {resume.get('experience_years', 'N/A')} years")
            print(f"Skills: {', '.join(resume.get('skills', []))}")
            print(f"Location: {resume.get('location', 'N/A')}")
            print(f"Salary Expectation: {resume.get('salary_expectation', 'N/A')}")
            print(f"Link: {resume.get('link', 'N/A')}")
    else:
        print("No resumes found based on the given criteria.")

def main():
    criteria = get_user_criteria()

    parser_class, site_name = choose_parser()
    if not parser_class:
        return  

    parser = parser_class(**criteria)
    print(f"Fetching resumes from {site_name}...")

    try:
        parser.fetch_resumes()
        display_resumes(parser.resumes)
    except Exception as e:
        print(f"An error occurred while fetching resumes: {e}")

if __name__ == "__main__":
    main()
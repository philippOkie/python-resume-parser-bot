from parsers.work_ua_parser import WorkUaParser

def get_user_criteria():
    """Prompt the user to enter criteria for filtering resumes."""
    job_position = input("Enter the job position (e.g., Data Scientist, Web Developer): ").strip()
    location = input("Enter the location (e.g., Kyiv, Lviv or leave blank): ").strip()
    salary = input("Enter salary budget expectation (e.g., 20000 or leave blank for no preference): ").strip()
    years_of_experience = input("Enter minimum years of experience (e.g. 7 or leave blank for no preference): ").strip()
    english_language = input("Is English language knowledge required? (type yes or leave blank): ").strip().lower()
    keywords = input("Enter keywords (e.g., data analyst python sql or leave blank): ").strip()

    return {
        "job_position": job_position,
        "location": location if location else None,
        "salary": salary if salary else None,
        "years_of_experience": years_of_experience if years_of_experience else None,
        "english_language": english_language if english_language in ["yes", "no"] else None,
        "keywords": keywords if keywords else None 
    }

def choose_parser():
    """Prompt user to choose the site to parse resumes from."""
    print("Select job site to parse resumes from:")
    print("1. work.ua")
    print("2. robota.ua")
    site_choice = input("Enter your choice (1 or 2): ").strip()
    
    if site_choice == "1":
        return WorkUaParser, "work.ua"
    else:
        print("Invalid choice. Please select 1 or 2.")
        return None, None

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

    # Sort resumes first by relevance score and then by position name
    return sorted(resumes, key=lambda x: (calculate_relevance(x), x.get("position", "").lower()), reverse=True)

def display_resumes(resumes):
    """Display the parsed resumes in a readable format, limited to 10 resumes."""
    if resumes:
        limited_resumes = resumes[:10]
        print(f"\nFound {len(resumes)} resumes, displaying up to 10:")
        for idx, resume in enumerate(limited_resumes, start=1):
            print(f"\nResume {idx}:")
            print(f"Position: {resume.get('position', 'N/A')}")
            print(f"Location: {resume.get('location', 'N/A')}")
            print(f"Salary Expectation: {resume.get('salary_expectation', 'N/A')}")
            print(f"Skills: {resume.get('skills', 'N/A')} ")
            print(f"Additional info: {resume.get('additional_info', 'N/A')}")
            print(f"Link: {resume.get('link', 'N/A')}")
    else:
        print("No resumes found based on the given criteria.")

def save_resumes_to_file(resumes, filename="resumes.txt"):
    """Save the fetched resumes to a text file."""
    with open(filename, 'w', encoding='utf-8') as file:
        for resume in resumes:
            file.write(f"Position: {resume.get('position', 'N/A')}\n")
            file.write(f"Location: {resume.get('location', 'N/A')}\n")
            file.write(f"Salary Expectation: {resume.get('salary_expectation', 'N/A')}\n")
            file.write(f"Link: {resume.get('link', 'N/A')}\n")
            file.write("\n" + "-"*40 + "\n\n")  

    print(f"Resumes saved to {filename}")

def main():
    criteria = get_user_criteria()

    parser_class, site_name = choose_parser()
    if not parser_class:
        return  

    parser = parser_class(
        job_position=criteria["job_position"], 
        location=criteria["location"], 
        salary=criteria["salary"],
        experience=criteria["years_of_experience"],
        english_language=criteria["english_language"],
        keywords=criteria["keywords"] 
    )
    
    print(f"Fetching resumes from {site_name}...")

    try:
        resumes = parser.fetch_resumes()

        sorted_resumes = sort_resumes_by_relevance(
            resumes,
            keywords=criteria["keywords"].split(",") if criteria["keywords"] else [],
            salary=criteria["salary"],
            experience=int(criteria["years_of_experience"]) if criteria["years_of_experience"] else 0,
            english_language=criteria["english_language"] or 'no'
        )

        display_resumes(sorted_resumes)
        save_resumes_to_file(sorted_resumes) 
    except Exception as e:
        print(f"An error occurred while fetching resumes: {e}")

if __name__ == "__main__":
    main()
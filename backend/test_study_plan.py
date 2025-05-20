import requests
import json

# Sample data for testing
sample_data = {
    "subjects": [
        {
            "name": "Mathematics",
            "chapters": ["Algebra", "Geometry", "Trigonometry", "Calculus"],
            "exam_date": "2025-05-30"
        },
        {
            "name": "Physics",
            "chapters": ["Mechanics", "Thermodynamics", "Electromagnetism", "Modern Physics"],
            "exam_date": "2025-06-05"
        },
        {
            "name": "Chemistry",
            "chapters": ["Organic", "Inorganic", "Physical", "Analytical"],
            "exam_date": "2025-06-10"
        }
    ],
    "daily_hours": 4.0,
    "start_date": "2025-05-20"
}

# Send request to the API
response = requests.post('http://localhost:8000/generate-plan/', json=sample_data)

# Print the response
print("\nGenerated Study Plan:")
print("-" * 80)

if response.status_code == 200:
    study_plan = response.json()["study_plan"]
    
    # Print in a readable format
    for day in study_plan:
        print(f"\nDate: {day['date']}")
        print("-" * 20)
        for item in day['plan']:
            print(f"Subject: {item['subject']}")
            print(f"Chapter: {item['chapter']}")
            print(f"Hours: {item['hours']:.2f}")
            print("-" * 20)
else:
    print(f"Error: {response.status_code}")
    print(response.text)

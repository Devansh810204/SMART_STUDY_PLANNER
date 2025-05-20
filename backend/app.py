from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta
import json

app = FastAPI(title="Smart Study Planner API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Subject(BaseModel):
    name: str
    chapters: List[str]
    exam_date: str
    difficulty: int  # 1 (easy) to 5 (very difficult)

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Subject name is required')
        return v.strip()

    @validator('exam_date')
    def validate_exam_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError('Invalid date format. Please use YYYY-MM-DD')
        return v

    @validator('difficulty')
    def validate_difficulty(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Difficulty must be between 1 and 5')
        return v

    @validator('chapters')
    def validate_chapters(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one chapter is required')
        return v

class StudyPlanRequest(BaseModel):
    subjects: List[Subject]
    daily_hours: float
    start_date: str

    @validator('daily_hours')
    def validate_daily_hours(cls, v):
        if v <= 0:
            raise ValueError('Daily hours must be greater than 0')
        return v

    @validator('start_date')
    def validate_start_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError('Invalid start date format. Please use YYYY-MM-DD')
        return v

    @validator('subjects')
    def validate_subjects(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one subject is required')
        return v

def generate_study_plan(request: StudyPlanRequest):
    """
    Generate a study plan that:
    1. Prioritizes subjects based on exam dates
    2. Removes subjects after their exam dates
    3. Adjusts study hours based on difficulty
    4. Ensures all chapters are covered before exams
    """
    # Convert input dates to datetime objects
    start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
    
    # Calculate days until each exam and difficulty factor
    subjects_with_days = []
    for subject in request.subjects:
        exam_date = datetime.strptime(subject.exam_date, "%Y-%m-%d")
        days_until_exam = (exam_date - start_date).days
        difficulty_factor = subject.difficulty / 5.0  # Normalize to 0-1 range
        subjects_with_days.append({
            "name": subject.name,
            "chapters": subject.chapters,
            "exam_date": exam_date,
            "difficulty_factor": difficulty_factor,
            "total_chapters": len(subject.chapters)
        })
    
    # Sort subjects by exam date (closest first) and difficulty (higher difficulty first)
    subjects_with_days.sort(key=lambda x: (x["exam_date"], -x["difficulty_factor"]))
    
    # Calculate initial distribution of hours
    total_chapters = sum(len(subject["chapters"]) for subject in subjects_with_days)
    base_hours_per_chapter = request.daily_hours / total_chapters
    
    # Create study plan
    study_plan = []
    current_date = start_date
    
    while subjects_with_days:
        # Calculate remaining hours for today
        daily_hours = request.daily_hours
        daily_plan = []
        
        # Remove subjects that have already had their exams
        subjects_with_days = [s for s in subjects_with_days if s["exam_date"] >= current_date]
        
        # Calculate dynamic hours distribution based on remaining subjects
        total_remaining_chapters = sum(s["total_chapters"] for s in subjects_with_days)
        if total_remaining_chapters > 0:
            dynamic_hours_per_chapter = daily_hours / total_remaining_chapters
        else:
            break
        
        # Assign chapters based on priority
        for subject in subjects_with_days[:]:
            if len(subject["chapters"]) > 0 and subject["exam_date"] >= current_date:
                chapter = subject["chapters"][0]
                # Adjust hours based on difficulty and remaining chapters
                hours_needed = dynamic_hours_per_chapter * (1 + subject["difficulty_factor"])
                
                if hours_needed <= daily_hours:
                    daily_plan.append({
                        "subject": subject["name"],
                        "chapter": chapter,
                        "hours": hours_needed
                    })
                    daily_hours -= hours_needed
                    subject["chapters"].pop(0)
                    
                    # Update total chapters for this subject
                    subject["total_chapters"] = len(subject["chapters"])
                    
                    # If all chapters of a subject are completed, remove it
                    if len(subject["chapters"]) == 0:
                        subjects_with_days.remove(subject)
                else:
                    break
        
        if daily_plan:
            # Format hours and minutes
            formatted_plan = []
            for item in daily_plan:
                hours = int(item["hours"])
                minutes = int((item["hours"] - hours) * 60)
                formatted_plan.append({
                    "subject": item["subject"],
                    "chapter": item["chapter"],
                    "time": f"{hours}h {minutes}m"
                })
            
            study_plan.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "plan": formatted_plan
            })
        
        current_date += timedelta(days=1)
        
        # If we've reached the last exam date, stop
        if current_date > max(s["exam_date"] for s in subjects_with_days):
            break
    
    return study_plan

@app.post("/generate-plan/")
async def generate_plan(request: StudyPlanRequest):
    try:
        # Validate request
        request.validate()
        
        # Generate plan
        plan = generate_study_plan(request)
        
        # Validate plan
        if not plan or len(plan) == 0:
            raise HTTPException(status_code=400, detail="Failed to generate study plan")
            
        return {"study_plan": plan}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

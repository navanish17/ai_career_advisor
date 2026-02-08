"""
Script to expand the intent training dataset for better accuracy.
Run this script to generate a larger, more balanced dataset.

Usage: python expand_training_data.py
"""

import json
from pathlib import Path

# Additional training examples to add
NEW_EXAMPLES = {
    "greeting": [
        "hiii", "helloo", "heyy", "wassup", "sup", "hola", "bonjour",
        "good day", "hi career bot", "hello ai", "hey assistant",
        "hi there bot", "hello hello", "hey hey", "morning sir",
        "evening sir", "good night", "namaskar", "pranam", "ssup",
        "hi ji", "hello ji", "kya haal", "theek ho", "sab badhiya",
        "how do you do", "nice to meet you", "hi can you help",
        "hello i need help", "hey need guidance", "hi i have a question",
        "hello there friend", "hey can we talk", "hi im new here",
        "hello first time here", "hey i just joined", "hi looking for help",
        "hello seeking advice", "hey need some info", "hi quick question",
        "hello there assistant", "hey bot are you there", "hi anyone there",
        "hello is anyone home", "hey wake up", "hi are you active",
        "hello can you hear me", "hey respond please", "hi testing",
        "hello world", "hey universe", "hi planet", "hello everyone",
        "hey all", "hi guys", "hello folks", "hey people", "hi team",
        "hello dear", "hey buddy boy", "hi pal", "hello mate", "hey dude",
        "hi bro", "hello sis", "hey friend", "hi amigo", "hello comrade"
    ],
    "farewell": [
        "byee", "byebye", "goodbyee", "see ya later", "catch you later",
        "gotta go", "have to leave", "need to go now", "time to go",
        "i should go", "leaving now", "signing off", "logging out",
        "im done for today", "thats all i needed", "you helped a lot",
        "thanks for everything", "appreciate your help", "grateful for this",
        "you were helpful", "this was useful", "got my answers", "im satisfied",
        "no more doubts", "all clear now", "understood everything", "crystal clear",
        "makes sense now", "got it thanks", "okay understood", "alright bye",
        "fine thanks bye", "cool thanks", "awesome thanks", "great help thanks",
        "wonderful assistance", "excellent help", "superb guidance", "amazing support",
        "alvida", "phir milenge", "chalta hu", "nikal raha hu", "ab jata hu",
        "bohot shukriya", "dhanyawad", "bahut achha laga", "maza aaya",
        "take care bye", "stay safe bye", "keep well", "be good", "all the best",
        "good luck", "best wishes", "wishing you well", "have a great day",
        "have a nice day", "enjoy your day", "talk soon", "until next time",
        "see you soon", "see you around", "catch up later", "lets talk again",
        "come back soon", "visit again", "remember me", "dont forget me"
    ],
    "career_query": [
        "kaise banu software engineer", "data scientist kaise bane",
        "doctor banne ke liye kya karna padega", "engineer kaise bante hain",
        "IAS officer banne ka tarika", "CA kaise bane india mein",
        "pilot banne ke liye kya chahiye", "lawyer kaise bane",
        "teacher banne ke liye", "scientist kaise bane ISRO mein",
        "what to do for becoming engineer", "steps for doctor career",
        "process to become CA", "way to become IAS", "method to become pilot",
        "tell about software jobs", "explain data science field",
        "describe engineering career", "elaborate on medical career",
        "discuss IT industry jobs", "scope in machine learning",
        "prospects in artificial intelligence", "opportunities in cyber security",
        "growth in cloud computing", "demand for web developers",
        "is software engineering good", "is data science worth it",
        "is medical field good", "is engineering saturated", "is IT good now",
        "software developer job description", "data analyst work profile",
        "product manager responsibilities", "business analyst role",
        "devops engineer duties", "best career options 2025", "trending careers",
        "emerging job fields", "future proof careers", "recession proof jobs",
        "how much does software engineer earn", "data scientist package",
        "CA salary in india", "doctor income per month", "IAS officer salary",
        "career after 12th science PCM", "career after 12th science PCB",
        "career after 12th commerce", "career after 12th arts",
        "job options after graduation", "career scope in india",
        "career opportunities for freshers", "entry level jobs in tech",
        "career change at 30", "career switch from non-tech"
    ],
    "college_query": [
        "best colleges for btech", "top university for engineering",
        "good colleges for computer science", "famous colleges in delhi",
        "reputed institutes in bangalore", "top schools for mba",
        "IIT kaise join kare", "NIT mein admission kaise milega",
        "BITS mein kaise jaye", "IIM mein kaise ghuse",
        "college fees kitni hai", "hostel facilities kaisi hai",
        "placement record kya hai", "campus recruitment kaisa hai",
        "tell about iit bombay", "info about iit delhi", "details of iit madras",
        "review of nit trichy", "feedback on bits pilani",
        "which college is better IIT or NIT", "IIT vs BITS comparison",
        "private vs government college", "top 5 engineering colleges",
        "top 10 medical colleges", "top 3 law colleges", "best architecture college",
        "collegedunia ranking", "nirf ranking 2025", "qs ranking india",
        "times higher education ranking", "college rank for placements",
        "cheapest good engineering college", "affordable medical colleges",
        "low fees high quality college", "scholarship available colleges",
        "deemed university vs state university", "autonomous college benefits",
        "college in pune for engineering", "mumbai best btech college",
        "hyderabad top tech colleges", "chennai engineering institutes",
        "kolkata best universities", "best college for CS in UP", 
        "top polytechnic colleges", "diploma colleges in maharashtra"
    ],
    "roadmap_request": [
        "give me a roadmap", "create path for me", "design my journey",
        "chart my course", "map my career", "plan my future",
        "roadmap banao", "path batao", "rasta dikhao", "guide karo",
        "kaise karu start", "kahan se shuru karu", "first step kya hai",
        "beginning se batao", "zero se hero kaise banu",
        "month by month plan", "week by week guide", "day by day schedule",
        "yearly plan for career", "2 year roadmap", "5 year career plan",
        "detailed steps to become", "complete guide for", "full tutorial for",
        "a to z for becoming", "everything about becoming",
        "i want to be software developer what to do", "want to become doctor guide me",
        "aspiring CA need roadmap", "future IAS officer roadmap",
        "planning to be engineer", "thinking of becoming lawyer",
        "roadmap for machine learning engineer", "path to data scientist",
        "journey to become devops", "route to cloud architect",
        "roadmap after 10th for engineering", "roadmap after 12th for medical",
        "roadmap for commerce student", "roadmap for arts student",
        "how to proceed step by step", "what are the milestones",
        "what should be my targets", "how to track my progress",
        "create learning roadmap", "skill development roadmap",
        "certification roadmap for IT", "upskilling roadmap"
    ],
    "exam_query": [
        "jee kya hota hai", "neet exam kya hai", "upsc kaise crack kare",
        "gate exam ke baare mein batao", "cat preparation tips",
        "clat syllabus kya hai", "gre score kitna chahiye",
        "ielts band requirement", "toefl score for usa",
        "exam date kab hai", "registration kaise kare", "form kaise bhare",
        "admit card kaise download kare", "result kab aayega",
        "passing marks kitne hai", "cutoff kya hoga", "previous year cutoff",
        "expected cutoff 2025", "difficulty level of exam",
        "how hard is jee advanced", "is neet tougher than jee",
        "which is easier cat or gmat", "gre vs gmat difficulty",
        "exam pattern for ssc", "marking scheme of upsc",
        "negative marking in jee", "sectional cutoff in cat",
        "best books for exam preparation", "recommended study material",
        "coaching vs self study", "online classes for exam",
        "mock test series", "previous year papers", "sample papers download",
        "question bank for jee", "practice set for neet",
        "time management in exam", "how to attempt paper",
        "revision strategy for exam", "last minute tips for exam"
    ],
    "degree_query": [
        "btech kya hai", "mba ka matlab", "mbbs course details",
        "bca course information", "mca kya hota hai", "bba course structure",
        "bcom syllabus", "ba subjects", "bsc branches",
        "what is dual degree", "integrated course meaning",
        "honours degree vs regular", "distance learning valid hai kya",
        "online degree value", "part time mba worth it",
        "btech duration", "mba kitne saal ka hai", "mbbs length",
        "phd kitne saal", "diploma vs degree", "certificate vs diploma",
        "btech cse vs it", "mechanical vs electrical engineering",
        "civil vs architecture", "ece vs eee difference",
        "bcom vs bba which is better", "bca vs bsc cs",
        "mba vs mtech salary", "ms vs mtech abroad",
        "regular vs correspondence", "full time vs part time course",
        "degree recognition by ugc", "aicte approved courses",
        "naac accredited colleges", "degree validity for jobs"
    ],
    "recommendation_request": [
        "mujhe batao kya karu", "kya suitable hai mere liye",
        "meri situation mein kya best hai", "mere interest ke hisaab se",
        "mere marks ke according", "mere budget mein kya milega",
        "mere liye best option", "mujhe guide karo",
        "confused hu kya karu", "samajh nahi aa raha", "help me choose",
        "i am lost", "dont know what to pick", "no idea what to do",
        "clueless about career", "need direction in life",
        "based on my profile", "according to my background",
        "considering my situation", "given my constraints",
        "for someone like me", "in my case what should i do",
        "what would you suggest", "your recommendation please",
        "what do you think is best", "in your opinion",
        "science lena chahiye ya commerce", "pcm vs pcb",
        "arts vs commerce after 10th", "which stream is better",
        "cse vs mechanical", "it vs ece", "core vs non-core",
        "service vs product company", "startup vs mnc",
        "should i do mba or mtech", "masters in india vs abroad",
        "job vs higher studies", "coding vs management track"
    ],
    "off_topic": [
        "aaj ka mausam kaisa hai", "cricket score batao",
        "film ka review do", "song suggest karo", "joke sunao",
        "story batao", "game khelte hain", "chat karte hain",
        "timepass karte hain", "bakwas karte hain",
        "who is the president", "capital of state", "history of india",
        "geography fact", "science experiment", "math problem solve karo",
        "do my homework", "write my essay", "complete my assignment",
        "code likhdo mere liye", "project bana do",
        "relationship advice", "love tips", "friendship help",
        "family problem", "personal issue",
        "health advice", "diet plan", "workout routine", "yoga tips",
        "meditation technique", "mental health help",
        "shopping suggestion", "product review", "phone comparison",
        "laptop recommendation", "gadget review",
        "travel suggestion", "hotel booking", "flight ticket",
        "train timing", "bus route",
        "food recipe", "cooking tips", "restaurant review",
        "cafe suggestion", "street food places",
        "movie streaming", "web series suggestion", "youtube video",
        "instagram reels", "tiktok trend", "social media tips",
        "crypto investment", "stock market tips", "mutual funds",
        "insurance advice", "loan help",
        "astrology prediction", "horoscope today", "lucky number",
        "dream meaning", "palm reading"
    ]
}

def main():
    # Load existing data
    data_path = Path(__file__).parent / "intent_training_data.json"
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    existing_count = len(data['training_data'])
    print(f"Existing examples: {existing_count}")
    
    # Count existing per label
    from collections import Counter
    existing_labels = Counter(item['label'] for item in data['training_data'])
    print("\nBefore expansion:")
    for label, count in sorted(existing_labels.items()):
        print(f"  {label}: {count}")
    
    # Add new examples
    added = 0
    for label, examples in NEW_EXAMPLES.items():
        for text in examples:
            data['training_data'].append({
                "text": text,
                "label": label
            })
            added += 1
    
    print(f"\nAdded {added} new examples")
    print(f"Total now: {len(data['training_data'])}")
    
    # Count after
    new_labels = Counter(item['label'] for item in data['training_data'])
    print("\nAfter expansion:")
    for label, count in sorted(new_labels.items()):
        print(f"  {label}: {count}")
    
    # Save expanded data
    output_path = Path(__file__).parent / "intent_training_data_expanded.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nExpanded data saved to: {output_path}")
    print("Upload this file to Kaggle for better training!")

if __name__ == "__main__":
    main()

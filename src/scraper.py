import os
import praw
import re
import json
import sys

CLIENT_ID     = os.getenv('PRAW_CLIENT_ID')
CLIENT_SECRET = os.getenv('PRAW_CLIENT_SECRET')
USERNAME      = os.getenv('PRAW_USERNAME')
PASSWORD      = os.getenv('PRAW_PASSWORD')
USER_AGENT    = "Intern Salary Scraper https://github.com/dillionverma/intern-salaries"

reddit = praw.Reddit(client_id=CLIENT_ID, \
                     client_secret=CLIENT_SECRET, \
                     username=USERNAME, \
                     password=PASSWORD, \
                     user_agent=USER_AGENT)

subreddit = reddit.subreddit('cscareerquestions')

data = []

for submission in subreddit.search('[OFFICIAL] Salary Sharing thread for INTERNS', sort="new"):
    if "[OFFICIAL]" not in submission.title:
        continue
      
    # Extract month and year from title
    month, year = submission.title[submission.title.find("::")+3:].split()
    # remove comma from month (edge case)
    if month[-1] == ",":
        month = month[:-1]
        
    print(submission.title)
    print("- num_comments: ", int(submission.num_comments))

    submission.comments.replace_more(limit=0, threshold=0)
    for comment in submission.comments.list():
        body = comment.body

        # Remove markdown formatting in comment
        body = re.sub('>|\*|^$\n', "", body)

        # Extract all after ":" in line
        # assumes that data doesn't extend over multiple lines
        extract = lambda line: line[line.find(":")+1:].strip()

        data_point = {
            "school": None,
            "prior_experience": None,
            "offers": [],
            "month": month,
            "year": int(year)
        }

        offer = {}
        for line in body.splitlines():
            if "School/Year" in line:
                data_point["school"] = extract(line)
            elif "Prior Experience" in line:
                data_point["prior_experience"] = extract(line)
            elif "Company/Industry" in line:
                offer["company"] = extract(line)
            elif "Title" in line:
                offer["title"] = extract(line)
            elif "Location" in line:
                offer["location"] = extract(line)
            elif "Duration" in line:
                offer["duration"] = extract(line)
            elif "Salary" in line:
                offer["salary"] = extract(line)
            elif "Relocation" in line:
                offer["relocation"] = extract(line)
                data_point["offers"].append(offer.copy())
                offer.clear()

        # If valid data_point
        if data_point["offers"]:
            data.append(data_point)
    
with open("salaries.json", 'w') as f:
    json.dump(data, f, ensure_ascii=False)
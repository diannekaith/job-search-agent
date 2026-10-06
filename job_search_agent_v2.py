from openai import OpenAI
from dotenv import load_dotenv
from notion_client import Client
import os
from datetime import date, datetime
import json

load_dotenv()

client = OpenAI()

notion = Client(auth=os.getenv("NOTION_TOKEN"))

DATABASE_ID = "607dd64c-2cd0-4134-bae9-0bbbe0798afe"
DATA_SOURCE_ID = "c6d9ad47-137c-48bb-8b74-822d07ee4bfc"

def job_already_exists(job_url):
    results = notion.data_sources.query(
        data_source_id=DATA_SOURCE_ID,
        filter={
            "property": "Job URL",
            "url": {
                "equals": job_url
            }
        }
    )

    return len(results["results"]) > 0

def add_job_to_notion(job):
    notion.pages.create(
        parent={"data_source_id": DATA_SOURCE_ID},
        properties={
            "Role / Company": {
                "title": [
                    {
                        "text": {
                            "content": job["role_company"]
                        }
                    }
                ]
            },
            "Job Title": {
                "rich_text": [
                    {
                        "text": {
                            "content": job["job_title"]
                        }
                    }
                ]
            },
            "Company": {
                "rich_text": [
                    {
                        "text": {
                            "content": job["company"]
                        }
                    }
                ]
            },
            "Job URL": {
                "url": job["job_url"]
            },
            "Posting Date": (
                {"date": None}
                if job["posting_date"].lower() =="unknown"
                else {
                    "date": {
                        "start": job["posting_date"]
                    }
                }    
            ),
            "Date Found": {
                "date": {
                    "start": job["date_found"]
                }
            },
            "Location": {
                "select": {
                    "name": job["location"]
                }
            },
            "Work Type": {
                "select": {
                    "name": job["work_type"]
                }
            },
            "Salary": {
                "rich_text": [
                    {
                        "text": {
                            "content": job["salary"]
                        }
                    }
                ]
            },
            "Meta Ads Fit": {
                "select": {
                    "name": job["meta_ads_fit"]
                }
            },
            "Priority": {
                "select": {
                    "name": job["priority"]
                }
            },
            "Status": {
                "select": {
                    "name": "To Apply"
                }
            },
            "Notes": {
                "rich_text": [
                    {
                        "text": {
                            "content": job["notes"]
                        }
                    }
                ]
            }
        }
    )
conversation_history =[]

while True:
    user_message = input ("You: ")
    conversation_history.append(user_message)
    
    if user_message.lower() in ["quit", "exit"]:
        print("Agent: Goodbye!")
        break

    if user_message.lower() in ["hello", "hi", "hey", "good morning", "good afternoon"]:
        print("Agent: Hello, Kaith! How can I help with your job search?")
        continue

    intent_response = client.responses.create(
        model="gpt-5.6",
        input=f"""
    Decide whether this message is asking for a job search.

    User message:
    {user_message}

    Reply with ONLY:
    SEARCH
    or
    CHAT
    """
    )

    intent = intent_response.output_text.strip()

    if intent == "CHAT":
        print("Agent: I can help with your job search. Tell me what kind of roles you're looking for.")
        continue

    
    response = client.responses.create(
        model="gpt-5.6-luna",
        tools=[{"type": 'web_search'}],
        input=f"""
    You are Kaith's job search assistant.

    USER REQUEST:
    {user_message}

    JOB FRESHNESS REQUIREMENTS

    - Only include jobs that were originally posted within the last 3 months.
    - Prefer jobs originally posted within the last 1 month.
    - If a job is more than 3 months old, exclude it.
    - Exclude jobs that are expired, closed, filled, or no longer accepting applications.
    - Do not treat a recently updated, refreshed, or reposted listing as a newly posted job if the original posting date is older.
    - Check the original job posting date and current application status whenever the listing provides that information.
    - If the original posting date cannot be verified, do not assume the job is new. Only include the job if the listing clearly appears active and relevant.
    - For "posting_date", return ONLY the original posting date in YYYY-MM-DD format when it can be verified.
    - If the original posting date cannot be verified, return exactly "unknown".
    - Do not return phrases such as "unknown / not available", "not provided", "recently posted", "2 days ago", or any other text in the posting_date field.

    Find and recommend jobs that match this profile:
    - Based in the UK
    - Open to remote, hybrid and office-based roles
    - Prioritise Leeds and Manchester for office-based and hybrid roles
    - Include relevant UK-based roles in other locations, including London
    - Include roles that offer visa sponsorship, regardless of UK location, where the role otherwise matches the profile
    - Flag UK eligibility and sponsorship separately
    - Do not assume sponsorship is available unless the job listing or employer information indicates it
    - Junior to mid-level roles

    - Interested in Paid Media, Paid Social, PPC, Performance Marketing, Media Buying and Digital Marketing
    - Target roles include Paid Media Executive, Paid Media Specialist, Paid Social Executive, Paid Social Specialist, PPC Executive, Performance Marketing Executive, Digital Marketing Executive, Media Buyer, Business Analyst, Project Manager and related roles
    - Prioritise paid media and digital marketing roles, but also identify suitable Business Analyst and Project Management opportunities as alternative career paths

    - Hands-on experience with Meta Ads and Meta Ads Manager
    - Developing Google Ads experience
    - Experience with GA4, CRM, WordPress and digital marketing

    CANDIDATE PROFILE

    Education:
    - MSc Digital Marketing, University of Salford — Merit

    Current experience:
    - Marketing Executive & Media Buyer at Squarefoot Investment Ltd.
    - Hands-on experience managing Meta Ads and Meta Ads Manager
    - Set up and launched the company's first Meta Ads account
    - Manage paid social campaigns across Facebook and Instagram
    - Experience with audience targeting, creative testing, ad copy, campaign monitoring and reporting
    - Experience with digital marketing, social media and website redevelopment

    Previous experience:
    - E-commerce marketing and paid advertising
    - Hands-on experience running advertising campaigns and analysing campaign performance
    - Property marketing and sales experience
    - Project management and non-profit project experience

    Paid media skills:
    - Strong hands-on Meta Ads experience
    - Experienced with Meta Ads Manager, Facebook Ads and Instagram Ads
    - Experience with audience targeting, retargeting, creative testing, ad copy, campaign optimisation and performance monitoring
    - Google Ads: no hands-on professional experience yet, but understands the fundamentals of Google Ads, PPC, keywords, targeting, bidding and campaign structure
    - GA4: foundational knowledge
    - Google Search Console and Keyword Planner: familiar with the fundamentals

    Other technical and marketing skills:
    - CRM
    - WordPress
    - Canva, Figma, Photoshop, Lightroom and CapCut
    - Rightmove and Zoopla
    - AI-assisted marketing workflows

    Career level:
    - Primarily target junior to mid-level roles
    - Also consider more senior roles when the requirements are reasonably close to Kaith's experience
    - Do not reject a role solely because it asks for Google Ads experience if the rest of the role is a strong match, but clearly flag the Google Ads experience gap

    Search for current job listings that match this profile.

    Search worldwide, but only include jobs where someone living in the UK appears eligible to apply.


    JOB SEARCH SOURCES

    Search broadly across the public web for relevant job opportunities.

    Use a wide range of accessible sources, including:
    - Official company careers pages
    - Company application portals and ATS platforms
    - LinkedIn
    - Recruitment agency websites
    - Public job listings indexed by search engines
    - Other relevant websites where genuine, active vacancies can be verified

    Do not rely primarily on large job-board platforms such as Indeed, Reed, Totaljobs, CV-Library or Glassdoor.

    When the same vacancy appears on multiple sources, prefer the original employer's careers page or application page where available. LinkedIn is an acceptable source.

    Use web search broadly rather than restricting the search to a specific job platform.

    For each job, provide:
    - Job title
    - Company
    - Location
    - Remote/hybrid/on-site
    - Salary, if available
    - UK eligibility: Yes, No, or Unclear
    - Sponsorship: Yes, No, or Unknown
    - Job link
    - A short explanation of why the role matches Kaith's profile

    Prioritise strong matches in paid media, paid social, PPC, performance marketing and digital marketing. Also include suitable Business Analyst and Project Management roles where relevant.

    Do not invent job listings or details. If information is unavailable, say Unknown.

    For every job you find, evaluate it individually using this format:

    Fit: Strong / Good / Possible / Weak
    Why it fits: Explain the specific parts of the job that match Kaith's experience and qualifications.
    Main gap: Identify the most important requirement or qualification that Kaith does not fully meet.
    Location: State the job location.
    Work type: Remote / Hybrid / On-site.
    Salary: State the advertised salary or "Not stated".
    UK eligibility: State whether the listing appears to accept applicants living and working in the UK. Do not assume eligibility if the listing does not provide enough information.
    Sponsorship: Yes / No / Unknown. Only say Yes if the listing or reliable employer information indicates sponsorship is available. Do not assume sponsorship.
    Application priority: High / Medium / Low.

    Evaluate each job independently.

    Do not provide an overall observations section, overall summary, recommended application order, ranking, or comparison of the jobs.

    After the final job evaluation, stop.
    """,
    text={
        "format": {
            "type": "json_schema",
            "name": "job_search_results",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "jobs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "job_title": {
                                    "type": "string"
                                },
                                "company": {
                                    "type": "string"
                                },
                                "job_url": {
                                    "type": "string"
                                },
                                "fit": {
                                    "type": "string"
                                },
                                "why_it_fits": {
                                    "type": "string"
                                },
                                "main_gap": {
                                    "type": "string"
                                },
                                "priority": {
                                    "type": "string"
                                },
                                "location": {
                                    "type": "string"
                                },
                                "work_type": {
                                    "type": "string"
                                },
                                "salary": {
                                    "type": "string"
                                },
                                "uk_eligibility": {
                                    "type": "string"
                                },
                                "sponsorship": {
                                    "type": "string"
                                },
                                "posting_date": {
                                    "type": "string"
                                }
                                
                            },
                            "required": [
                                "job_title",
                                "company",
                                "job_url",
                                "fit",
                                "why_it_fits",
                                "main_gap",
                                "location",
                                "work_type",
                                "salary",
                                "uk_eligibility",
                                "sponsorship",
                                "priority",
                                "posting_date"
                            ]
                        }
                    }
                },
                "required": [
                    "jobs"
                ]
            }
        }
    }
    )

    data = json.loads(response.output_text)

    print(f"Found {len(data['jobs'])} jobs.")

    for job in data["jobs"]:

        date_found = date.today().isoformat()   

        posting_date = job["posting_date"]

        if posting_date.lower() == "unknown":
            posting_date_obj = None
        else:
            try:
                posting_date_obj = datetime.strptime(posting_date, "%Y-%m-%d").date()
            except ValueError:
                print(f"SKIPPED - invalid posting date: {job['job_title']} - {job['company']}")
                continue

        if posting_date_obj is not None:
            days_old = (date.today() - posting_date_obj).days

            if days_old > 90:
                print(f"SKIPPED — older than 3 months: {job['job_title']} — {job['company']}")
                continue

            if days_old < 0:
                print(f"SKIPPED — invalid future posting date: {job['job_title']} — {job['company']}")
                continue

        job_url = job["job_url"]
        
        if job_already_exists(job_url):
            print(f"SKIPPED — already in Notion: {job['job_title']} — {job['company']}")
            continue

        if job["fit"] == "Possible":
            meta_ads_fit = "Maybe"
        else:
            meta_ads_fit = job["fit"]

        work_type_text = job["work_type"].lower()

        if "remote" in work_type_text:
            notion_work_type = "Remote"
        elif "hybrid" in work_type_text:
            notion_work_type = "Hybrid"
        else:
            notion_work_type = "On-site"

        location_text = job["location"]

        if "Leeds" in location_text:
            notion_location = "Leeds"
        elif "Manchester" in location_text:
            notion_location = "Manchester"
        elif "London" in location_text:
            notion_location = "London"
        elif "Remote" in location_text:
            notion_location = "Remote UK"
        elif "Hybrid" in location_text:
            notion_location = "Hybrid UK"
        else:
            notion_location = "Other"

        notes = (
            f"Why it fits: {job['why_it_fits']}\n\n"
            f"Main gap: {job['main_gap']}\n\n"
            f"UK eligibility: {job['uk_eligibility']}\n\n"
            f"Sponsorship: {job['sponsorship']}"
        )

        add_job_to_notion({
            "role_company": f"{job['company']} — {job['job_title']}",
            "job_title": job["job_title"],
            "company": job["company"],
            "job_url": job_url,
            "posting_date": job["posting_date"],
            "date_found": date_found,
            "location": notion_location,
            "work_type": notion_work_type,
            "salary": job["salary"],
            "meta_ads_fit": meta_ads_fit,
            "priority": job["priority"],
            "notes": notes
        })

        print(f"ADDED — {job['job_title']} — {job['company']}")
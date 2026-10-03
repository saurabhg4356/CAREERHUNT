"""
Management command to seed realistic, clearly labeled DEMO DATA for CareerHunt.
Per requirements, all demo records are explicitly marked [DEMO DATA].
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.companies.models import Company
from apps.sources.models import JobSource
from apps.jobs.models import Category, Skill, Job, JobSkill


class Command(BaseCommand):
    help = "Seeds database with categorized DEMO DATA opportunities, skills, and sources."

    def handle(self, *args, **options):
        self.stdout.write("Seeding verified sources (DEMO DATA)...")

        sources_data = [
            ("Google Careers Official [DEMO DATA]", "official_company", "https://careers.google.com"),
            ("Microsoft Careers Portal [DEMO DATA]", "official_company", "https://careers.microsoft.com"),
            ("Amazon Student Programs [DEMO DATA]", "official_company", "https://amazon.jobs/en/teams/student-programs"),
            ("ISRO Recruitment Portal [DEMO DATA]", "government", "https://www.isro.gov.in/Careers.html"),
            ("Tech Opportunity Feed [DEMO DATA]", "rss_feed", "https://feed.example.com/jobs.xml"),
        ]

        sources = {}
        for name, stype, url in sources_data:
            src, _ = JobSource.objects.get_or_create(
                name=name,
                defaults={
                    "source_type": stype,
                    "source_url": url,
                    "status": "active",
                    "is_verified": True,
                    "last_checked_at": timezone.now(),
                }
            )
            sources[name] = src

        self.stdout.write("Seeding companies (DEMO DATA)...")
        companies_data = [
            ("Google", "https://google.com", "Technology & Search", "Mountain View, CA / Bangalore, India", True),
            ("Microsoft", "https://microsoft.com", "Cloud & Operating Systems", "Redmond, WA / Hyderabad, India", True),
            ("Amazon", "https://amazon.com", "E-Commerce & Cloud Computing", "Seattle, WA / Bangalore, India", True),
            ("ISRO", "https://isro.gov.in", "Aerospace & Government Research", "Bengaluru, Karnataka", True),
            ("Razorpay", "https://razorpay.com", "Fintech & Payments", "Bangalore, India", True),
            ("Infosys", "https://infosys.com", "IT Consulting & Services", "Bengaluru, India", True),
        ]

        companies = {}
        for name, web, ind, hq, ver in companies_data:
            comp, _ = Company.objects.get_or_create(
                name=name,
                defaults={
                    "website": web,
                    "industry": ind,
                    "headquarters": hq,
                    "is_verified": ver,
                    "description": f"{name} is a leading enterprise in {ind}.",
                }
            )
            companies[name] = comp

        self.stdout.write("Seeding categories and skills...")
        categories_data = {
            "Software Engineering": ["Python", "Django", "JavaScript", "React", "Java", "C++", "Go"],
            "Data Science & AI": ["Python", "Machine Learning", "PyTorch", "SQL", "Pandas", "Computer Vision"],
            "Cloud & DevOps": ["AWS", "Docker", "Kubernetes", "Linux", "CI/CD", "Terraform"],
            "Mobile Development": ["Flutter", "Kotlin", "Swift", "React Native"],
        }

        all_skills = {}
        for cat_name, skill_list in categories_data.items():
            cat, _ = Category.objects.get_or_create(name=cat_name)
            for sk_name in skill_list:
                sk, _ = Skill.objects.get_or_create(name=sk_name, defaults={"category": cat})
                all_skills[sk_name] = sk

        self.stdout.write("Seeding opportunities (DEMO DATA)...")
        now = timezone.now()

        demo_jobs = [
            {
                "title": "Software Development Engineering Intern [DEMO DATA]",
                "company": companies["Google"],
                "source": sources["Google Careers Official [DEMO DATA]"],
                "category": Category.objects.get(name="Software Engineering"),
                "opp_type": "internship",
                "exp": "fresher",
                "remote": "hybrid",
                "location": "Bangalore, India",
                "salary_min": 60000,
                "salary_max": 80000,
                "is_sal": True,
                "desc": "Join our Engineering team to build scalable services. Ideal for pre-final and final year undergraduate students.",
                "req": "Proficiency in Python or Java. Solid foundation in Data Structures and Algorithms.",
                "deadline": now + timedelta(days=12),
                "open_date": now - timedelta(days=5),
                "skills": ["Python", "Django", "SQL"],
            },
            {
                "title": "Cloud Support Associate [DEMO DATA]",
                "company": companies["Amazon"],
                "source": sources["Amazon Student Programs [DEMO DATA]"],
                "category": Category.objects.get(name="Cloud & DevOps"),
                "opp_type": "full-time",
                "exp": "0-1",
                "remote": "on-site",
                "location": "Hyderabad, India",
                "salary_min": 750000,
                "salary_max": 1100000,
                "is_sal": True,
                "desc": "Assist AWS customers with troubleshooting cloud architecture and deployment pipelines.",
                "req": "Basic understanding of networking, Linux operating systems, and AWS core services.",
                "deadline": now + timedelta(days=2),  # Closing soon!
                "open_date": now - timedelta(days=14),
                "skills": ["AWS", "Linux", "Docker"],
            },
            {
                "title": "Junior AI Research Trainee [DEMO DATA]",
                "company": companies["Microsoft"],
                "source": sources["Microsoft Careers Portal [DEMO DATA]"],
                "category": Category.objects.get(name="Data Science & AI"),
                "opp_type": "graduate-program",
                "exp": "fresher",
                "remote": "remote",
                "location": "Remote, India",
                "salary_min": 900000,
                "salary_max": 1300000,
                "is_sal": True,
                "desc": "Research program focusing on generative AI and natural language processing applications.",
                "req": "Strong background in mathematics and machine learning libraries.",
                "deadline": now + timedelta(days=25),
                "open_date": now - timedelta(days=2),
                "skills": ["Python", "Machine Learning", "PyTorch"],
            },
            {
                "title": "Scientist / Engineer Graduate Trainee [DEMO DATA]",
                "company": companies["ISRO"],
                "source": sources["ISRO Recruitment Portal [DEMO DATA]"],
                "category": Category.objects.get(name="Software Engineering"),
                "opp_type": "trainee",
                "exp": "fresher",
                "remote": "on-site",
                "location": "Bengaluru, Karnataka",
                "salary_min": 650000,
                "salary_max": 850000,
                "is_sal": True,
                "desc": "Government aerospace software trainee program for fresh engineering graduates.",
                "req": "First class B.E. / B.Tech in Computer Science or Electronics.",
                "deadline": now + timedelta(days=18),
                "open_date": now - timedelta(days=4),
                "skills": ["C++", "Linux", "Python"],
            },
            {
                "title": "Frontend React Internship [DEMO DATA]",
                "company": companies["Razorpay"],
                "source": sources["Tech Opportunity Feed [DEMO DATA]"],
                "category": Category.objects.get(name="Software Engineering"),
                "opp_type": "internship",
                "exp": "fresher",
                "remote": "hybrid",
                "location": "Bangalore, India",
                "salary_min": 35000,
                "salary_max": 45000,
                "is_sal": True,
                "desc": "Build next-generation payment checkout UI components using React and TypeScript.",
                "req": "Demonstrated React projects, CSS3 mastery, and modern JavaScript fundamentals.",
                "deadline": now + timedelta(days=1),  # Closing very soon!
                "open_date": now - timedelta(days=7),
                "skills": ["React", "JavaScript"],
            },
            {
                "title": "Future Graduate Program 2027 [DEMO DATA]",
                "company": companies["Google"],
                "source": sources["Google Careers Official [DEMO DATA]"],
                "category": Category.objects.get(name="Software Engineering"),
                "opp_type": "graduate-program",
                "exp": "fresher",
                "remote": "hybrid",
                "location": "Pune, India",
                "salary_min": 1400000,
                "salary_max": 1800000,
                "is_sal": True,
                "desc": "Upcoming campus hiring program for 2027 graduating batch. Applications open next week.",
                "req": "Enrolled in undergraduate degree graduating in 2027.",
                "deadline": now + timedelta(days=35),
                "open_date": now + timedelta(days=7),  # Upcoming!
                "skills": ["Java", "Python", "SQL"],
            },
            {
                "title": "Systems Engineering Associate [DEMO DATA]",
                "company": companies["Infosys"],
                "source": sources["Tech Opportunity Feed [DEMO DATA]"],
                "category": Category.objects.get(name="Software Engineering"),
                "opp_type": "full-time",
                "exp": "fresher",
                "remote": "on-site",
                "location": "Pune, India",
                "salary_min": 400000,
                "salary_max": 500000,
                "is_sal": True,
                "desc": "Entry-level software engineering role across enterprise client application modernization.",
                "req": "Basic coding proficiency in Python, Java, or C#.",
                "deadline": now + timedelta(days=20),
                "open_date": now - timedelta(days=10),
                "skills": ["Java", "SQL"],
            },
        ]

        count = 0
        for item in demo_jobs:
            job, created = Job.objects.get_or_create(
                title=item["title"],
                company=item["company"],
                defaults={
                    "source": item["source"],
                    "category": item["category"],
                    "opportunity_type": item["opp_type"],
                    "experience_level": item["exp"],
                    "remote_type": item["remote"],
                    "location_name": item["location"],
                    "salary_min": item["salary_min"],
                    "salary_max": item["salary_max"],
                    "is_salary_disclosed": item["is_sal"],
                    "description": item["desc"],
                    "requirements": item["req"],
                    "source_url": f"{item['source'].source_url}/job/{count+1}",
                    "application_url": f"{item['company'].website}/apply/{count+1}",
                    "application_open_date": item["open_date"],
                    "application_deadline": item["deadline"],
                    "verification_status": "verified",
                }
            )
            if created:
                count += 1
                for s_name in item["skills"]:
                    sk = all_skills.get(s_name)
                    if sk:
                        JobSkill.objects.get_or_create(job=job, skill=sk, defaults={"is_mandatory": True})

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {count} demo opportunities [DEMO DATA]."))

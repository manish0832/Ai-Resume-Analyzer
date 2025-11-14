import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------
# ✅ TECHNICAL SKILLS DICTIONARY
# ---------------------------------------------

TECHNICAL_SKILLS = {
    'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin'],
    'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring'],
    'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sqlite'],
    'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd'],
    'data': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'tableau', 'power bi', 'excel'],
    'tools': ['git', 'jira', 'confluence', 'slack', 'trello', 'figma', 'photoshop', 'illustrator']
}

# ---------------------------------------------
# ✅ MAIN ATS SCORE FUNCTION
# ---------------------------------------------

def calculate_ats_score(resume_text, job_description):
    resume_lower = resume_text.lower()
    job_lower = job_description.lower()

    scores = {}

    scores['keyword_match'] = calculate_keyword_match(resume_lower, job_lower) * 0.4
    scores['skills_match'] = calculate_skills_match(resume_lower, job_lower) * 0.3
    scores['text_similarity'] = calculate_text_similarity(resume_text, job_description) * 0.2
    scores['format_score'] = calculate_format_score(resume_text) * 0.1

    total_score = sum(scores.values())
    return min(100, max(0, int(total_score)))


# ---------------------------------------------
# ✅ KEYWORD MATCHING
# ---------------------------------------------

def calculate_keyword_match(resume_text, job_description):
    job_keywords = extract_keywords(job_description)
    resume_keywords = extract_keywords(resume_text)

    if not job_keywords:
        return 0

    matched_keywords = set(job_keywords) & set(resume_keywords)
    return min(100, (len(matched_keywords) / len(job_keywords)) * 100)


# ---------------------------------------------
# ✅ SKILL MATCHING
# ---------------------------------------------

def calculate_skills_match(resume_text, job_description):
    job_skills = extract_technical_skills(job_description)
    resume_skills = extract_technical_skills(resume_text)

    if not job_skills:
        return 50  # default

    matched_skills = set(job_skills) & set(resume_skills)
    return min(100, (len(matched_skills) / len(job_skills)) * 100)


# ---------------------------------------------
# ✅ TEXT SIMILARITY (TF-IDF + COSINE)
# ---------------------------------------------

def calculate_text_similarity(resume_text, job_description):
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        tfidf = vectorizer.fit_transform([resume_text, job_description])
        similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return similarity * 100
    except:
        return 0


# ---------------------------------------------
# ✅ FORMAT SCORE
# ---------------------------------------------

def calculate_format_score(resume_text):
    score = 0
    lower = resume_text.lower()

    sections = ['experience', 'education', 'skills', 'summary', 'objective']
    for section in sections:
        if section in lower:
            score += 10

    # Email present?
    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', resume_text):
        score += 10

    # ✅ Phone number (supports Indian + international)
    if re.search(r'(\+?\d{1,3}[- ]?)?\d{10}', resume_text):
        score += 10

    # Resume length
    words = len(resume_text.split())
    if 200 <= words <= 1000:
        score += 20

    return min(100, score)


# ---------------------------------------------
# ✅ KEYWORD EXTRACTION
# ---------------------------------------------

def extract_keywords(text):
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

    stop_words = {
        'the','and','for','are','but','not','you','all','can','had','her','was','one','our','out',
        'day','get','has','him','his','how','man','new','now','old','see','two','way','who','boy',
        'did','its','let','put','say','she','too','use'
    }

    keywords = [w for w in words if w not in stop_words]

    counter = Counter(keywords)
    return [word for word, _ in counter.most_common(50)]


# ---------------------------------------------
# ✅ TECHNICAL SKILL EXTRACTION
# ---------------------------------------------

def extract_technical_skills(text):
    skills = []
    lower = text.lower()

    for category, skill_list in TECHNICAL_SKILLS.items():
        for skill in skill_list:
            if skill in lower:
                skills.append(skill)

    return list(set(skills))


# ---------------------------------------------
# ✅ SKILL MATCH ANALYSIS (detailed)
# ---------------------------------------------

def analyze_skills_match(resume_text, job_description):
    job_skills = extract_technical_skills(job_description)
    resume_skills = extract_technical_skills(resume_text)

    matched = list(set(job_skills) & set(resume_skills))
    missing = list(set(job_skills) - set(resume_skills))

    percent = 0
    if job_skills:
        percent = (len(matched) / len(job_skills)) * 100

    return {
        'matched_skills': matched,
        'missing_skills': missing,
        'match_percentage': round(percent, 1),
        'total_job_skills': len(job_skills),
        'total_resume_skills': len(resume_skills)
    }

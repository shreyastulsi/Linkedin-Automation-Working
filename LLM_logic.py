


import re
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from dotenv import find_dotenv, load_dotenv
import openai
from openai import OpenAI
import requests

load_dotenv(find_dotenv())

embeddings = OpenAIEmbeddings()
chat_model = ChatOpenAI(model_name="gpt-3.5-turbo")

def create_db_from_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    full_text = "\n".join(page.page_content for page in pages)

    sections = section_based_split(full_text)
    docs = []

    for section in sections:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=50
        )
        section_chunks = text_splitter.split_text(section["content"])
        docs.extend(section_chunks)

    db = FAISS.from_texts(docs, embeddings)
    return db, sections

def section_based_split(text):
    section_pattern = re.compile(
        r"(?P<header>EDUCATION|EXPERIENCE|PROJECTS|COMPETITIONS|SKILLS|CERTIFICATIONS)(?:\n|\s|:)*",
        re.IGNORECASE,
    )
    matches = list(section_pattern.finditer(text))
    sections = []

    for i in range(len(matches)):
        start = matches[i].end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_content = text[start:end].strip()
        section_name = matches[i].group('header').strip()
        sections.append({"section": section_name, "content": section_content})

    return sections

def extract_keywords(example_experience):
    keywords = re.findall(r'\b\w+\b', example_experience.lower())
    unique_keywords = list(set(keywords))
    return unique_keywords

def extract_experience_examples(pdf_path):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    example_experience = "\n\n".join(page.page_content.strip() for page in pages)
    return example_experience

def generate_optimized_section(section_name, content, example_experience):
    section_name = section_name.upper()

    if section_name == "EXPERIENCE" and example_experience:
        print("Using specialized experience transformation")
        keywords = extract_keywords(example_experience)
        prompt_system = f"""
        You are a specialized LinkedIn writer helping Computer Science students optimize their EXPERIENCE sections.
        Use a narrative tone, focusing on action verbs like: 'collaborated', 'engineered', 'deployed', 'impact-driven', 'cross-functional'.
        Incorporate technologies, methodologies, and soft skills mentioned in the following examples: {example_experience}.
        Explain the modifications you've made from the original resume content to make it more suitable for LinkedIn.
        """
        prompt_human = (
            f"Transform the following resume content into an optimized LinkedIn EXPERIENCE section: {content}. "
            "Use storytelling elements like the STAR framework: situation, task, action, and result. Be very structured, each expeirence should be seperated."
        )
    elif section_name == "EDUCATION":
        prompt_system = """
        You are a professional writer specialized in crafting EDUCATION sections for LinkedIn.
        Focus on highlighting academic achievements, relevant coursework, projects, and any honors or scholarships.
        Emphasize key subjects and how they relate to the student's career goals in Computer Science.
        """
        prompt_human = (
            f"Develop a LinkedIn EDUCATION section using the following resume content: {content}. "
            "Highlight relevant coursework, achievements, and how it aligns with career aspirations."
        )
    elif section_name == "PROJECTS":
        prompt_system = """
        You are a LinkedIn writer helping students optimize their PROJECTS sections.
        Focus on describing the scope of the project, the technologies used, the challenges faced, and the impact or outcome.
        Use action verbs like: 'developed', 'designed', 'implemented', 'optimized', and 'delivered'.
        """
        prompt_human = (
            f"Transform the following resume content into a LinkedIn PROJECTS section: {content}. "
            "Focus on technology, challenges, and outcomes to make it engaging for potential recruiters."
        )
    elif section_name == "COMPETITIONS":
        prompt_system = """
        You are a LinkedIn expert specialized in optimizing COMPETITIONS sections.
        Emphasize the scope of the competition, the skills demonstrated, teamwork or leadership roles, and the final results or achievements.
        Highlight relevant technologies, problem-solving abilities, or strategic thinking used in the competition.
        """
        prompt_human = (
            f"Convert the following resume content into a compelling LinkedIn COMPETITIONS section: {content}. "
            "Highlight achievements, skills demonstrated, and leadership experience to make it stand out."
        )
    elif section_name == "SKILLS":
        prompt_system = """
        You are a professional LinkedIn writer focusing on SKILLS sections.
        Highlight technical and soft skills, emphasizing proficiency levels and any certifications or tools mastered.
        Use categories such as 'Programming Languages', 'Frameworks & Tools', and 'Soft Skills'.
        """
        prompt_human = (
            f"Optimize the following resume content for a LinkedIn SKILLS section: {content}. "
            "Group skills logically, and mention certifications or tools wherever applicable."
        )
    else:
        prompt_system = (
            "You are a helpful assistant specializing in writing professional LinkedIn sections "
            "for Computer Science students."
        )
        prompt_human = (
            f"Develop a LinkedIn {section_name} section using the following resume content: {content}."
        )

    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.8,
        messages=[
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_human}
        ]
    )

    message_content = response.choices[0].message.content
    return message_content

def optimize_all_sections(sections, example_experience):
    linkedin_sections = {}
    for section in sections:
        optimized_text = generate_optimized_section(section["section"], section["content"], example_experience)
        linkedin_sections[section["section"]] = optimized_text
    return linkedin_sections

def google_nlp_optimization(text):
    url = "https://language.googleapis.com/v1/documents:analyzeEntities?key=AIzaSyCJ2ro5TvvHgZD6YhKcF6Qztbk3C3Ui0JU"
    headers = {"Content-Type": "application/json"}
    data = {
        "document": {"type": "PLAIN_TEXT", "content": text},
        "encodingType": "UTF8"
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        entities = response.json().get("entities", [])
        keywords = [entity["name"] for entity in entities]
        return " ".join(keywords)
    return ""

def integrate_seo_optimization(sections):
    for section, content in sections.items():
        optimized_keywords = google_nlp_optimization(content)
        sections[section] = f"{content}\n\nOptimized Keywords: {optimized_keywords}"
    return sections

# if __name__ == "__main__":
#     pdf_path = "/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/Linkedin-Automation/Testing-Resume.pdf"
#     experiences_path = "/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/Linkedin-Automation/Experience-Examples-PDF.pdf"

#     db, sections = create_db_from_pdf(pdf_path)
#     example_experience = extract_experience_examples(experiences_path)

#     optimized_linkedin_content = optimize_all_sections(sections, example_experience)

#     # optimized_linkedin_content = integrate_seo_optimization(optimized_linkedin_content)

#     for section, content in optimized_linkedin_content.items():
#         print(f"--- {section} ---\n{content}\n")

import os
import openai
from dotenv import load_dotenv, find_dotenv
import sys

load_dotenv(find_dotenv(), override=True)  # Load env before run powerpaint

# Access the value of PYTHONPATH
# python_path = os.getenv("PYTHONPATH")

# openai.api_key = os.environ["OPENAI_API_KEY"]
# depens
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.memory import ConversationBufferWindowMemory
import os
from langchain.document_loaders import PyPDFLoader


# Schema
def cv_parser(filepath) -> dict:
    designation_schema = ResponseSchema(
        name="designation",
        description="Extract all positions or job titles of the person writting this CV. Output them as a Python list, if can't find any output empty list.",
    )
    name_schema = ResponseSchema(
        name="name",
        description="What is the name of the person writing this CV. If this information is not found, output None.",
    )
    email_schema = ResponseSchema(
        name="email",
        description="Extract any email address, and output them as a Python string.",
    )
    mobile_number_schema = ResponseSchema(
        name="mobile_number",
        description="What is the mobile number of the person writing this CV. Output them as a string. If you can't find it, output None.",
    )
    skills_schema = ResponseSchema(
        name="skills",
        description="Extract all name of skills the writer possessed. Then output them as a Python list. If you can't find skill's name, output empty list.",
    )
    college_name_schema = ResponseSchema(
        name="college_name",
        description="What is the name of the college attended by the person writing this CV. If this information is not found, output None.",
    )
    degree_schema = ResponseSchema(
        name="degree",
        description="Extract any academic degree of the person writing this CV. Output them as a comma separated Python list.",
    )
    company_names_schema = ResponseSchema(
        name="company_names",
        description="What is the name of the company attended by the person writing this CV. If this information is not found, output None.",
    )

    response_schemas = [
        name_schema,
        email_schema,
        mobile_number_schema,
        skills_schema,
        college_name_schema,
        degree_schema,
        designation_schema,
        company_names_schema,
        # no_of_pages_schema,
        # total_experience_schema,
    ]

    # Parser
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    # Message template
    input_template = """\
    You're a helpful assistant that can scan the CV and extract useful informations 
    for Human. For the following CV that was given below, extract the following 
    information:

    designation: Extract all positions or job titles of the person writting this CV. Output them as a Python list, if can't find any output empty list.

    name: What is the name of the person writing this CV. If this information is not found, output None.

    email: Extract any email address, and output them as a Python string.

    mobile_number: What is the mobile number of the person writing this CV. Output them as a string. If you can't find it, output None.

    skills: Extract all name of skills the writer possessed. Then output them as a Python list. If you can't find skill's name, output empty list.
    
    college_name: What is the name of the college attended by the person writing this CV. If this information is not found, output None.

    degree: Extract any academic degree of the person writing this CV. Output them as a comma separated Python list.
                                    
    company_names: What is the name of the company attended by the person writing this CV. If this information is not found, output None.
                                        
    CV: {text}

    {format_instructions}
    """

    # Init memory
    memory = ConversationBufferWindowMemory(k=7)

    # Init chatbot
    llm = ChatOpenAI(temperature=0.0)

    # Load the CV file
    with open(filepath, "r", encoding="utf-8") as cv_file:
        cv_text = cv_file.read()

    # Init prompt
    prompt = ChatPromptTemplate.from_template(template=input_template)
    messages = prompt.format_messages(
        text=cv_text, format_instructions=format_instructions
    )
    response = llm(messages)

    # Parse the output and return as JSON
    output_dict = output_parser.parse(response.content)
    # output_dict["no_of_pages"] = no_of_pages

    return output_dict


def cv1(filepath) -> dict:
    return {
        "name": "Tristan Nguyen",
        "email": "kivanolai@gmail.com",
        "mobile_number": "+84 918378804",
        "date_of_birth": "1993-01-01",
        "skills": [
            "NodeJS",
            "Python",
            "Backend: Python Flask, Django framework, NodeJS NestJS",
            "Frontend: React, Angular, native JS",
            "Database: MongoDB , Neo4J, Postgres",
            "Smart Contracts: EVM, Solidity, Rust, DAML",
            "Web3 blockchain ecosystem: Solana, Hyperledger Fabric, Near, Avax, Ethereum, Tezos",
        ],
        "college_name": "University of Bordeaux",
        "degree": "Master Computer Science, Degree Information Technologies",
        "designation": [
            "Remote Senior/Lead Frontend Engineer",
            "(ReactJS/VueJS)",
            "Technical consultant / Backend Engineer",
            "Full Stack Developer",
            "Full Stack Software Developer",
            "Data engineer",
        ],
        "company_names": [
            "Axpara Consulting",
            "Notico Logistics",
            "Vertex Growth",
            "System",
            "Smartec IoT",
        ],
        "no_of_pages": 4,
    }

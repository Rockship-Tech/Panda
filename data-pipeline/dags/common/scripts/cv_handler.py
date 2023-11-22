# Depens
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts.prompt import PromptTemplate
from operator import itemgetter

# Set API keys
import os
import openai
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)  # read local .env file

openai.api_key = os.environ["OPENAI_API_KEY"]

MAX_TOKENS = int(3600)


def cv_handle(file):
    #####################################
    # Input: directory of 1 CV file     #
    # Output: the JSON extracted schema #
    #####################################

    # Environment check for OPENAI key | <------ Need to integrate logging here
    if os.getenv("OPENAI_API_KEY") is None or os.getenv("OPENAI_API_KEY") == "":
        raise Exception("OPENAI_API_KEY is not set")

    # Schema
    name_schema = ResponseSchema(
        name="name",
        description="What is the name of this person. Output as Python string.",
        type="string"
    )
    designation_schema = ResponseSchema(
        name="designation",
        description="What is the latest job title of this person. Output as Python string.",
        type="string"
    )
    email_schema = ResponseSchema(
        name="email",
        description="Extract any email address. Output as Python list of string.",
        type="List[string]"
    )
    mobile_number_schema = ResponseSchema(
        name="mobile_number",
        description="What is the mobile number of this person. Output them as list of string.",
        type="List[string]"
    )
    skills_schema = ResponseSchema(
        name="skills",
        description="Extract all name of skills this person possessed. Output them as list of string.",
        type="List[string]"
    )
    college_name_schema = ResponseSchema(
        name="college_name",
        description="What is the name of the college attended by this person. Output them as list of string.",
        type="List[string]"
    )
    degree_schema = ResponseSchema(
        name="degree",
        description="Extract any academic degree of this person. Output them as list of string.",
        type="List[string]"
    )
    company_names_schema = ResponseSchema(
        name="company_names",
        description="What is the name of the company attended by this person. Output them as list of string.",
        type="List[string]"
    )
    experience_schema = ResponseSchema(
        name="experience",
        description="Extract all the jobs experience of this person. Each job experience is a JSON dictionary \
of company name, project name, position name and the duration then concanate them into a list, if you can't find \
any field just let them be empty string.",
        type="List[dict]"
    )
    certificate_schema = ResponseSchema(
        name="certificate",
        description="Extract any certificate (not a degree) of this person. Output them as list of string.",
        type="List[string]"
    )

    response_schemas = [name_schema,
                        email_schema,
                        mobile_number_schema,
                        skills_schema,
                        college_name_schema,
                        degree_schema,
                        certificate_schema,
                        designation_schema,
                        company_names_schema,
                        experience_schema,
                        # no_of_pages_schema,
                        ]

    # Parser
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    # CV extraction template
    cv_extract_chain = (
            PromptTemplate.from_template(
                template="""You're a helpful assistant that can scan the CV and extract useful informations \
for Human. For the below verbatim of a CV, extract the following information:

<information>
designation, name, email, mobile_number, skills, college_name, degree, company_names, experience, certificate
</information>
                                                               
<CV>
{text}
</CV>

<Output format>
{format}
</Output format>"""
            )
            | ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
            | output_parser
    )

    # Handle file extension, only pdf in this version
    if not str(file).lower().endswith('.pdf'):
        raise TypeError(f"File is not .PDF: {file}")

    loader = PyPDFLoader(file)
    pages = loader.load()

    # Recombine then split to chunks    
    text = "\n\n".join([p.page_content for p in pages])
    no_of_pages = len(pages)
    texts = CharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    ).split_text(text)

    complete_dict_chain = {"text": itemgetter("text"),
                           "format": itemgetter("format")
                           } | cv_extract_chain

    try:
        responses = complete_dict_chain.batch([{"text": text, "format": format_instructions} for text in texts])
    except:
        raise Exception(f"An unexpected situation occurred while running batch to a chain. Check {file}")

    # CV combine template
    cv_combine_chain = {"text": lambda X: "\n\n".join([str(x) for x in X['text']]), "format": itemgetter("format")} | (
            PromptTemplate.from_template(
                template="""You're a helpful assistant that can combine Python dictionaries \
dict by dict extracted from parts of ONE same CV and craft the final Python dictionary that \
represent that ONE CV using below information.
                                                               
<parts of CV>
{text}
</parts of CV>

<Output format>
{format}
</Output format>"""
            )
            | ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
            | output_parser
    )

    try:
        response = cv_combine_chain.invoke({"text": responses, "format": format_instructions})
    except:
        raise TypeError("Expecting value in correct list[dict] format in:" + str(responses))

    response["no_of_pages"] = no_of_pages

    return response

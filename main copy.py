import os
from langchain_community.document_loaders import TextLoader
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import MarkdownTextSplitter
from langchain.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.vectorstores import Chroma
from colorama import Fore
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

# https://python.langchain.com/docs/modules/data_connection/vectorstores/

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGUAGE_MODEL = "gpt-3.5-turbo-instruct"

template: str = """/
    You are a senior developer who can answer {question} in natural language about markdown files  and {context} /
    respond in bullet points. /
    """
system_message_prompt = SystemMessagePromptTemplate.from_template(template)
human_message_prompt = HumanMessagePromptTemplate.from_template(
    input_variables=["question", "context"],
    template="{question}",
)
chat_prompt_template = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)

model = ChatOpenAI()

chunk_size = 60

# md loader
markdown_path = "./README.md"
data = TextLoader(markdown_path).load()
markdown_text = ",".join([doc.page_content for doc in data])

def load_documents():
    md_splitter = MarkdownTextSplitter(chunk_size=chunk_size, chunk_overlap=0)
    return md_splitter.create_documents([markdown_text])


documents = load_documents()
db = Chroma.from_documents(documents, OpenAIEmbeddings())
retriever = db.as_retriever()

def print_chunks():
    _ = [print(f"{index + 1}/{len(documents)} - {document.page_content}\n") for index, document in enumerate(documents)]

    print(f"{Fore.GREEN}- Chunk Size: {chunk_size}")
    print(f"- Number of chunks: {len(documents)}")

 
def main(query):
    print_chunks()
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | chat_prompt_template
        | model
        | StrOutputParser()
    )
    response = chain.invoke(query)
    print(f"{Fore.CYAN}{response}")
   

if __name__ == "__main__":  
    query = "explain how to create a virtual environment for mac users"
    main(query)

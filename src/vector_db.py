import re
import json
import argparse
from pathlib import Path
import os

import chromadb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHROMA_DIR = PROJECT_ROOT / "backend" / "output" / "chroma_db"
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
chroma_db = chroma_client.get_or_create_collection(name="textbook_slides_3")

from openai import OpenAI
API_KEY = os.getenv('API_KEY')
openai_client = OpenAI(api_key=API_KEY)

def llm_response(text, context):
    
    system_message = f"""
    You are a professor of mathematics, trained to answer questions from students based on your knwoledge and notes.
    """

    prompt = rf"""
    You are given the following query from a student:
    {text}
    
    You have gathered following reference notes to answer the question:
    {context}
    
    Based on your own knowledge of the main topic asked in the question and using some references from your notes, provide an answer to the student:
    Your answer must be in the detailed as if you are teaching in a one on one session with the student.
    """
    
    completion = openai_client.chat.completions.create(
            model="gpt-4o",
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}],
            temperature=0
        )

    output = completion.choices[0].message.content
    output_prompt_tokens = completion.usage.prompt_tokens
    output_completion_tokens = completion.usage.completion_tokens
    print(f"Output Prompt Tokens: {output_prompt_tokens}")
    print(f"Output Completion Tokens: {output_completion_tokens}")
    return output

def llm_response_null(text, context):
    
    system_message = f"""
    You are a professor of mathematics, trained to answer questions from students based on your knwoledge.
    """

    prompt = rf"""
    You are given the following query from a student:
    {text}
        
    Based on your own knowledge of the main topic asked in the question provide an answer to the student:
    Your answer must be in the detailed as if you are teaching in a one on one session with the student.
    """
    
    completion = openai_client.chat.completions.create(
            model="gpt-4o",
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}],
            temperature=0
        )

    output = completion.choices[0].message.content
    output_prompt_tokens = completion.usage.prompt_tokens
    output_completion_tokens = completion.usage.completion_tokens
    print(f"Output Prompt Tokens: {output_prompt_tokens}")
    print(f"Output Completion Tokens: {output_completion_tokens}")
    return output


def embed_func(text):

    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small")
    
    return response.data[0].embedding

def clean_text(text):
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    return cleaned_text
    
def embed_slides(slides_dict):
    documents = []
    embeddings = []
    metadatas = []
    for chapter_title, headings in slides_dict.items():
        for heading, slide in headings.items():
            for slide_title, slide_points in slide.items():
                slide_text = " ".join(slide_points)
            # clean_slide_text = clean_text(slide_text)
            
                documents.append(slide_text)
                metadatas.append({
                    'Chapter Title': chapter_title,
                    'Slide Title': slide_title,
                    'Heading Titile': heading
                })
            
                embeddings.append(embed_func(slide_text))
            
    chroma_db.add(
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
        ids=[str(i+1) for i in range(len(documents))]
    )
    print("Slides have been embedded and stored in ChromaDB.")

def retrieve_slides(query_text, top_k=10):
    query_embedding = embed_func(query_text)
    
    results = chroma_db.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
    
    print()

    retrieved_slides = []
    context = ""
    for i, document in enumerate(results["documents"][0]):
        slide_info = {
            "Chapter Title": results["metadatas"][0][i]["Chapter Title"],
            "Heading Titile": results["metadatas"][0][i]["Heading Titile"],
            "Slide Title": results["metadatas"][0][i]["Slide Title"],
            "Content": document
        }
        retrieved_slides.append(slide_info)
        
        print(f"Chapter Title: {slide_info['Chapter Title']}")
        print(f"Slide Title: {slide_info['Slide Title']}")
        print(f"Content: {slide_info['Content']}\n")
        
        context += f"Slide Title: {slide_info['Slide Title']}"
        context += f"Content: {slide_info['Content']}\n"

    return retrieved_slides, context


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--sp', 
                        type=str, 
                        default=str(PROJECT_ROOT / 'sample_toc.json'),
                        help='Path of Slide JSON')
    parser.add_argument('--embed', action='store_true', help='Option to create vector db')
    parser.add_argument('--query', type=str, help='Query text')

    args = parser.parse_args()
        
    if args.embed:
        with open(args.sp, 'r') as f:
            slides_dict = json.load(f)
        embed_slides(slides_dict)
    
    if args.query:
        retrieved_slides, context = retrieve_slides(args.query, top_k=10)
        response = llm_response(text=args.query, context=context)
        print(response)

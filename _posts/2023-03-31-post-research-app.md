---
title: "Building an Interactive PDF Q&A System with GPT-3.5-turbo, FAISS, and Streamlit"
categories:
  - blog
tags:
  - nlp
  - large language models
  - app development
  - openai
---

Hello, everyone! In today's post, I am excited to share with you one of the apps that I've been working on. The purpose of this app is to allow users to submit PDFs and interactively ask questions about the content within them. The program analyzes the text in the PDFs and provides answers to the users' questions based on the information available in the documents.

> [Research Paper Guru](https://huggingface.co/spaces/mikeion/research_guru)

To achieve this functionality, the program leverages several powerful technologies, including pyPDF2 for extracting text from PDFs, OpenAI embeddings for generating embeddings of sentences and sections, FAISS for comparing embeddings and matching questions to relevant text, GPT-3.5-turbo from OpenAI for processing user input and generating responses, Streamlit for building the front end, and [Hugging Face](https://huggingface.co/spaces) Spaces for hosting the application. The program is written in Python and makes use of additional libraries such as NumPy and Pandas.

In this blog post, I will take you through the key components and functionalities of the program, as well as provide a step-by-step walkthrough of how to use it. Let's get started!

## Extracting Text from PDFs

The first step in building our interactive Q&A system is to extract the text from the PDF documents that users submit. To accomplish this task, we use the pyPDF2 library, which is a widely-used tool for working with PDF files in Python.

With pyPDF2, we can open a PDF file and read its contents page by page. The library allows us to extract the text from each page and concatenate it to form a complete representation of the document's content. Here is a code snippet that demonstrates how we use pyPDF2 to extract text from a PDF file:

```python
# Import the PyPDF2 library
import PyPDF2

"""
Extract text from a PDF file

:param pdf_path: The path to the PDF file
:return: The text extracted from the PDF file

"""

def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as pdf_file:
        # Read the PDF file
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        # Get the number of pages in the PDF
        num_pages = pdf_reader.numPages
        # Initialize an empty string to store the text
        full_text = ''
        # Loop through each page and extract the text
        for page_num in range(num_pages):
            # Get the page object
            page = pdf_reader.getPage(page_num)
            # Extract the text from the page
            page_text = page.extractText()
            # Append the text to the full_text variable
            full_text += page_text
    # Return the full text of the PDF
    return full_text
```

In the code snippet above, we define a function `extract_text_from_pdf` that takes the file path of a PDF document as input and returns the extracted text. We use the `PdfFileReader` class from `pyPDF2` to read the PDF and iterate through its pages, extracting the text from each page and appending it to the full_text variable.

Now that we have the ability to extract text from PDFs, we can move on to the next step: generating and comparing embeddings.

## Generating and Comparing Embeddings

Once we have extracted the text from the PDFs, our next step is to represent this text in a way that allows us to compare and match questions to relevant sections of the document. For this purpose, we use embeddings.

Embeddings are numerical representations of text that capture semantic information in a lower-dimensional vector space. To generate embeddings for the sentences and sections of text within the PDFs, we use the ``openai.embeddings`` library.

Here is how we obtain embeddings for the text:

```python
# Import the OpenAI library
import openai
    
    """
    Generate embeddings for a list of text strings

    :param text_list: A list of text strings
    :return: A NumPy array of embeddings

    """

def get_embeddings(text_list):
    # Generate embeddings for the text strings, using the default parameters.
    # The default parameters are: model="ada", version="2020-05-03", and
    # return_metadata=False.
    # See the OpenAI documentation for more information: https://beta.openai.com/docs/api-reference/embeddings

    embeddings = openai.embeddings(text_list)
    return embeddings
```

In the code snippet above, we define a function get_embeddings that takes a list of text strings as input and returns their embeddings. We use the openai.embeddings function to generate embeddings for each text string in the input list.

## Creating a FAISS Index

FAISS (Facebook AI Similarity Search) is a library designed to perform efficient similarity search and clustering of high-dimensional vectors, such as embeddings. In our program, we use FAISS to create an index of the embeddings generated for the sections of text within the PDFs. By creating a FAISS index, we can efficiently search for the most similar embeddings to the user's question, allowing us to identify the most relevant sections of text.

To create a FAISS index, we need to perform the following steps:

1. Determine the Dimensionality: We need to determine the dimensionality of the embeddings we plan to index. The dimensionality is simply the number of components in each embedding vector.

2. Initialize the Index: We initialize the FAISS index using the dimensionality of the embeddings. In our program, we use an IndexFlatL2 index, which is a basic index type that performs L2 distance-based similarity search.

3. Add Embeddings to the Index: Once the index is initialized, we add the embeddings to the index. This process involves transferring the embeddings to the FAISS index structure so they can be searched efficiently.

Here is a code snippet to show how to implement this in practice:


```python

import faiss

    """
    Create a FAISS index for a set of embeddings

    :param embeddings: A NumPy array of embeddings
    :return: A FAISS index

    """

def create_faiss_index(embeddings):
    # Determine the dimensionality of the embeddings
    dimension = embeddings.shape[1]
    # Initialize the FAISS index
    index = faiss.IndexFlatL2(dimension)
    # Add the embeddings to the index, using .add(), as index is a object.
    index.add(embeddings)
    return index
```

By creating a FAISS index for the text embeddings, we enable our program to quickly find the most relevant sections of text in response to user questions.

## Searching for Similar Embeddings

After creating a FAISS index with the embeddings of the sections of text within the PDFs, our next step is to perform similarity search. The goal of similarity search is to find the embeddings in the index that are most similar to a given query embedding. In our program, the query embedding represents the user's question, and we aim to find the sections of text that are most relevant to that question.

To perform similarity search using a FAISS index, we need to follow these steps:

1. Prepare the Query Embedding: We need to ensure that the query embedding (the embedding of the user's question) is in the correct format. It should be a 2D array where the number of rows corresponds to the number of queries (in our case, usually 1), and the number of columns corresponds to the dimensionality of the embeddings.

2. Perform the Search: We use the search method of the FAISS index to search for the most similar embeddings to the query embedding. We can specify the number of nearest neighbors ($k$) we want to retrieve. The search method returns two arrays: distances and indices. The distances array contains the L2 distances between the query embedding and the nearest neighbors found in the index. The indices array contains the indices of the nearest neighbors in the original dataset.

```python

"""
Search for similar embeddings in a FAISS index

:param query_embedding: A NumPy array of embeddings
:param index: A FAISS index
:param k: The number of nearest neighbors to retrieve
:return: A tuple containing the distances and indices of the nearest neighbors

"""

def search_similar_embeddings(query_embedding, index, k=1):
    # Ensure that the query embedding is a 2D array
    distances, indices = index.search(query_embedding, k)
    # Return the distances and indices of the nearest neighbors
    return distances, indices
```

In this code snippet, we define a function ``search_similar_embeddings`` that takes a query embedding, a FAISS index, and an optional parameter $k$ as input. We ensure that the query embedding is a 2D array by reshaping it using ``query_embedding.reshape(1, -1)``. We then use the search method of the FAISS index to find the k nearest neighbors. The function returns the distances and indices of the nearest neighbors.

By searching for similar embeddings, our program is able to identify the sections of text within the PDFs that are most semantically similar to the user's question, and thus most likely to contain relevant information.

By leveraging embeddings and FAISS, our application is able to identify the sections of text within the PDFs that are most relevant to the user's question.

## Processing User Input and Generating Responses

After identifying the most relevant sections of text within the PDFs, our next step is to process the user's input and generate meaningful responses. To do this, we take advantage of GPT-3.5-turbo, a powerful language model developed by OpenAI.

The GPT-3.5-turbo model is capable of understanding natural language input and generating human-like text. We use the model to interpret the user's question and provide an answer based on the selected sections of text.

To generate responses using GPT-3.5-turbo, we perform the following steps:

1. Prepare the Prompt: We create a prompt for the language model that includes the user's question and the relevant text from the PDFs. The prompt should be designed in a way that guides the model to provide a relevant and informative response.

2. Call the OpenAI API: We use the OpenAI API to send the prompt to the GPT-3.5-turbo model. The API returns a response that includes the model-generated text.

3. Extract the Answer: We extract the answer from the model-generated text and present it to the user.

The following code snippet demonstrates how we interact with the GPT-3.5-turbo model to generate responses:

```python
import openai

"""
Generate a response using the GPT-3.5-turbo model

:param prompt: A string containing the prompt for the model
:param model: The name of the model to use
:return: A string containing the model-generated text

"""


def generate_response(prompt, model="gpt-3.5-turbo"):
    # Step 1: Prepare the prompt
    response = openai.Completion.create(engine=model, prompt=prompt, max_tokens=150)
    
    # Step 2: Extract the answer
    answer = response["choices"][0]["text"].strip()
    
    return answer

# Example usage
user_question = "What are some of the different ways students can think about the derivative?"
relevant_text = "There are many ways students can think about the derivative. For example, some problems ask students to use a graph of the derivative of a function to say something about the original function, which requires students to think about the derivative graphically. Another subset of problems might ask students to use take the limit of a difference quotient as the limit approaches 0 to find a derivative, which requires students to think about the derivative symbolically."
prompt = f"User: {user_question}\nDocument: {relevant_text}\nAnswer:"
answer = generate_response(prompt)
```
In this code snippet, we define a function ``generate_response`` that takes a prompt and an optional model name as input. We call the ``openai.Completion.create`` method to send the prompt to the ``GPT-3.5-turbo`` model, and we extract the answer from the response. In the example usage, we demonstrate how to create a prompt that includes the user's question and the relevant text from the PDFs.

By using ``GPT-3.5-turbo``, our program can interpret user input, understand the context provided by the text sections, and generate informative and relevant answers to the user's questions.

## Building and Hosting the Web Application

With the core functionality for processing PDFs and generating responses in place, the next step is to build a user-friendly web application that allows users to interact with the program. To achieve this, we use Streamlit, a powerful and intuitive Python library for building interactive web apps.

In addition, we host the application on Hugging Face Spaces, a platform that allows us to easily deploy and share machine learning models and applications.

### Building the Front End with Streamlit

[Streamlit](https://streamlit.io/) provides an easy-to-use framework for building interactive web applications. With Streamlit, we can create user interfaces that allow users to upload PDF files, enter questions, and view answers.

Here is a simplified example of how we use Streamlit to build the front end of the application:

```python
# Import the Streamlit library
# Streamlit is a Python library for building interactive web apps
import streamlit as st

"""

# Q&A App

This app allows users to upload PDF files and ask questions about the content.

"""


def q_and_a_app():
    # Create a file uploader for PDFs
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    
    # Allow users to enter a question
    question = st.text_input("Enter your question")
    
    # Create a button to submit the question
    submit_button = st.button("Submit")
    
    # When the user clicks the "Submit" button, process the PDF and generate a response
    if submit_button:
        if pdf_file and question:
            # Process the PDF and generate a response (function calls omitted for brevity)
            response = process_pdf_and_generate_response(pdf_file, question)
            # Display the response
            st.write(response)
        else:
            st.warning("Please upload a PDF file and enter a question.")

# Run the Streamlit app
if __name__ == "__main__":
    app()
```

In this example, we use Streamlit's ``file_uploader`` to create an interface for users to upload PDF files. We use ``text_input`` to allow users to enter a question, and button to create a "Submit" button. When the user clicks the "Submit" button, the application processes the PDF, generates a response to the user's question, and displays the response using the write method.
Hosting on Hugging Face Spaces

Hugging Face Spaces is a platform that allows developers to deploy and share machine learning models and applications with a wider audience. We host our Streamlit application on Hugging Face Spaces to make it accessible to users around the world.

To deploy the application on Hugging Face Spaces, we create a new Space, upload the application's source code, and configure the deployment settings. Hugging Face Spaces automatically handles the deployment process and provides us with a public URL where the application can be accessed.

By combining Streamlit and Hugging Face Spaces, we create an interactive and accessible web application that allows users to submit PDFs, ask questions about the text, and receive answers based on the content within the documents.

## Conclusion

In conclusion, the interactive Q&A program I've walked through here provides users with a powerful and convenient way to extract information from PDF documents. By leveraging technologies such as pyPDF2, OpenAI embeddings, FAISS, GPT-3.5-turbo, Streamlit, and Hugging Face Spaces, the application offers a user-friendly interface for submitting PDFs, asking questions, and receiving answers based on the content within the documents.

Whether it's extracting insights from research papers, finding specific information in lengthy documents, or simply exploring the content of a PDF, this application empowers users to access information in a dynamic and interactive way. 

Thank you for joining me on this journey to explore the inner workings of the program. Let me know if you have any questions by sending me a message on my LinkedIn profile posted on the homepage.

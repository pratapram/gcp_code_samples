# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



import PyPDF2
import io
from google.cloud import storage
import chainlit as cl
import vertexai
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
    GenerativeModel,
    Tool,
    ToolConfig,
    FunctionDeclaration,
)

#importing a file
import searchpythonapi

# Google Cloud project ID and model name
PROJECT_ID = ""
LOCATION = "us-central1"  
vertexai.init(project=PROJECT_ID, location=LOCATION)

model_name_gemini_15_flash = "gemini-1.5-flash-001"  # @param {type:"string"}
model_summarizer = GenerativeModel(
    model_name_gemini_15_flash,
    system_instruction=[
        "You are a  document helper bot.",
        "Write a concise summary of the following text delimited by triple backquotes.",
        ],
)
summarizer_gen_config = GenerationConfig(
    temperature=0.9,
    top_p=1.0,
    top_k=32,
    candidate_count=1,
    max_output_tokens=8192,
)

def search_datastore(query_str):
    print (f"in get_search_data tool : {query_str}")
    # for now always use this doc_id. real implmentation should get it from search results
    response_str =  searchpythonapi.search_datastore(query_str)
    return response_str


def get_doc_id(doc_query):
    print (f"in get_doc_id tool : {doc_query}")
    # for now always use this doc_id. real implmentation should get it from search results
    doc_id = "11537"

    print ("="*80 + f"\n doc_id {doc_id}")
    return str(doc_id)


def gemini_summarize(doc_id):
    print (f"in gemini_summarize tool: doc_id {doc_id}")
    bucket: str = "pratapdemobucket"
    file_path: str = "pdfs/set2/11537.pdf"
    file_path: str = "pdfs/set2/10027.pdf"

    print(f"file is {bucket}/{file_path}")
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(file_path)
    pdf_content = blob.download_as_bytes()  # Download as bytes for PyPDF2
    
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))  # Use BytesIO for in-memory access
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()


    prompt_template = """
        Return your response in bullet points which covers the key points of the text.
        ```{pdf_text}```

        BULLET POINT SUMMARY:
    """
    prompt = prompt_template.format(pdf_text=text[1:3000000])
    print (f"document text extracted. len of prompt{len(prompt)}")
    print("calling gemini-flash")


    response = model_summarizer.generate_content(
        [prompt],
        generation_config=summarizer_gen_config,
        safety_settings=safety_settings)

    if response.candidates[0].finish_reason != 1 :
        print (f"ERROR: {response.candidates[0].finish_reason}")
        print (f"ERROR: {response.candidates[0]}")
        
        response_str = f"ERROR: {response.candidates[0].finish_reason}"
    else:
        response_str = response.candidates[0].content.parts[0].text
        print (response_str)
    
    return response_str

search_datastore_fd = FunctionDeclaration(
    name="search_datastore",
    description="Search through the datastore of many pdfs, and return an answer along with citations",
    parameters={
        "type": "object",
        "properties": {"query_str": {"type": "string", "description": "query string "}},
    },
)

gemini_summarize_fd = FunctionDeclaration(
    name="gemini_summarize",
    description="Get the summary of a particular document identified by the document id.",
    parameters={
        "type": "object",
        "properties": {"doc_id": {"type": "string", "description": "Document id"}},
    },
)

get_doc_id_fd = FunctionDeclaration(
    name="get_doc_id",
    description="Get document id.",
    parameters={
        "type": "object",
        "properties": {"doc_query": {"type": "string", "description": "Query to get the document"}},
    },
)

tools = Tool(
    function_declarations=[gemini_summarize_fd, get_doc_id_fd,search_datastore_fd],
)


# Set safety settings
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
}

model_router = GenerativeModel(
    model_name=model_name_gemini_15_flash,
    generation_config=GenerationConfig(temperature=0.1),
    system_instruction=[
        "You are a  document helper bot.",
        "Use [get_doc_id] to retrive the document id from description provided",
        "If user asks for summary of a document, then use [get_doc_id] to get the doc_id and then use  "
        "[gemini_summarize] to summarize a document identified by doc_id",
        "For all other questions use the [search_datastore] tool, to get search results. ",
        "Then Use the search results to formulate a response for the user. ",
        "Provide a nice answer, and make sure to pass on the reference links provided by the search tool"
    ],
    tools = [tools]
)
chat = model_router.start_chat()


def ask_gemini_to_select_tool(prompt):
    response = chat.send_message(prompt)
    print(f"ask_gemini_to_select_tool {response.candidates[0].content.parts[0].function_call.name}")
    return response


def needs_tool(response):
    try :
        if hasattr(response, 'text'):
            print (f"got finalresponse. no need for tool")
            #final_answer.content = response.text
            return False
        else :
            # will not hit here. will hit the except
            print ("REALLY? how did you get here?")
            return True
    except:
        # return true if text is not found??
        print (f"Needs a tool ")
        return True

@cl.on_message  # this function will be called every time a user inputs a message in the UI
async def main(message: cl.Message):
    """
    This function is called every time a user inputs a message in the UI.
    It sends back an intermediate response from the tool, followed by the final answer.

    Args:
        message: The user's message.

    Returns:
        None.
    """


    update_message = await cl.Message(content="Processing..").send()

    # Call the tool
    #final_answer.content = await tool()

    # send the first message to Gemini-chat to get the first tool to select
    prompt = message.content
    response = await cl.make_async (ask_gemini_to_select_tool)(prompt)

    while True:
        print ("MAIN LOOP " * 10)
        print (f"prompt {prompt}")

        # check if we have the final answer to send to the user
        if not (needs_tool(response)):
            print (f"---got finalresponse")
            # todo: is this needed here or will it be taken care outside the loop?
            await cl.Message(content=response.text).send() 
            break

        function_call = response.candidates[0].function_calls[0]
        print ("+"*30+ f"calling the next funcaion {function_call.name}")

        if (function_call.name == "gemini_summarize"):
            #response = await cl.make_async (call_tool)(response)
            update_message.content = f"Calling gemini_summarize. if document is long, could take several seconds...  "
            await update_message.update()
            #await cl.Message(content=f"Calling gemini_summarize. if document is long, could take several seconds...  ").send()
            response_str = await cl.make_async (gemini_summarize)( function_call.args['doc_id'])
        elif  (function_call.name == "get_doc_id"):
            update_message.content = f"using tool to get doc_id.."
            await update_message.update()
            response_str = await cl.make_async (get_doc_id)(doc_query=function_call.args['doc_query'])
        elif (function_call.name == "search_datastore"):
            update_message.content = f"Searching datastore..."
            await update_message.update()
            #await cl.Message(content=f"Searching datastore...  ").update()
            response_str = await cl.make_async (search_datastore)(query_str=function_call.args['query_str'])
        else :
            print ("Should not come here!! ERROR")
            #print (response)
            break

        # send the response from the tool back to chat
        response = chat.send_message(
            Part.from_function_response(
                    name=function_call.name,
                    response={
                        "content": response_str,
                    },
                ),
            )


    print ("Completed all tools, now will wait for user input")
    #await update_message.update()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
    app = cl.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), headless=False)

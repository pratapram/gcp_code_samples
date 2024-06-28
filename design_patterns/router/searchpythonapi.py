#from google.cloud import translate_v2 

from typing import List
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine
import os 
import json
import re

from google.cloud.discoveryengine_v1 import *


#from google.cloud import translate

import sys

project_id = ""
location = "global"                    # Values: "global", "us", "eu"
data_store_id = ""
search_query = ""



def parse_external_link(url=''):
    protocol_regex = r'^(gs)://'

    match = re.match(protocol_regex, url)
    protocol = match.group(1) if match else None

    if protocol == 'gs':
        return re.sub(protocol_regex, 'https://storage.cloud.google.com/', url)
    else:
        return url


def replace_references(text: str, references: List):
    for i, reference in enumerate(references):
        placeholder = f"[{i + 1}]"
        text = text.replace(placeholder,
                            f"{placeholder}({parse_external_link(reference.uri)})")
    return text

def add_references_answers(text: str, citations: List,response):
    textref = f"\n References:"
    textlinks = []
    
    for i, citation in enumerate(citations):
        citindex = int(citation.sources[0].reference_id)
        url = response.answer.references[citindex].chunk_info.document_metadata.uri
        title = response.answer.references[citindex].chunk_info.document_metadata.title
        if not any(url in link for link in textlinks):
            textlinks.append(f"\n [{title}]({url})")
    text = text + textref + "".join(textlinks)
    return text

def search_datastore(query:str):
    return search_sample(project_id, location, data_store_id,query)

def search_sample( 
    project_id: str,
    location: str,
    data_store_id: str,
    search_query: str,
) -> List[discoveryengine.SearchResponse]:
    #  For more information, refer to:
    # https://cloud.google.com/generative-ai-app-builder/docs/locations#specify_a_multi-region_for_your_data_store
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )

    # Create a client
    client = discoveryengine.SearchServiceClient(client_options=client_options)

    # The full resource name of the search engine serving config
    # e.g. projects/{project_id}/locations/{location}/dataStores/{data_store_id}/servingConfigs/{serving_config_id}
    serving_config = client.serving_config_path(
        project=project_id,
        location=location,
        data_store=data_store_id,
        serving_config="default_config",
    )

    # Optional: Configuration options for search
    # Refer to the `ContentSearchSpec` reference for all supported fields:
    # https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchRequest.ContentSearchSpec
    content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
        # For information about snippets, refer to:
        # https://cloud.google.com/generative-ai-app-builder/docs/snippets
        snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
            return_snippet=True
        ),
        # For information about search summaries, refer to:
        # https://cloud.google.com/generative-ai-app-builder/docs/get-search-summaries
        summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
            summary_result_count=5,
            include_citations=True,
            ignore_adversarial_query=True,
            ignore_non_summary_seeking_query=True,
        ),
    )

    # Refer to the `SearchRequest` reference for all supported fields:
    # https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchRequest
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=search_query,
        page_size=1,
        content_search_spec=content_search_spec,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )


    response = client.search(request)


    try:
        content = f"{replace_references(response.summary.summary_text, response.summary.summary_with_metadata.references)}"
        #content = f"{add_references_answers(response.answer.answer_text, response.answer.citations,response)}"
        content = f"{response.summary.summary_text}  {response.summary.summary_with_metadata.references}"
        print (content)

    except AttributeError:
        print ("Caught AttributeError Exception")
        content = f"{response.reply.summary.summary_text}"
    
    #print(response.summary.summary_with_metadata)    
    return content




#querystr = "relationship between pollution and cancer"
#response = search_sample(project_id=project_id, location=location, data_store_id = data_store_id, search_query = querystr)

#response = search_datastore(querystr)

#print (response)
#exit(0)




# from google.protobuf.json_format import MessageToDict

# data = MessageToDict(response._pb, including_default_value_fields=True)
# print(data)

# #MessageToDict()
# #translate.Client()
# #exit(0)
# name1 = response.results[0].document.name
# derived_struct_data = dict(response.results[0].document.derived_struct_data)

# print (f"PRINTING {name1 } ")

# #snippets = list(derived_struct_data.snippets)
# snippets = derived_struct_data['snippets']
# print (f"PRINTING {str(derived_struct_data)}")

# #response_json = google.protobuf.json_format.MessageToJson(response)
# for field,value in derived_struct_data.items():

#     print (f" INSIDE LOOP { field }-- {value}" )
#     if field == 'snippets':
#         snippet_dict = dict(value)
#         for s in snippet_dict.keys():
#             print(f" INNERLOOP {s} ---> {snippet_dict[s]}") 

#     #snippets -> list_value -> struct_value -> snippet

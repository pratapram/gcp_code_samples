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

import chainlit as cl
from vertexai.preview import reasoning_engines

PROJECT_ID = "YOUR_PROJECT_ID"
LOCATION = "us-central1"
REASONING_ENGINE_ID = "" # Your reasoning engine id
remote_agent = reasoning_engines.ReasoningEngine(f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}")

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
    query = message.content
    print (f"sending {query} to remote_agent")
    update_message = await cl.Message(content="Processing..").send()
    
    response = remote_agent.query(input=query,
        config={"configurable": {"session_id": "demo1"}},
    )

    print (f"got response {response['output']}")
    update_message = await cl.Message(content=response["output"]).send()

if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
    app = cl.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), headless=False)

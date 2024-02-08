from botbuilder.core import ActivityHandler, ConversationState, TurnContext, UserState
from botbuilder.schema import ChannelAccount

# from rpay_chat_bot.user_profile import UserProfile
from data_models.user_profile import UserProfile
from data_models.conversation_data import ConversationData
import time
from datetime import datetime
from openai import AzureOpenAI
import sys
from config import DefaultConfig
import json
import os
from botbuilder.schema import HeroCard, CardAction, ActionTypes, CardImage, Attachment, Activity, ActivityTypes
from botbuilder.core import TurnContext, MessageFactory, CardFactory

import pyodbc
import inspect
import requests
import openai


class StateManagementBot(ActivityHandler):

    connection = None
    user_response_system_prompt = None

    def init_meta_prompt() -> any:
        # print("init")
        # read all lines from a text file
        
        with open("metaprompt-1.txt", "r") as file:
            data = file.read().replace("\n", "")
        # print(data)
        chat_history = [{"role": "system", "content": data}]
        return chat_history

    def init_response_meta_prompt() -> any:
        # print("init")
        # read all lines from a text file
        
        with open("metaprompt-2.txt", "r") as file:
            data = file.read().replace("\n", "")
            return data
        # print(data)
        # chat_history = [{"role": "system", "content": data}]
        # return chat_history


    def __init__(self, conversation_state: ConversationState, user_state: UserState):
        if conversation_state is None:
            raise TypeError(
                "[StateManagementBot]: Missing parameter. conversation_state is required but None was given"
            )
        if user_state is None:
            raise TypeError(
                "[StateManagementBot]: Missing parameter. user_state is required but None was given"
            )

        self.conversation_state = conversation_state
        self.user_state = user_state
        self.config =  DefaultConfig()

        self.conversation_data_accessor = self.conversation_state.create_property(
            "ConversationData"
        )
        self.user_profile_accessor = self.user_state.create_property("UserProfile")
        if StateManagementBot.connection is None:
            print("Connecting to database....")
            l_connection = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};SERVER=' + self.config.az_db_server + ';DATABASE=' + self.config.az_db_database + ';UID=' + self.config.az_db_username + ';PWD=' + self.config.az_db_password)
            StateManagementBot.connection = l_connection
            print("Connection to database established")

    async def on_message_activity(self, turn_context: TurnContext):
        # Get the state properties from the turn context.
        user_profile = await self.user_profile_accessor.get(turn_context, UserProfile)
        conversation_data = await self.conversation_data_accessor.get(
            turn_context, ConversationData
        )

        if user_profile.name is None:
            # First time around this is undefined, so we will prompt user for name.
            if conversation_data.prompted_for_user_name:
                # Set the name to what the user provided.
                user_profile.name = turn_context.activity.text

                conversation_data.chat_history = StateManagementBot.init_meta_prompt()

                # Acknowledge that we got their name.
                await turn_context.send_activity(
                    f"Thanks { user_profile.name }. Let me know how can I help you today"
                )

                # Reset the flag to allow the bot to go though the cycle again.
                conversation_data.prompted_for_user_name = False
            else:
                # Prompt the user for their name.
                await turn_context.send_activity("I am your AI Assistant from Contoso Retail. I can help you quickly get to it!"+\
                                                  "Can you help me with your name?")

                # Set the flag to true, so we don't prompt in the next turn.
                conversation_data.prompted_for_user_name = True
        else:
            # Add message details to the conversation data.
            conversation_data.timestamp = self.__datetime_from_utc_to_local(
                turn_context.activity.timestamp
            )
            conversation_data.channel_id = turn_context.activity.channel_id

            l_chat_history = conversation_data.chat_history

            if l_chat_history is None:
                conversation_data.chat_history = StateManagementBot.init_meta_prompt()
                l_chat_history = conversation_data.chat_history
                print('chat history is not available!')
            
            ####### the following code is to be removed after testing ##############
            # conversation_data.chat_history = StateManagementBot.init_meta_prompt()
            #######  ##############
            l_chat_history.append({"role": "user", "content": turn_context.activity.text})
            print('user messaged received, there are these many messages in conversation history : ',len(l_chat_history))
            
            client = AzureOpenAI(
            azure_endpoint = self.config.az_openai_baseurl, 
            api_key=self.config.az_openai_key,   
            api_version=self.config.az_openai_version_latest
            )

            response = None
            try:
                response = client.chat.completions.create(
                model= self.config.deployment_name,
                messages=l_chat_history,
                temperature=0,
                functions=StateManagementBot.functions, 
                function_call="auto"
                )
            except Exception as e:
                print('error in openai chat completion invocation (with function calling): ',e)
                await turn_context.send_activity(
                        f"{ user_profile.name }: sorry, unable to process your request at the moment. Please try again later."
                    )
                return
            
            print('response from openai chat completion : ',response)
            function_response = None
            if response.choices[0].finish_reason == "function_call":
                response_message = response.choices[0].message
                print('aoai response message to function call : ',response_message)
                print('function name > ', response_message.function_call.name)
            
                function_name = response_message.function_call.name

                # verify function exists
                if function_name not in StateManagementBot.available_functions:
                    print(
                        "Function " + function_name + " does not exist"
                    )
                    await turn_context.send_activity(
                        f"{ user_profile.name }: sorry, I do not support the request you made. Please reach out to our customer support for further assistance."
                    )
                    return
                
                function_to_call = StateManagementBot.available_functions[function_name]

                # verify function has correct number of arguments
                function_args = json.loads(response_message.function_call.arguments)
                if self.check_args(function_to_call, function_args) is False:
                    print(
                        "Invalid number of arguments for function: " + function_name
                    )
                    await turn_context.send_activity(
                        f"{ user_profile.name }: sorry, I do not have enough information to process this request. Can you provide this information and try again?"
                    )

                                
                function_response = function_to_call(**function_args)

                print('Output of function call: >',function_response)
            #     l_chat_history.append(
            #         {
            #             "role": response_message.role,
            #             "name": response_message.function_call.name,
            #             "content": response_message.function_call.arguments,
            #         }
            #     )

            #     l_chat_history.append(
            #     {
            #         "role": "function",
            #         "name": function_name,
            #         "content": function_response,
            #     }
            # )
            else: # Function call could not be determined because of user input is not complete or could not be interpreted
                print('User input is not valid')
                response_message = response.choices[0].message.content
                l_chat_history.append({"role": "assistant", "content":response_message })
                await turn_context.send_activity(
                        f"{ user_profile.name } : { response_message }"
                    )
                return

            if function_response[1] is True:
                user_response = self.prepare_user_response(function_response[0],turn_context.activity.text)
            else:
                user_response = function_response[0]
            l_chat_history.append({"role": "assistant", "content":user_response })
            await turn_context.send_activity(
                        f"{ user_profile.name } : { user_response }"
                    )

            
    
    def get_order_status(order_id):
        response_message = ''
        cursor = None
        # if order_id is None:
        #     return "Sure, I will help you with the status of your order. Can you please the order id of the consignment?"
        try:
            cursor = StateManagementBot.connection.cursor()
            cursor.execute('SELECT * FROM dbo.consignments where OrderID = ?', order_id)
        except Exception as e:
            print(e)
            print("Error in database query execution")
        
        for row in cursor:
            print(row)
            response_message += str(row) + "\n"
        
        response_array = []
        response_array.append(response_message)
        response_array.append(True)
        return response_array
    
    def prepare_user_response(self, context, query):
        messages = []
        if StateManagementBot.user_response_system_prompt is None:
            StateManagementBot.user_response_system_prompt = StateManagementBot.init_response_meta_prompt()
        messages.append({"role": "system", "content": StateManagementBot.user_response_system_prompt})
        
        input_message = "Context: \n" + context + "\n User Query: \n" + query
        messages.append({"role": "user", "content": input_message})


        client = AzureOpenAI(
            azure_endpoint = self.config.az_openai_baseurl, 
            api_key=self.config.az_openai_key,   
            api_version=self.config.az_openai_version
            )

        response = client.chat.completions.create(
        model=self.config.deployment_name,
        messages=messages
    )
        
        print('llm response to user>\n',response)
        return response.choices[0].message.content
    

    def seek_assistance(query):
        
        l_config =  DefaultConfig()

        client = AzureOpenAI(
        base_url=f"{l_config.az_openai_baseurl}openai/deployments/{l_config.deployment_name}/extensions",
        api_key=l_config.az_openai_key,
        api_version=l_config.az_openai_version_latest,
    )

        completion = client.chat.completions.create(
        model=l_config.deployment_name,
        messages=[
            {
                "role": "user",
                "content": query,
            },
        ],
        extra_body={
            "dataSources": [
                {
                    "type": "AzureCognitiveSearch",
                    "parameters": {
                        "endpoint": l_config.ai_search_url,
                        "key": l_config.ai_search_key,
                        "indexName": l_config.ai_index_name,
                        "semanticConfiguration": l_config.ai_semantic_config,
                    }
                }
            ]
        }
    )
        rag_response = completion.choices[0].message.content
        print('search based rag and llm response : ',rag_response)
        response_array = []
        response_array.append(rag_response)
        response_array.append(False)
        client = None

        return response_array

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)

    def __datetime_from_utc_to_local(self, utc_datetime):
        now_timestamp = time.time()
        offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(
            now_timestamp
        )
        result = utc_datetime + offset
        return result.strftime("%I:%M:%S %p, %A, %B %d of %Y")
    

    functions = [
        {
            "name": "get_order_status",
            "description": "Get the current status of delivery of the order",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "number",
                        "description": "The order id of the consignment",
                    }
                },
                "required": ["order_id"],
            },
        },
        {
            "name": "seek_assistance",
            "description": "Seek general assistance or register complaint from the AI assistant",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to seek assistance for",
                    }
                },
                "required": ["query"],
            },
        }
    ]

    available_functions = {
    "get_order_status": get_order_status,
    "seek_assistance": seek_assistance
    }


    # helper method used to check if the correct arguments are provided to a function
    def check_args(self, function, args):
        print('checking function parameters')
        sig = inspect.signature(function)
        params = sig.parameters
        # Check if there are extra arguments
        for name in args:
            if name not in params:
                return False
        # Check if the required arguments are provided
        for name, param in params.items():
            if param.default is param.empty and name not in args:
                return False

        return True



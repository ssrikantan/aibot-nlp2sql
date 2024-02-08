# Contoso Retail_chat_bot

The is an AI Assistant powered by Azure Open AI.
helps users have their queries on order status (from a database) or questions answered from knowledge based, using AI Search

This bot has been created using [Bot Framework](https://dev.botframework.com), it shows how to create a simple bot that accepts input from the user and echoes it back.

This Bot application showcases the following:
    - Function calling
    - Extract intent and entities and branch off into different systems for RAG
    - Calls AI Search or calls database query

It is based on version 1 of open ai library in python. **Does not work with 0.28.1**

**towards the end of this page, refer to the steps that were to be performed to get this deployed to azure** 

## Prerequisites

This sample **requires** prerequisites in order to run.

### Install Python 3.11.7

## Running the sample
- Run `pip install -r requirements.txt` to install all dependencies
- Run `python app.py`


## Testing the bot using Bot Framework Emulator

[Bot Framework Emulator](https://github.com/microsoft/botframework-emulator) is a desktop application that allows bot developers to test and debug their bots on localhost or running remotely through a tunnel.

- Install the Bot Framework Emulator version 4.3.0 or greater from [here](https://github.com/Microsoft/BotFramework-Emulator/releases)

### Connect to the bot using Bot Framework Emulator

- Launch Bot Framework Emulator
- Enter a Bot URL of `http://localhost:3978/api/messages`


## Further reading

- [Bot Framework Documentation](https://docs.botframework.com)
- [Bot Basics](https://docs.microsoft.com/azure/bot-service/bot-builder-basics?view=azure-bot-service-4.0)
- [Dialogs](https://docs.microsoft.com/azure/bot-service/bot-builder-concept-dialog?view=azure-bot-service-4.0)
- [Gathering Input Using Prompts](https://docs.microsoft.com/azure/bot-service/bot-builder-prompts?view=azure-bot-service-4.0&tabs=csharp)
- [Activity processing](https://docs.microsoft.com/en-us/azure/bot-service/bot-builder-concept-activity-processing?view=azure-bot-service-4.0)
- [Azure Bot Service Introduction](https://docs.microsoft.com/azure/bot-service/bot-service-overview-introduction?view=azure-bot-service-4.0)
- [Azure Bot Service Documentation](https://docs.microsoft.com/azure/bot-service/?view=azure-bot-service-4.0)
- [Azure CLI](https://docs.microsoft.com/cli/azure/?view=azure-cli-latest)
- [Azure Portal](https://portal.azure.com)
- [Language Understanding using LUIS](https://docs.microsoft.com/azure/cognitive-services/luis/)
- [Channels and Bot Connector Service](https://docs.microsoft.com/azure/bot-service/bot-concepts?view=azure-bot-service-4.0)


## Deploying to Azure

Follow the steps that are documented already, to create an App Service plan, a Web app in it and an Azure Bot Service App.
Get the AppID, generate a Secret. this needs to be added to the Config section in the VS Code Project

Steps to be performed in the Web App:

- In the Application settings, under configuration, add -> SCM_DO_BUILD_DURING_DEPLOYMENT, and set the value to true
- In the General Settings, add the start up script below (**note that we need to install the ODBC Driver for SQL Sever**)

```sh
#!/bin/bash
apt-get update
apt-get install -y unixodbc-dev
ACCEPT_EULA=Y apt-get install msodbcsql18
gunicorn --bind 0.0.0.0 --worker-class aiohttp.worker.GunicornWebWorker app:APP
```
### What to include in the requirements.txt

In the VS Code project, the requirements.txt only required the following 

openai==1.11.1
botbuilder-integration-aiohttp>=4.14.0
pyodbc

### Deploying the solution to App Service 

Used the ZIP file method and cli command

```cli
az webapp deployment source config-zip --resource-group "rpay-app-rg" --name "nlp2sql-bot-web" --src "nlp2sqlbot-app.zip"
```


### Adding CORS

In the Web app, permitted the following CORS

https://botservice.hosting.portal.azure.net

https://hosting.onecloud.azure-test.net

*
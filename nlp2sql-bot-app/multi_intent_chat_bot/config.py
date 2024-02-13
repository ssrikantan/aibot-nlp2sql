#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import openai
class DefaultConfig:
    """ Bot Configuration """
    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "xxxxxxxxxxxxx")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "xxxxxxxxxxxxxx")
    ai_search_url = "https://xxxxxxxxx.search.windows.net"
    ai_search_key = "xxxxxxxxxxxxxxxx"
    ai_index_name = "contoso-retail-index"
    ai_semantic_config = "contoso-retail-config"
    az_db_server = "xxxxxxxxxxx.database.windows.net"
    az_db_database = "cdcsampledb"
    az_db_username = "xxxxxxxxxxx"
    az_db_password = "xxxxxxxxxxxxxx"
    az_openai_key = "xxxxxxxxxxxxx"
    az_openai_baseurl = "https://xxxxxxx.openai.azure.com/"
    az_openai_type = "azure"
    az_openai_version_latest = "2023-08-01-preview"
    az_openai_version = "2023-07-01-preview"
    # deployment_name = "turbo0613"  # T
    deployment_name = "gpt-4"  # T
#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import openai
class DefaultConfig:
    """ Bot Configuration """
    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "xxxxxxxxxxxxxxxxxxxxxxxxxx")

    ai_search_url = "https://xxxxxxxxxxxx.search.windows.net"
    ai_search_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ai_index_name = "contoso-retail-index"
    ai_semantic_config = "contoso-retail-config"

    az_db_server = "xxxxxxxx.database.windows.net"
    az_db_database = "cdcsampledb"
    az_db_username = "xxxxxxxxxxxx"
    az_db_password = "xxxxxxxxxxxxxxx"

    az_openai_key = "xxxxxxxxxxxxxxxxxxxx"
    az_openai_baseurl = "https://xxxxxxxxxxxx.openai.azure.com/"
    az_openai_type = "azure"
    az_openai_version_latest = "2023-08-01-preview"
    az_openai_version = "2023-07-01-preview"
    # deployment_name = "turbo0613"  # T
    deployment_name = "gpt-4"  # T

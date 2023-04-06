import openai
class ChatGPT:

    def __init__(self, organization, api_key):
        openai.organization = organization
        openai.api_key = api_key

    def get_models(self):
        return openai.Model.list()

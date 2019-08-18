import os, os.path as p
from google.cloud.translate import Client


#! If this is gonna work, need to add billing method to service. This can be done here:
#! https://console.developers.google.com/apis/api/translate.googleapis.com/overview?project=142410202562


credential_path = p.abspath(p.join(p.dirname(__file__), "api_resources/google-credentials.json"))
if not p.exists(credential_path):
    raise FileNotFoundError("Please, provide the private key for using Google Translate API")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_path


class GoogleTranslator(Client):
    pass


from zeep import Client

"""
Use:
    client = GoPressAPI()
    output = client.service.get_categories(client.license_key)
TODO: add license key by default at each service method call
"""
#! Needs a license_key when doing requests


class GoPressAPI(Client):
    
    wsdl_schema = "http://api-staging.gopress.be/wsoutput?WSDL"
    license_key = ""

    def __init__(self):
        super(GoPressAPI, self).__init__(self.wsdl_schema)

    
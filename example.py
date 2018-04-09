from twentyi_api import api

auth = {
            "bearer": "base64medaddy",
#            "username": "absolutely@thebestemail.net",
#            "password": "SuperSecurePassword"
       }

twentyi = api.TwentyIRestAPI(auth=auth)

domains = twentyi.get("/domain")
packages = twentyi.get("/package")

layout = "{:<40}{:<10}"
print(layout.format("Domain name", "ID"))
print("{:=<40}{:=>10}".format("=", "="))
for domain in domains:
    print(layout.format(domain["name"], domain["id"]))

print()

layout = layout+"{:<30}"
print(layout.format("Package name", "ID", "Type"))
print("{:=<40}{:=>10}{:=>30}".format("=", "=", "="))
for package in packages:
    print(layout.format(package["name"], package["id"], package["packageTypeName"]))

twentyi.post("/domain/example.com/claimName")

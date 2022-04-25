import requests


# property search
url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"

querystring = {"location":"dallas, tx","home_type":"Houses"}

headers = {
	"X-RapidAPI-Host": "zillow-com1.p.rapidapi.com",
	"X-RapidAPI-Key": "a271625fdbmsh9c07327c04cb02bp1314d1jsn9ac44145b089"
}

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)

# get property details
url = "https://zillow-com1.p.rapidapi.com/property"

querystring = {"zpid":"69670062"}

headers = {
	"X-RapidAPI-Host": "zillow-com1.p.rapidapi.com",
	"X-RapidAPI-Key": "a271625fdbmsh9c07327c04cb02bp1314d1jsn9ac44145b089"
}

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)
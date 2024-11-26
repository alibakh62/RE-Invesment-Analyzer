# API Specifications

## ExtendedProperty Search

Note: Except for the property address, all the other parameters are optional. 
Note: If an exact address is provided, the response from this endpoint is a `zpid` which should be used in in the property details endpoint to get more information about the property. If a more general address is provided (anything that doesn't specify a house, for example, a city or neighborhood), the response will be a list of properties.

query = {}  # query parameters
url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"

querystring = {f"location": str(query['address']),
                "page":"2",
                "status_type":str(query['status_type']),
                "home_type":str(query['property_type']),
                "sort":str(query['sort_by']),
                "minPrice":str(query['price'][0]),
                "maxPrice":str(query['price'][1]),
                "bathsMin":str(query['bathrooms'][0]),
                "bathsMax":str(query['bathrooms'][1]),
                "bedsMin":str(query['bedrooms'][0]),
                "bedsMax":str(query['bedrooms'][1]),
                "sqftMin":str(query['square_feet'][0]),
                "sqftMax":str(query['square_feet'][1]),
                "buildYearMin":str(query['build_year'][0]),
                "buildYearMax":str(query['build_year'][1]),
                "daysOn":str(query['days_on_zillow']),}

headers = {
    "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com",
    "X-RapidAPI-Key": "<your API key>"
}

response = requests.request("GET", url, headers=headers, params=querystring)

## Property Details
Getting property details through Zillow property ID (zpid)

url = "https://zillow-com1.p.rapidapi.com/property"

querystring = {"zpid": str(zpid)}

headers = {
    "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com",
    "X-RapidAPI-Key": "<your API key>"
}

response = requests.request("GET", url, headers=headers, params=querystring)

## Property Images
Getting property images through Zillow property ID (zpid)

url = "https://zillow-com1.p.rapidapi.com/images"

querystring = {"zpid": str(zpid)}

headers = {
    "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com",
    "X-RapidAPI-Key": "<your API key>"
}

response = requests.request("GET", url, headers=headers, params=querystring)

## Property Rent Estimate
Getting property rent estimate through Zillow property ID (zpid)

url = "https://zillow-com1.p.rapidapi.com/rentEstimate"

querystring = {"propertyType": str(property_type),"address": str(address),"beds": str(beds),"baths": str(baths)}

headers = {
    "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com",
    "X-RapidAPI-Key": "<your API key>"
}

response = requests.request("GET", url, headers=headers, params=querystring)

## Property Search by MLS
Getting property details through property MLS number

url = "https://zillow-com1.p.rapidapi.com/propertyByMls"

querystring = {"mls": f"{str(mls_number)}"}

headers = {
    "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com",
    "X-RapidAPI-Key": "<your API key>"
}

response = requests.request("GET", url, headers=headers, params=querystring)
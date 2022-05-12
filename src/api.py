import requests
import json


def property_search(query):
    # extended property search
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
        "X-RapidAPI-Key": "a271625fdbmsh9c07327c04cb02bp1314d1jsn9ac44145b089"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response


def property_detail(zpid):
    # get property details
    url = "https://zillow-com1.p.rapidapi.com/property"

    querystring = {"zpid": str(zpid)}

    headers = {
        "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com",
        "X-RapidAPI-Key": "a271625fdbmsh9c07327c04cb02bp1314d1jsn9ac44145b089"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response


def property_image(zpid):
    url = "https://zillow-com1.p.rapidapi.com/images"

    querystring = {"zpid": str(zpid)}

    headers = {
        "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com",
        "X-RapidAPI-Key": "a271625fdbmsh9c07327c04cb02bp1314d1jsn9ac44145b089"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response


def rent_estimate(property_type, address, beds=3, baths=2):
    url = "https://zillow-com1.p.rapidapi.com/rentEstimate"

    querystring = {"propertyType": str(property_type),"address": str(address),"beds": str(beds),"baths": str(baths)}

    headers = {
        "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com",
        "X-RapidAPI-Key": "a271625fdbmsh9c07327c04cb02bp1314d1jsn9ac44145b089"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response


def search_by_mls(mls_number):
    url = "https://zillow-com1.p.rapidapi.com/propertyByMls"

    querystring = {"mls": f"{str(mls_number)}"}

    headers = {
        "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com",
        "X-RapidAPI-Key": "a271625fdbmsh9c07327c04cb02bp1314d1jsn9ac44145b089"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response
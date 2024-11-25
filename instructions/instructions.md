I want to rewrite this Streamlit app in Python. I have developed it couple of years ago and I would like to take it further.

The app has the following pages:
1. Investment Criteria: Here, user can set their investment criteria. These investment criteria will be used in the following pages.
2. Search: Here, user can search for properties based on their search criteria which is shown in the UI.
3. Property Details: When the user selects a property from the search results, they will be redirected to this page where they can see the details of the property.
4. Scenario Analysis: Here, user can analyze different investment scenarios and compare them.

The code is structured as follows:
1. `src` directory: This directory contains all the code for the app. This includes the following:
    - `utils.py`: This file is the brain of the app. It contains all the calculations and logic for the app.
    - `config.py`: This file contains all the configuration for the app.
    - `api.py`: This file contains all the code for the API calls to Zillow API in RapidAPI.
2. `pages` directory: This directory contains all the code for the app pages. The main pages are desribed above.
3. `data` directory: This directory contains all the data for the app. It's a temporary placeholder for keeping track of the user session data and the data for the app.

I want a compelete refactoring of the code to remove unnecessary code and make the code more readable and maintainable. Also, any new improvements or optimizations can be made.
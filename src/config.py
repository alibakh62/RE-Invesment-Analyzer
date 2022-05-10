import time

version = "new"  #time.strftime("%m%d%Y_%H%M%S")

DEBUG_MODE='DEV'
if DEBUG_MODE == 'DEV':
    BASE_DIR='data'
elif DEBUG_MODE == 'PROD':
    BASE_DIR='data'
elif DEBUG_MODE == 'TEST':
    BASE_DIR='../data'
USER_METRICS=f'user_metrics_{version}.json'
USER_FINANCE=f'user_finance_{version}.json'
PROP_SEARCH=f'search_data_{version}.csv'
PROP_SEARCH_RESPONSE=f'search_response_{version}.json'
PROP_SEARCH_REFINED=f'search_data_refined_{version}.csv'
PROP_SEARCH_WITH_METRICS=f'search_data_with_metrics_{version}.csv'
PROP_SEARCH_WITH_METRICS_FILTERED=f'search_data_with_metrics_filtered_{version}.csv'
USER_ASSUMPTIONS=f'user_assumptions_output_{version}.pkl'
USER_ASSUMPTIONS_MODIFIED=f'user_assumptions_modified_{version}.pkl'
CASH_FLOW=f'cash_flow_output_{version}.pkl'
AMORTIZATION=f'amortization_output_{version}.pkl'
if DEBUG_MODE == 'DEV':
    LOG_DIR='logs'
elif DEBUG_MODE == 'PROD':
    LOG_DIR='logs'
elif DEBUG_MODE == 'TEST':
    LOG_DIR='../logs'
LOG_PROP_DETAILS='prop_details_log'
SELECTED_PROPERTY=f'selected_property_{version}.pkl'
PROP_DETAIL_RESPONSE="prop_details"
PROP_IMAGES="images"
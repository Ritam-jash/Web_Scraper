class GoogleMapsSelectors:
    """CSS selectors for Google Maps elements"""
    
    # Search elements
    SEARCH_BOX = "input[id='searchboxinput']"
    SEARCH_BUTTON = "button[id='searchbox-searchbutton']"
    
    # Results panel
    RESULTS_PANEL = "div[role='main']"
    BUSINESS_LINKS = "div[role='main'] a[data-value='Directions']"
    BUSINESS_ITEMS = "div[role='main'] div[jsaction]"
    
    # Business details
    BUSINESS_NAME = "h1[data-attrid='title']"
    BUSINESS_ADDRESS = "button[data-item-id='address']"
    BUSINESS_PHONE = "button[data-item-id*='phone']"
    BUSINESS_WEBSITE = "a[data-item-id='authority']"
    BUSINESS_RATING = "span.MW4etd"
    BUSINESS_REVIEW_COUNT = "span.UY7F9"
    BUSINESS_CATEGORY = "button[jsaction*='category']"
    BUSINESS_HOURS = "div[data-item-id='oh'] div.t39EBf"
    BUSINESS_PRICE_RANGE = "span.mgr77e"
    
    # Navigation
    BACK_BUTTON = "button[data-value='Back']"
    CLOSE_BUTTON = "button[aria-label='Close']"
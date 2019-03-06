# GLOBAL VARIABLES

volunteer_file_name = "volunteers.pkl"
# Categories as provided to those requesting review (same categories Aiomebot uses)

review_categories = ["Arts", "Everyday life", "Engineering and technology", "General", "Geography and places",
                     "History", "Natural sciences and mathematics", "Language and literature",
                     "Philosophy and religion", "Social sciences and society", "List"]


# review_categories = ["Arts"]
# time intervals offered by template
time_intervals = {"monthly": 2419200, "quarterly": 7776000, "halfyearly": 15811200, "annually": 31536000}

# WP:PRV headings are different. This is a map to the translation.
# Key (String): PRV Heading Title. Value (String[]): Request Headings
volunteer_heading_translations = {u"applied sciences and technology": [u"Engineering and technology"],
                                  u"arts": [u"Arts"],
                                  u"everyday life": [u"Everyday life"],
                                  u"geography": [u"Geography and places"],
                                  u"history": [u"History"],
                                  u"language and literature": [u"Language and literature"],
                                  u"mathematics": [u"Natural sciences and mathematics"],
                                  u"natural Sciences": [u"Natural sciences and mathematic"],
                                  u"philosophy and religion": [u"Philosophy and religion"],
                                  u"society and social sciences": [u"Social sciences and society"],
                                  u"general copy editors": [u"General"]
                                  }

review_listing_directory = u"User:AnomieBOT/C/"
transclusion_listing_directory = u"User:KadaneBot/PR/Categories/"

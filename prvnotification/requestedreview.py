from prvnotification import definitions
import mwparserfromhell
import pywikibot


class RequestedReview:
    # Represents requested article review. (Name, request page, date)

    _allRequests = {}

    def __init__(self, article, category, request_page, date):
        self.article = article
        self.request_page = request_page
        self.date = date
        self.category = category

    @property
    def article(self):
        return self._article

    @article.setter
    def article(self, article):
        self._article = article

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category):
        if category in definitions.review_categories:
            self._category = category

    @property
    def request_page(self):
        return self._request_page

    @request_page.setter
    def request_page(self, request_page):
        self._request_page = request_page

    @property
    def date(self):
        return self._date.split("T")[0]

    @date.setter
    def date(self, date):
        self._date = date



    @property
    def wiki_text(self):
        return u"|[[{}]] <sub>([[WP:{}|Peer Review]])</sub> ||style=\"width: 6em;\"| {}".format(self.article, self.request_page,
                                                                              self.date)

    @classmethod
    def get_all_requests_by_category(cls, site, force_update=False):
        # key: string (category name)
        # value: RequestedReview[]

        if not force_update and len(cls._allRequests.keys()) == len(definitions.review_categories):
            print("Returning cache")
            return cls._allRequests

        print("Generating requests")
        cls._allRequests = {}

        for category in definitions.review_categories:
            page_name = u"{}{} peer reviews".format(definitions.review_listing_directory, category)
            cls._allRequests[category] = RequestedReview.get_request_by_category(category,
                                                                                 pywikibot.Page(site, page_name)
                                                                                 )

        return cls._allRequests

    @staticmethod
    def get_request_by_category(category, page):
        return_value = []

        templates = mwparserfromhell.parse(page.text).filter_templates()

        for template in templates:
            if template.name.startswith(u"CF/") and len(template.params) == 4:
                params = template.params

                return_value.append(RequestedReview(params[0].split(u'/')[1], category, params[0], params[2]))

        return return_value

    @classmethod
    def generate_transclusion(cls, category, page):

        text = u"{| class=\"wikitable sortable\" style=\"width: 34em;\"\n|-\n!Article !! Date Added\n"

        for value in cls._allRequests[category]:
            text += u"|-\n"
            text += value.wiki_text + u'\n'
        text += u"|}"
        if page.strip() != text.strip():
            return page, text
        else:
            return None

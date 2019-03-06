from prvnotification import definitions
import pywikibot
import mwparserfromhell
import jsonpickle
import os
import traceback
from datetime import datetime

class Volunteer():

    _cached_record = {}
    _live_record = {}
    _cache_loaded = False

    def __init__(self, name, date_added):


        if name in Volunteer._live_record:
            raise ValueError("Duplicate user '[[User:{0}]]' found".format(name))

        self.name = name
        self.date_added = date_added if name not in Volunteer._cached_record \
            else Volunteer._cached_record[name].date_added

        # dictionary (key: review_category ; value: Subscription)
        # todo make subscriptions none and import last message sent from _cached_record
        self.subscriptions = None if self.name not in Volunteer._cached_record\
            else Volunteer._cached_record[self.name].subscriptions

        if name not in Volunteer._live_record:

            Volunteer._live_record[name] = self



    def __getitem__(self, subscription_category):
        if subscription_category in subscriptions:
            return subscriptions[subscription_category]
        else:
            return None


    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def date_added(self):
        return self._date_added

    @date_added.setter
    def date_added(self, date_added):
        # Todo add date checking
        self._date_added = date_added

    @property
    def subscriptions(self):
        return self._subscriptions

    @subscriptions.setter
    def subscriptions(self, subscription):
        if subscription is None:
            self._subscriptions = {}
        else:
            self._subscriptions = subscription

    def add_subscription(self, review_category, time_interval, date):

        if review_category in definitions.review_categories:
            if review_category not in self.subscriptions:
                self._subscriptions[review_category] = Subscription(review_category, time_interval, date)
            else:
                self._subscriptions[review_category].time_interval = time_interval

    def remove_subscription(self, subscription):
        if subscription in definitions.review_categories and subscription in self._subscriptions:
            del self.subscriptions[subscription]

    @classmethod
    def save_volunteers(cls, pretty=False):
        if pretty:
            return cls.pretty_save()
        elif len(cls._live_record) > 0:
            return jsonpickle.encode(cls._live_record)
        else:
            return None

    @classmethod
    def pretty_save(cls):
        string = u""
        for key in cls.get_live_record():
            string += u"{}".format(cls._live_record[key])
        return string
    @classmethod
    def load_volunteers(cls, text):

        cls._cached_record = jsonpickle.decode(text)
        print(u"Loaded {} previous volunteers".format(len(cls._cached_record)))
    '''
    @classmethod
    def import_subscribers_from_prv(cls, site_text, date):
        site_text = site_text.split(u"\n")
        current_interest = u""
        for line in site_text:

            parsed_text = mwparserfromhell.parse(line)
            templates = parsed_text.filter_templates()
            section = parsed_text.filter_headings()

            if len(section) > 0 and u"{}".format(section[0].title).strip() in definitions.volunteer_heading_translations:
                current_interest = u"{}".format(section[0].title.strip())

            for template in templates:
                try:
                    if template.name == u"PRV":
                        name = u'{}'.format(template.params[0])
                        volunteer = Volunteer(name, date) if name not in cls.get_live_record() else \
                        cls.get_live_record()[name]
                        if u"{}".format(template.get(u"contact").split(u'=')[1]) in definitions.time_intervals:
                        
                            if len(current_interest) > 0:
                                for interest in definitions.volunteer_heading_translations[current_interest]:
                                    volunteer.add_subscription(interest, u"{}".format(template.get(u"contact").split(u'=')[1]))
                        else:
                            volunteer.remove_subscription(interest)


                except ValueError:
                    continue
    '''
    @classmethod
    def import_subscribers_from_prv(cls, site_text, date):
        site_text = site_text.split(u"\n")
        current_interest = u""
        for line in site_text:

            parsed_text = mwparserfromhell.parse(line)
            templates = parsed_text.filter_templates()
            section = parsed_text.filter_headings()

            if len(templates) > 0 and len(current_interest) > 0 and templates[0].name == u"PRV":
                user_name = u'{}'.format(templates[0].params[0])
                try:
                    time_interval = u"{}".format(templates[0].get(u"contact").split(u'=')[1]).lower()
                except ValueError:
                    time_interval = u"never"
                if time_interval in definitions.time_intervals:
                    volunteer = Volunteer(user_name, date) if user_name not in cls.get_live_record() else \
                        cls.get_live_record()[user_name]
                    volunteer.add_subscription(current_interest, time_interval, date)
                elif user_name in cls.get_live_record():
                    cls.get_live_record()[user_name].remove_subscription(current_interest)
            elif len(section) > 0 and section[0].title.strip().lower() in definitions.volunteer_heading_translations:
                current_interest = definitions.volunteer_heading_translations[section[0].title.strip().lower()][0]

    @classmethod
    def generate_mailing_list(cls):
        string = ""
        for key in cls._live_record:
            string += u"* {{{{Mailing list member|user={}}}}}\n".format(key)
        return string

    @classmethod
    def generate_messages_to_send(cls, date):
        message_dictionary = {}
        for name in cls.get_live_record():
            categories_ready_to_send = []
            volunteer = cls.get_live_record()[name]
            for subscription_name in volunteer.subscriptions:
                subscription = volunteer.subscriptions[subscription_name]
                interval = definitions.time_intervals[subscription.time_interval.lower()]
                registered_send = date - subscription.sub_date_added > interval
                last_send = subscription.last_contact is None or date - subscription.last_contact > interval
                if registered_send and last_send:
                    categories_ready_to_send.append(subscription)
            if len(categories_ready_to_send) > 0:
                message_dictionary[name] = categories_ready_to_send
        return message_dictionary

    def get_number_of_volunteers(cls):
        return len(cls._live_record)

    @classmethod
    def get_live_record(cls):
        return cls._live_record

    def __str__(self):
        string = u"==[[User:{0}|{0}]]==\n*Time Added (UTC): {1}\n*Subscriptions (count: {2}):\n".format(self.name,
                                                                                                        datetime.utcfromtimestamp(self.date_added).strftime('%H:%M, %d %B %Y'),
                                                                                                        len(self.subscriptions))
        for key in self.subscriptions:
            string += u"{}\n".format(self.subscriptions[key])
        return string

class Subscription:

    def __init__(self, review_category, time_interval, date_added, last_contact=None):
        self.review_category = review_category
        self.time_interval = time_interval
        self.last_contact = last_contact
        self.sub_date_added = date_added

    def __str__(self):
        return u":*[[Wikipedia:Peer_review#{0}|{0}]]\n::Date Added: {3}\n::Contact Interval: {1}\n::Last Contact: {2}\n".format\
            (self.review_category, self.time_interval.capitalize(),
             datetime.utcfromtimestamp(self.last_contact).strftime('%H:%M, %d %B %Y')
             if self.last_contact is not None else u"Never", datetime.utcfromtimestamp(self.sub_date_added).strftime('%H:%M, %d %B %Y'))

    def sent(self, date):
        self.last_contact = date
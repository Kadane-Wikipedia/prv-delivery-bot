import pywikibot
import os
import pickle
import calendar
import mwparserfromhell
import json

from prvnotification import definitions
from prvnotification.requestedreview import RequestedReview
from prvnotification.volunteerinfo import Volunteer
from datetime import datetime

# GLOBAL VARIABLES
run_date = calendar.timegm(datetime.utcnow().utctimetuple())
site = pywikibot.Site()


def send_messages(message_dictionary):
    input("Press Enter to start sending messages")
    edit_summary = u"Delivering [[WP:PRWAITING|Open Peer Review Requests]]. Want to unsubscribe? " \
                   u"Visit [[WP:PRV]] and update your contact preferences. " \
                   u"(Automated Edit; [[Wikipedia:Bots/Requests_for_approval/KadaneBot|BRFA]])"
    for name in message_dictionary:
        template = u"{{{{subst:User:KadaneBot/PR/ReviewNotification|{}".format(name)

        for subscription in message_dictionary[name]:
            template = u"{}|{}".format(template, subscription.review_category)
            subscription.sent(run_date)
        template = u"{}}}}}".format(template)

        page = pywikibot.Page(site, u"User_talk:{}".format(name))

        page.text = page.text + u"\n" + template + u" ~~~~"
        page.save(edit_summary)
        input(u"Press Enter To Continue...")


def run():

    # code to run
    # retrieve request from #Aiomie
    try:
        Volunteer.load_volunteers(pywikibot.Page(site, u"User:KadaneBot/PR/Jsondump").text)
    except json.decoder.JSONDecodeError:
        print("[WARNING]: Unable to load subscribers save file")
        pass

    Volunteer.import_subscribers_from_prv(pywikibot.Page(site, u"Wikipedia:Peer review/volunteers").text, run_date)

    message_dict = Volunteer.generate_messages_to_send(run_date)

    if len(message_dict) > 0:

        RequestedReview.get_all_requests_by_category(site)
        edit_summary = u"Updating transclusions for automated message (Automated Edit; " \
                       u"[[Wikipedia:Bots/Requests_for_approval/KadaneBot|BRFA]])"
        for category in definitions.review_categories:
            transclusion = RequestedReview.generate_transclusion(category, "{}{}".format(
                definitions.transclusion_listing_directory, category)
                                                             )

            if transclusion is not None:
                page = pywikibot.Page(site, transclusion[0])
                page.text = transclusion[1]
                page.save(edit_summary)

        send_messages(message_dict)

    edit_summary = u"Serializing task state (Automated Edit; [[Wikipedia:Bots/Requests_for_approval/KadaneBot|BRFA]])"

    page = pywikibot.Page(site, u"User:KadaneBot/PR/Jsondump")
    page.text = Volunteer.save_volunteers()
    page.save(edit_summary)
    edit_summary = u"Saving task state in human readable form (Automated Edit;" \
                   u" [[Wikipedia:Bots/Requests_for_approval/KadaneBot|BRFA]])"

    page = pywikibot.Page(site, u"User:KadaneBot/PR/Jsondump/Pretty")

    page.text = u"This is a human-readable [[WP:PRV]] volunteer list with subscription information generated on {}\n"\
                .format(datetime.utcfromtimestamp(run_date).strftime('%H:%M, %d %B %Y'))

    page.text += Volunteer.save_volunteers(pretty=True)

    page.save(edit_summary)



run()
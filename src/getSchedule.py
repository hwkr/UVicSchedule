import logging
import re
import sys
import datetime

import pytz
from bs4 import BeautifulSoup
from icalendar import Calendar, Event, vText

import uvic


COURSE_TITLE_RE = re.compile(r"[^-]+- ([A-Z]+ [0-9]+) - ([A-Z][0-9]+)")


ICAL_WEEKDAY_DICTIONARY = {
    "Su": "SU",  # TODO: Figure out if this is right
    "M": "MO",
    "T": "TU",
    "W": "WE",
    "R": "TH",
    "F": "FR",
    "S": "SA"

}

ICAL_WEEKDAYS = [
    "MO",
    "TU",
    "WE",
    "TH",
    "FR",
    "SA",
    "SU"
]

ICAL_FREQUENCY_DICTIONARY = {
    "Every Week": 1,
    "Every Second Week": 2
}


def main():
    # Set up logging
    logging.basicConfig(filename='uvicSchedule.log', level=logging.INFO, format='%(asctime)s %(message)s')

    logging.info('Starting Calendar Grabber')

    auth = uvic.Auth()

    # Attempt to open the MyCard page
    response = auth.load('https://www.uvic.ca/BAN2P/bwskfshd.P_CrseSchdDetl')

    # Once we're done with the login (if necessary), the final response object url should be at MyCard history
    logging.debug('Parsing output')
    timetable_html = response.read()
    timetable_soup = BeautifulSoup(timetable_html, "html.parser")

    courses = timetable_soup.find_all('table', attrs={
        "class": "datadisplaytable",
        "summary": "This layout table is used to present the schedule course detail"
    })

    # Make the Calendar
    cal = Calendar()
    cal.add('prodid', '-//Ben Hawker//UVic Calendar Extractor//EN')
    cal.add('version', '2.0')

    for course in courses:

        title = course.find("caption").string
        title_match = COURSE_TITLE_RE.match(title)
        code = title_match.groups()[0]
        section = title_match.groups()[1]

        logging.info('Parsing ' + code)

        meeting_times = course.find_next_sibling('table', attrs={
            "class": "datadisplaytable",
            "summary": "This table lists the scheduled meeting times and assigned instructors for this class.."
        }).find_all("tr")[1:]  # skip the first row (headers)

        for meeting_time in meeting_times:
            event = Event()

            time_soup = meeting_time.find_all("td")

            meeting_type = time_soup[5].text
            description = {
                "Instructor": time_soup[6].text,
                "Section": section
            }

            location = time_soup[3].string

            time_range = [datetime.datetime.strptime(time.strip(), "%I:%M %p") for time in
                          time_soup[1].text.split("-")]
            date_range = [datetime.datetime.strptime(date.strip(), "%b %d, %Y") for date in
                          time_soup[4].text.split("-")]

            interval = ICAL_FREQUENCY_DICTIONARY[time_soup[0].text]
            weekdays = [ICAL_WEEKDAY_DICTIONARY[day] for day in time_soup[2].text.strip()]

            start_datetime = date_range[0].replace(hour=time_range[0].hour, minute=time_range[0].minute,
                                                   tzinfo=pytz.timezone("America/Vancouver"))
            while ICAL_WEEKDAYS[start_datetime.weekday()] != weekdays[0]:
                start_datetime += datetime.timedelta(days=1)

            end_datetime = start_datetime + (time_range[1] - time_range[0])
            until_datetime = date_range[1].replace(tzinfo=pytz.timezone("America/Vancouver"))

            event.add('summary', code + " " + meeting_type)
            event.add('dtstart', start_datetime)
            event.add('dtend', end_datetime)
            event.add('dtstamp', datetime.datetime.utcnow().replace(tzinfo=pytz.utc))
            event.add('rrule', {'FREQ': ['weekly'], 'BYDAY': weekdays, 'INTERVAL': interval, "UNTIL": until_datetime})

            event['location'] = vText(location)
            event['description'] = vText("\n".join([item + ": " + value for item, value in description.iteritems()]))

            cal.add_component(event)

    print cal.to_ical()

    f = open('cal.ics', 'wb')
    f.write(cal.to_ical())
    f.close()

    logging.info('Done')


if __name__ == "__main__":

    if len(sys.argv) is not 2:
        print "Usage: python {0} <netlink>".format(sys.argv[0])
        sys.exit(0)

    try:
        main()
    except KeyboardInterrupt:
        print '\nExiting by user request.\n'
        sys.exit(0)

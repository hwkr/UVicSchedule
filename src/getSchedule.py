import logging
import re
import sys
from datetime import datetime

from bs4 import BeautifulSoup

import uvic

COURSE_TITLE_RE = re.compile(r"[^-]+- ([A-Z]+ [0-9]+) - ([A-Z][0-9]+)")

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
    for course in courses:
        title = course.find("caption").string
        title_match = COURSE_TITLE_RE.match(title)
        course_code = title_match.groups()[0]
        course_section = title_match.groups()[1]

        logging.info('Parsing ' + course_code)

        course_info = course.find_next_sibling('table', attrs={
            "class": "datadisplaytable",
            "summary": "This table lists the scheduled meeting times and assigned instructors for this class.."
        }).find_all("tr")[1].find_all("td")

        date_range = [datetime.strptime(date.strip(), "%b %d, %Y") for date in course_info[4].string.split("-")]

        print course_code

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

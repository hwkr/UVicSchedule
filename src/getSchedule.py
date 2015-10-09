import sys
import datetime
import logging

from bs4 import BeautifulSoup

import uvic


def main():
    # Set up logging
    logging.basicConfig(filename='uvicSchedule.log', level=logging.INFO, format='%(asctime)s %(message)s')

    logging.info('Starting Calendar Grabber')

    auth = uvic.Auth()

    # Attempt to open the MyCard page
    response = auth.load('https://www.uvic.ca/BAN2P/bwskfshd.P_CrseSchdDetl')

    # Once we're done with the login (if necessary), the final response object url should be at MyCard history
    logging.debug('Parsing output')
    timetable_html = response.read();
    timetable_soup = BeautifulSoup(timetable_html, "html.parser")

    courses = timetable_soup.find_all('table', attrs={
        "class": "datadisplaytable",
        "summary": "This layout table is used to present the schedule course detail"
    })

    # Save our newly found out data and the time to the file
    logging.debug('Updating balance file')
    outputString = "balance=" + ufsBalance + ";date=" + datetime.datetime.now().strftime("%a %b %d, %I:%M%p") + "\n"

    print(outputString)

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
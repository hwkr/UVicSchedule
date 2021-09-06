# Import datetime, errno, logging, os, pytz, re, and sys
import datetime
import errno
import logging
import os
import pytz
import re
import sys
# Import BeatifulSoup from bs4
from bs4 import BeautifulSoup
# Import Calendar, Event, vText from icalendar
from icalendar import Calendar, Event, vText, Alarm

# Import UVic Class from uvic.py
import uvic

# Default output_file
output_file = "calendar.ics"

# COURSE_TITLE_RE Format
COURSE_TITLE_RE = re.compile(r"([A-Z]+ [A-Z0-9]*) - ([A-Z][0-9]+)")

# ICAL Weekday Dictionary
ICAL_WEEKDAY_DICTIONARY = {
    "Su": "SU",
    "M": "MO",
    "T": "TU",
    "W": "WE",
    "R": "TH",
    "F": "FR",
    "S": "SA"
}

# ICAL Weekdays List
ICAL_WEEKDAYS = [
    "MO",
    "TU",
    "WE",
    "TH",
    "FR",
    "SA",
    "SU"
]

# ICAL Frequency Dictionary 
ICAL_FREQUENCY_DICTIONARY = {
    "Every Week": 1,
    "Every Second Week": 2
}

# UVic Building Codes
UVIC_BUILDING_CODES = {
    "Alice Ravenhill Hall": "RRA",
    "Arthur Currie": "RAC",
    "Bamfield Marine Sciences Centre": "BMSC",
    "Bev Glover Greenhouse Facility": "GGF",
    "Bob Wright Centre": "BWC",
    "Business & Economics Building": "BEC",
    "Campus Security Building": "SEC",
    "Campus Services": "CSR",
    "Carroll": "RCA",
    "Centennial Stadium": "STA",
    "Centre for Athletics, Recreation and Special Abilities": "CARSA",
    "Child Care Complex": "CCC",
    "Clearihue": "CLE",
    "Continuing Studies": "CST",
    "Cornett": "COR",
    "Cornett Building": "COR",
    "Craigdarroch Office": "CRA",
    "Cunningham": "CUN",
    "David Strong": "DSB",
    "David Strong Building": "DSB",
    "David Thompson": "RDT",
    "David Turpin": "DTB",
    "Elliott Building": "ELL",
    "Engineering Comp Science Bldg": "ECS",
    "Engineering & Computer Science": "ECS",
    "Engineering Lab Wing": "ELW",
    "Engineering Office Wing": "EOW",
    "Enterprise Data Centre": "EDC",
    "Fine Arts": "FIA",
    "First Peoples House": "FPH",
    "Fraser": "FRA",
    "Halpern Centre for Graduate Students": "GSC",
    "Health and Wellness": "HWB",
    "Helmcken": "RHE",
    "Hickman": "HHB",
    "Hodges": "RHO",
    "Hugh Stephen": "RHS",
    "Human & Social Development": "HSD",
    "Ian Stewart Complex": "ISC",
    "Jamie Cassels Centre": "JCC",
    "Joseph Cunliffe": "RJC",
    "Lansdowne Residence #1": "RL1",
    "Lou-Poy Child Care Centre": "HLP",
    "MacLaurin": "MAC",
    "Marine Technology Centre": "MTC",
    "McKinnon": "MCK",
    "McPherson Library": "LIB",
    "Mearns Centre for Learning": "MCL",
    "Medical Sciences": "MSB",
    "Michael Williams": "MWB",
    "Modular Dining Facility": "MOD",
    "Outdoor Aquatic Unit": "OAU",
    "Park": "R42",
    "Petch": "PCH",
    "Phoenix Theatre": "PNX",
    "Poole House": "RPH",
    "R. Haig Brown": "RHB",
    "Richard Wilson": "RRW",
    "Ring Road": "R40",
    "Robert Wallace Hall": "RWA",
    "Sanderson": "RSA",
    "Saunders": "SAU",
    "Saunders Annex": "SAA",
    "Sedgewick": "SED",
    "Shirley Baker": "RSB",
    "South Tower": "R43",
    "Student Union": "SUB",
    "Tower": "R41",
    "University Club": "UCL",
    "University House 1": "UH1",
    "University House 2": "UH2",
    "University House 3": "UH3",
    "University House 4": "UH4",
    "University House 5": "UH5",
    "Visual Arts": "VIA",
}

# Main
def main():
    """
    Get Schedule and Create .ics File
    """

    # Set up logging
    logging.basicConfig(filename='uvicSchedule.log', level=logging.INFO, format='%(asctime)s %(message)s')
    # Log start of script
    logging.info('Starting getSchedule')

    # Authorize with UVic Auth
    auth = uvic.Auth()

    # Attempt to open the MyCard page
    response = auth.load('https://www.uvic.ca/BAN2P/bwskfshd.P_CrseSchdDetl')

    # Once we're done with the login (if necessary), the final response object url should be at MyCard history
    # Log that the script is parsing output
    logging.debug('Parsing output')

    # Read and Parse the schedule
    timetable_html = response.read()
    timetable_soup = BeautifulSoup(timetable_html, "html.parser")

    # Create courses
    courses = timetable_soup.find_all('table', attrs={
        "class": "datadisplaytable",
        "summary": "This layout table is used to present the schedule course detail"
    })

    # Make the Calendar
    cal = Calendar()
    cal.add('version', '2.0')
    cal.add('prodid', '-//UVic Schedule//UVic Schedule to Calendar Format Script//EN')
    cal.add('X-WR-CALNAME', timetable_soup.find_all('div', attrs={"class": 'staticheaders'})[0].text.split('\n')[2])

    # Add each course to calendar
    for course in courses:
        # Create title
        title = course.find("caption").string
        # Create title match
        title_match = COURSE_TITLE_RE.search(title)
        # Create code
        code = title_match.groups()[0]
        # Create section
        section = title_match.groups()[1]
        # Create table information
        table_information = course.find_all('td')

        # Log that script is parsing a course
        logging.info('Parsing ' + code)

        # Create meeting times
        meeting_times = course.find_next_sibling('table', attrs={
            "class": "datadisplaytable",
            "summary": "This table lists the scheduled meeting times and assigned instructors for this class.."
        }).find_all("tr")[1:]  # skip the first row (headers)

        # Add meeting time for each meeting times
        for meeting_time in meeting_times:
            # Create event
            event = Event()

            # Find all times
            time_soup = meeting_time.find_all("td")
            
            if (time_soup[1].text == 'TBA'):
                logging.info('Course ' + code + ' has no Meeting Times. Skipping.')
                break

            # Create meeting type
            meeting_type = time_soup[5].text

            # Create CRN
            crn = table_information[1].text

            # Create status
            status = table_information[2].text

            # Create email
            email = table_information[3].find("a")
            email_address = "Not Available"
            if email != None:
                email_address = email.get('href').split(':')[1]

            # Create description
            description = {
                "Instructor": re.sub(" ?\([A-Z]\)", "", re.sub("  +", " ",time_soup[6].text)),
                "Section": section,
                "CRN": crn,
                "Registration Status": status,
                "Contact Information": email_address
            }

            # Create location
            location = time_soup[3].string

            # Create time range
            time_range = [datetime.datetime.strptime(time.strip(), "%I:%M %p") for time in time_soup[1].text.split("-")]
            # Create date range
            date_range = [datetime.datetime.strptime(date.strip(), "%b %d, %Y") for date in time_soup[4].text.split("-")]

            # Add interval of meeting
            interval = ICAL_FREQUENCY_DICTIONARY[time_soup[0].text]
            # Add day(s) to meeting
            weekdays = [ICAL_WEEKDAY_DICTIONARY[day] for day in time_soup[2].text.strip()]

            # Create start time
            start_datetime = date_range[0].replace(hour=time_range[0].hour, minute=time_range[0].minute, tzinfo=pytz.timezone("America/Vancouver"))
            while ICAL_WEEKDAYS[start_datetime.weekday()] not in weekdays:
                start_datetime += datetime.timedelta(days=1)

            # Create end time
            end_datetime = start_datetime + (time_range[1] - time_range[0])
            # Create duration
            until_datetime = date_range[1].replace(hour=23, minute=59, second=59, tzinfo=pytz.timezone("America/Vancouver"))

            # Add summary, dtstart, dtend, dtstamp, and rrule
            event.add('summary', code + " " + meeting_type)
            event.add('dtstart', start_datetime)
            event.add('dtend', end_datetime)
            event.add('dtstamp', datetime.datetime.utcnow().replace(tzinfo=pytz.utc))
            event.add('rrule', {'FREQ': ['weekly'], 'BYDAY': weekdays, 'INTERVAL': interval, "UNTIL": until_datetime})

            # Add location and description
            if (location != "TBA"):
                event.add('location', location + " (" + locationmatch(location) + ")")
            else:
                event.add('location', locationmatch(location))
            event.add('description', "\n".join([item + ": " + value for item, value in description.items()]))

            # Add UID
            event.add('uid', str(crn) + '-' + str(start_datetime.year) + '-' + str(start_datetime.month) + '@uvic.ca')

            # Add event to calendar component
            cal.add_component(event)

    # Output Calendar Event(s) to desired file
    with open(output_file, 'w') as f:
        f.write((cal.to_ical()).decode())
        f.close()

    # Log that the script is done
    logging.info('Done!')

# Location Match
def locationmatch(location):
    """
    Convert full-length location names to a shortcode variant

    :param location: A full-length building location string: Engineering Computer Science Bldg 125
    :return: Shortcode version of location: ECS 125
    """

    # Tokenize the room # away from the building
    # Perform if location does not equal TBA
    if (location != "TBA"):
        # Create building and room
        building, room = location.rsplit(' ', 1)

        # If we know the short code for a building, return it, otherwise pass the original value straight through
        if building in UVIC_BUILDING_CODES:
            return UVIC_BUILDING_CODES[building] + " " + room
        else:
            return location
    else:
        return location

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: python {0} [<calendar-TERM.ics>]".format(sys.argv[0]))
        sys.exit(0)
    elif len(sys.argv) == 2:
        output_file = sys.argv[1]

    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting by user request.\n")
        sys.exit(0)

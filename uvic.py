# Import http.cookiejar, mechanize, and os
import http.cookiejar
import mechanize
import os
# Import getpass from getpass
from getpass import getpass

# Cookie File for Holding Login Status for UVic NETLINK ID
COOKIES_FILE = '.cookies'

# Auth
class Auth:
    # __init__
    def __init__(self):
        # Create a mechanize browser instance
        self._browser = mechanize.Browser()
        self._browser.set_handle_equiv(True)
        self._browser.set_handle_redirect(True)
        self._browser.set_handle_referer(True)
        self._browser.set_handle_robots(False)
        self._browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
        self._browser.addheaders = [('User-agent', 'Chrome')]

        # Load the CookieJar from the CookieJar file if it exists
        self.cookies = http.cookiejar.LWPCookieJar()

        # Set Cookies to CookieJar
        self._browser.set_cookiejar(self.cookies)

        # Load COOKIES_FILE if it exists
        if os.path.isfile(COOKIES_FILE):
            self.cookies.load(COOKIES_FILE, ignore_discard=True, ignore_expires=True)

    # Load
    def load(self, url):
        """
        Login into UVic.ca, Select Term, and Display UVic Schedule

        Parameters self, url
        Returns response
        """

        # Open url and set to response
        response = self._browser.open(url)

        # If the session cookie that we have is expired, we will be redirected to the CAS login page so we check
        # the resulting final url and login if necessary
        while response.geturl().startswith('https://www.uvic.ca/cas/login'):
            # Select the credentials form
            self._browser.select_form(predicate=lambda form:"id" in form.attrs and form.attrs['id'] == "fm1")

            # Enter the credentials
            self._browser.form['username'] = input('Netlink ID: ')
            self._browser.form['password'] = getpass()

            # Login
            response = self._browser.submit()

        # Check for a Semester Selection Form
        for form in self._browser.forms():
            if form.action.endswith('/bwskfshd.P_CrseSchdDetl'):

                # Print Prompt for User
                print("Please select a term: ")

                # Print Term Selection Options
                # Grab the selector
                self._browser.form = form
                selector = self._browser.find_control('term_in')
                # Ignore all (View only) options
                terms = [i for i in selector.items if '(View only)' not in i.get_labels()[0].text]
                # Print term selection options plus option to select
                for i, option in enumerate(reversed(terms)):
                    print("    [{0}] {1}".format(i + 1, option.get_labels()[0].text))

                # Add selected term to term_number
                term_number = None
                while type(term_number) is not int or term_number >= len(terms) or term_number < 0:
                    try:
                        term_number = int(input('Select term: ')) - 1
                    except ValueError:
                        continue

                # Select the corresponding value
                selector.value = [terms[term_number].name]

                # Submit Form
                response = self._browser.submit()
                break

        # Save the browser cookies to a file
        self._browser._ua_handlers['_cookies'].cookiejar.save(COOKIES_FILE, ignore_discard=True, ignore_expires=True)
        
        # Return the response
        return response

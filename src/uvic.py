import os
import cookielib
from getpass import getpass

import mechanize


# TODO: find somewhere better to store cookies
COOKIES_FILE = '.cookies'


class Auth:
    def __init__(self):

        # Create a mechanize browser instance
        self._browser = mechanize.Browser()
        self._browser.set_handle_equiv(True)
        self._browser.set_handle_redirect(True)
        self._browser.set_handle_referer(True)
        self._browser.set_handle_robots(False)
        # noinspection PyProtectedMember,PyUnresolvedReferences
        self._browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
        self._browser.addheaders = [('User-agent', 'Chrome')]

        # Load the CookieJar from the CookieJar file if it exists
        self.cookies = cookielib.LWPCookieJar()

        self._browser.set_cookiejar(self.cookies)

        if os.path.isfile(COOKIES_FILE):
            self.cookies.load(COOKIES_FILE, ignore_discard=True, ignore_expires=True)

    def load(self, url):
        response = self._browser.open(url)

        # If the session cookie that we have is expired, we will be redirected to the CAS login page so we check
        # the resulting final url and login if necessary
        if response.geturl().startswith('https://www.uvic.ca/cas/login'):
            # Select the credentials form
            self._browser.select_form("credentials")

            # Enter the credentials
            self._browser.form['username'] = raw_input('Netlink ID:')
            self._browser.form['password'] = getpass()
            self._browser.form['workstationType'] = ['Private']

            # Login
            response = self._browser.submit()

            # Save the browser cookies to a file
        # noinspection PyProtectedMember
        self._browser._ua_handlers['_cookies'].cookiejar.save(COOKIES_FILE, ignore_discard=True, ignore_expires=True)

        return response
import os
import unittest
from selenium.webdriver.support.wait import WebDriverWait
from splinter import Browser

from run import app


class Auth0LoginTest(unittest.TestCase):
    def test_login(self):
        if os.getenv('TRAVISCI'):
            return  # pragma: no cover
        chrome = Browser('chrome', incognito=True, headless=True)

        with Browser('flask', app=app) as browser:
            # Visit URL
            browser.visit('/')
            # Find and click the 'search' button
            link = browser.find_link_by_partial_href('auth0.com/authorize')
            link = link.first.outer_html.split('"')[1].replace('&amp;', '&')
            chrome.visit(link)

            self.assertIn('wildapps.us', chrome.url)

            WebDriverWait(chrome, 1)
            chrome.fill('username', 'ian+1@iandouglas.com')
            chrome.fill('password', 'UdacityPassword123!')
            buttons = chrome.find_by_name('action')
            buttons.first.click()

            WebDriverWait(chrome, 1)
            local_link = chrome.url
            print('callback url:', chrome.url)
            jwt = chrome.url.split('=')[1].split('&')[0]
            print('jwt:', jwt)

            self.assertIn('localhost:5000/callback#access_token=', chrome.url)
            chrome.quit()

            local_link = local_link.replace('http://localhost:5000', '')
            browser.visit(local_link)

            self.assertIn('Welcome back', browser.html)


'''
click 'Sign up'
fill 'email' with id@w98.us
fill 'password' with password
    Your password must contain:
    At least 8 characters
    At least 3 of the following:
    Lower case letters (a-z)
    Upper case letters (A-Z)
    Numbers (0-9)
    Special characters (ex. !@#)
click button Continue name=action
click button Accept name=action

http://localhost:5000/callback#
access_token=eyJ...&expires_in=86400&token_type=Bearer
'''

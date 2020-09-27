import unittest
from selenium.webdriver.support.wait import WebDriverWait
from splinter import Browser

from run import app

class Auth0LoginTest(unittest.TestCase):
    def test_login(self):
        chrome = Browser('chrome', incognito=True, headless=True)

        with Browser('flask', app=app) as browser:
            # Visit URL
            browser.visit('/')
            # Find and click the 'search' button
            link = browser.find_link_by_partial_href('auth0.com/authorize')
            link = link.first.outer_html.split('"')[1].replace('&amp;', '&')
            chrome.visit(link)

            assert 'wildapps.us' in chrome.url

            WebDriverWait(chrome, 1)
            chrome.fill('username', 'ian+1@iandouglas.com')
            chrome.fill('password', 'UdacityPassword123!')
            buttons = chrome.find_by_name('action')
            buttons.first.click()

            WebDriverWait(chrome, 1)
            local_link = chrome.url
            assert 'Welcome back' in chrome.html
            assert 'localhost:5000/callback#access_token=' in chrome.url

            local_link = local_link.replace('http://localhost:5000', '')
            browser.visit(local_link)

            jwt = chrome.url.split('=')[1].split('&')[0]
            chrome.quit()
            print(jwt)
            assert 'Welcome back' in browser.html

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

http://localhost:5000/callback#access_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Im9ZSjlMWWZ1a0pwT21TNW9EMUMtaCJ9.eyJpc3MiOiJodHRwczovL3dpbGRhcHBzLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZjcwNDdkZWE1MTFmZTAwNmI3OGY4ZjYiLCJhdWQiOiJmc25kLWNhcHN0b25lIiwiaWF0IjoxNjAxMTkzOTYwLCJleHAiOjE2MDEyODAzNjAsImF6cCI6Ijl3VVBkTmNIT3hUWlZPcnFnZWtTeDBMSkNENkJkVlJCIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6W119.H0sJH-9g_MSPAbdIucklYGWCMit_1RNJBtHV8Gsvi8qpn7uHaGirHkKMOP4b6K5b3zhBgNz9hraoFFffn996t-1GOynWUTRMDTio0T4nVJ0Cs68s3XGGyU-Yr_AxFaS6WvftkvRwfwZ1a85wTSvSJdaaMT6Cbns6Yp3DrH62Frba66UjH5wSasIjj_BX5s6qmNeIjOjVjzqoIxWwEJ5CQKUAEcYTov0Ox4tUNx3zRRI8F8MTJH9G2OoSsgWUL_o1bsWED1TmZD8UvSrzDvX_S7ECy3jz6D1ciDEl9FprtZCl2iKizDaWrgAyepjmoIV45ZnpHh1uawIZC9-YR_-3Zg&expires_in=86400&token_type=Bearer
'''

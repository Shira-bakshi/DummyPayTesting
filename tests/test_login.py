

from pages.login_page import LoginPage
from playwright.sync_api import Page, expect

def test_login_page_title(page: Page):

    login_page = LoginPage(page)
    login_page.fillEmail()
    login_page.fillPassword()
    login_page.clickSignInButton()
    

def test_forgot_password(page: Page):
    login_page = LoginPage(page)
    login_page.clickForgotPasswordLink()
    expect(login_page.page).to_have_url("https://dummypay.vercel.app/forgot-password")
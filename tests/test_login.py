

import os

import pytest

from pages.loginPage import LoginPage
from playwright.sync_api import Page, expect

@pytest.mark.smoke
def test_negativeLoginPage(page: Page):
    loginPage = LoginPage(page)
    loginPage.fillEmail(os.getenv("TEST_USER_EMAIL"))
    loginPage.fillPassword("11111111")
    loginPage.clickSignInButton()
    expect(page).to_have_url("https://dummypay.vercel.app/login")
    loginPage.fillEmail("shirab7641")
    loginPage.fillPassword("11111111")
    loginPage.clickSignInButton()
    expect(page).to_have_url("https://dummypay.vercel.app/login")

@pytest.mark.smoke
def test_loginPage(loginPage: LoginPage):
    loginPage.fillEmail()
    loginPage.fillPassword()
    loginPage.clickSignInButton()
    expect(loginPage.page.get_by_role("navigation", name="Main")).to_be_visible()
    
@pytest.mark.regression
@pytest.mark.skip
def test_forgotPassword(page: Page):
    loginPage = LoginPage(page)
    loginPage.clickForgotPasswordLink()
    expect(loginPage.page).to_have_url("https://dummypay.vercel.app/forgot-password")


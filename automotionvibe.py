from typing import List, Any, Union

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
import time
from datetime import date
import datetime
import calendar
import pickle
import pause
from PIL import Image
import sys

# EXAMPLE USE
# ------------------------ #
# CONFIG
# username = 'JoeFantastic123'
# password = 'BadPassword123'
# user_id = 'Joe'

# get_cookie_profile(user_id, username, password)
# cookies = "<PATH-TO-COOKIE-OBJECT>/cookies_" + user_id + ".pkl"

# quick_reg(cookies) <- Automated: sign-up for one appt in your favorites daily
# reg_all(cookies) <- Manually triggered: sign up for all available appts in favorites
# unreg_nearest(cookies) <- Manually triggered: unregisters from nearest appt in your favorites
# ------------------------ #

#       Business logic      #

# Finds the day of week of a given date
def findDay(date_):
    month, day, year = (int(i) for i in date_.split('/'))
    day_number = calendar.weekday(year, month, day)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"]
    return days[day_number]


# Finds the day of the week 3 days ahead of a given date
def findregDay(date_):
    month, day, year = date_.split('/')
    day, year = int(day), int(year)
    months_days = {'01': 31, '02': 28, '03': 31, '04': 30, '05': 31, '06': 30, '07': 31, '08': 31, '09': 30, '10': 31,
                   '11': 30, '12': 31}
    day = day + 3
    if day > months_days[month]:
        day = day - months_days[month]
        month = int(month) + 1
    else:
        month = int(month)
    day_number = calendar.weekday(year, month, day)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"]
    return days[day_number]


# Defines today's date, today's day, and the day to be registered
def today_info():
    today = date.today()
    date_t = today.strftime("%m/%d/%y")
    day_t = findDay(date_t)
    day_r = findregDay(date_t)
    return [date_t, day_t, day_r]


# Displays image or exception message if error
def img_display(image):
    try:
        img = Image.open(image)
        img.show()
    except ImportError:
        print('Error loading image: no file found under that name.\n')
    finally:
        pass
    return


# Adds leading `0` to date string, if applicable
def date_len_check(date_num1, date_num2):
    length1 = len(str(date_num1))
    length2 = len(str(date_num2))
    if length1 == 1:
        new_num1 = '0' + str(date_num1)
    else:
        new_num1 = date_num1
    if length2 == 1:
        new_num2 = '0' + str(date_num2)
    else:
        new_num2 = date_num2
    return new_num1, new_num2


# Defines this week and next week in computer readable form (important for precise implicit waits)
def weeks():
    today = date.today()
    date_t = today.strftime("%Y/%m/%d")
    y, m, d = date_t.split('/')  # Year, month, and day as strings
    y, m, d = int(y), int(m), int(d)
    # y, m, d = 2021, 6, 20 <-- for debugging
    day_w_num = calendar.weekday(y, m, d)  # Finds day of the week of today (0=Mon, 6=Sun)
    # Defines the start date of Sunday and end date Saturday for the current week.
    sun: int
    sat: int
    if day_w_num == 6:
        sun = d
        sat = d + 6
    elif day_w_num == 5:
        sun = d - 6
        sat = d
    elif day_w_num == 4:
        sun = d - 5
        sat = d + 1
    elif day_w_num == 3:
        sun = d - 4
        sat = d + 2
    elif day_w_num == 2:
        sun = d - 3
        sat = d + 3
    elif day_w_num == 1:
        sun = d - 2
        sat = d + 4
    elif day_w_num == 0:
        sun = d - 1
        sat = d + 5
    else:
        raise IndexError

    month_abbrs: List[str] = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_days: List[int] = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if calendar.isleap(y) is True:
        month_days[2] = 29
    else:
        pass

    # Nested if statements handle changing of months, not equipped to change years
    #   (feel free to add to this logic and send a pull request)
    if sat > month_days[m]:
        sat = sat - month_days[m]
        sat, sun = date_len_check(sat, sun)
        this_week = month_abbrs[m].upper() + ' ' + str(sun) + ' - ' + str(sat) + ', ' + str(y)
        sat, sun = int(sat), int(sun)
        n_sun = sun + 7 - month_days[m]
        n_sat = sat + 7
        m = m + 1
        sat, sun = date_len_check(sat, sun)
        next_week = month_abbrs[m].upper() + ' ' + str(n_sun) + ' - ' + str(n_sat) + ', ' + str(y)
    else:
        if sun <= 0:
            m = m - 1
            sun = sun + month_days[m]
            sat, sun = date_len_check(sat, sun)
            this_week = month_abbrs[m].upper() + ' ' + str(sun) + ' - ' + str(sat) + ', ' + str(y)
            sat, sun = int(sat), int(sun)
            n_sun = sun + 7 - month_days[m]
            n_sat = sat + 7
            m = m + 1
            n_sat, n_sun = date_len_check(n_sat, n_sun)
            next_week = month_abbrs[m].upper() + ' ' + str(n_sun) + ' - ' + str(n_sat) + ', ' + str(y)
        else:
            sat, sun = date_len_check(sat, sun)
            this_week = month_abbrs[m].upper() + ' ' + str(sun) + ' - ' + str(sat) + ', ' + str(y)
            sat, sun = int(sat), int(sun)
            n_sun = sun + 7
            n_sat = sat + 7
            if n_sat > month_days[m]:
                n_sat = n_sat - month_days[m]
                n_sat, n_sun = date_len_check(n_sat, n_sun)
                next_week = month_abbrs[m].upper() + ' ' + str(n_sun) + ' - ' + str(n_sat) + ', ' + str(y)
            else:
                n_sat, n_sun = date_len_check(n_sat, n_sun)
                next_week = month_abbrs[m].upper() + ' ' + str(n_sun) + ' - ' + str(n_sat) + ', ' + str(y)

    return this_week, next_week


# Pauses the program until 8:59:59.500 PM
def wait_for_9PM():
    td = datetime.datetime.now()
    date_ls = td.strftime('%m/%d/%Y')
    m, d, y = (int(i) for i in date_ls.split('/'))
    go_time = datetime.datetime(y, m, d, 20, 59, 59, 500000)
    print('\nWaiting until', str(go_time))
    pause.until(go_time)
    return


# Pauses the program until 8:59:00 PM
def wait_for_8_59PM():
    td = datetime.datetime.now()
    date_ls = td.strftime('%m/%d/%Y')
    m, d, y = (int(i) for i in date_ls.split('/'))
    go_time = datetime.datetime(y, m, d, 20, 59, 0, 0)
    print('\nWaiting until', str(go_time))
    pause.until(go_time)
    return


#       Selenium        #

# Helper function: clicks the 'next week' button on the calendar iff the day of the appointment is Sun, Mon, or Tues
def next_week_cond_click(driver, reg_day, this_week, next_week):
    wait = WebDriverWait(driver, 15)
    next_btn = 'phMemberPortalTimeline1_btnNext1'
    week_header = 'phMemberPortalTimeline1_lblHeader'

    if reg_day == 'Sunday':
        n = wait.until(ec.element_to_be_clickable((By.ID, next_btn)))
        n.click()
        wait.until(ec.text_to_be_present_in_element((By.ID, week_header), next_week))

    elif reg_day == 'Monday':
        n = wait.until(ec.element_to_be_clickable((By.ID, next_btn)))
        n.click()
        wait.until(ec.text_to_be_present_in_element((By.ID, week_header), next_week))

    elif reg_day == 'Tuesday':
        n = wait.until(ec.element_to_be_clickable((By.ID, next_btn)))
        n.click()
        wait.until(ec.text_to_be_present_in_element((By.ID, week_header), next_week))

    else:
        wait.until(ec.text_to_be_present_in_element((By.ID, week_header), this_week))

    return


# Helper function: retrieves the cookies from a logged in session and saves as a python object
def get_cookie_profile(user_id, u_name, p_word):
    # Start webdriver instance, get login page
    driver = webdriver.Chrome()
    url = '<MOTION-VIBE-LOGIN-PORTAL>'
    driver.get(url)
    time.sleep(2)
    # Send username and password, then check the 'Remember me' box, and submit
    user = driver.find_element_by_name('txtLogin')
    pw = driver.find_element_by_name('txtPassword')
    time.sleep(0.5)
    user.send_keys(u_name)
    time.sleep(0.5)
    check = driver.find_element_by_id('chkRememberPassword')
    check.click()
    pw.send_keys(p_word)
    time.sleep(0.75)
    pw.send_keys(Keys.RETURN)
    time.sleep(3)
    # Save cookies as python object in project directory
    pickle.dump(driver.get_cookies(), open("cookies_" + user_id + ".pkl", "wb"))
    time.sleep(3)
    driver.close()
    driver.quit()
    return print('Cookie profile created for ' + user_id)


#       Main Function       #
# Loads the page and gets info(~15 sec), then waits until 9PM for registration to open;
# Registers user for one newly available appointment in their favorites
def quick_reg(cookies):
    # Starts webdriver instance, opens MotionVibe website, loads user cookies, then refreshes the page
    chromedriver = '<PATH-TO>/chromedriver'
    options = webdriver.ChromeOptions()
    options.add_argument('headless')  # opt
    options.add_argument('window-size=1200x644')  # opt
    driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=options)  # opt chrome_options=options
    url = '<MOTION-VIBE-LOGIN-PORTAL>'
    driver.get(url)
    cookies = pickle.load(open(cookies, "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()

    # Helpful data/vars
    info = today_info()
    w_info = weeks()
    wait = WebDriverWait(driver, 15)
    dashboard = '//*[@id="divHeader"]/div[1]/div/table/tbody/tr/td[4]/div[1]'

    # Loads user favorites registration page, goes to next week in calendar if appropriate
    acct_a = wait.until(
        ec.element_to_be_clickable((By.XPATH, dashboard)))
    acct_a.click()
    next_week_cond_click(driver, info[2], w_info[0], w_info[1])

    # Learns how many registration buttons exist before 9 PM so it knows not to click them
    try:
        st_opts = WebDriverWait(driver, 2).until(ec.visibility_of_any_elements_located((By.LINK_TEXT, 'REGISTER')))
        st_num = len(st_opts)
    except TimeoutException:
        st_num = 0
    finally:
        acct_b = wait.until(
            ec.element_to_be_clickable((By.XPATH, dashboard)))
        wait_for_9PM()  # Pauses the function until 8:59:59.5000
        acct_b.click()  # Loads user favorites registration page

    # This loop checks for a new appointment 17 times over about 30sec;
    # If one is found, the loop breaks, otherwise the program quits after 17 attempts
    effort = False
    counter = 0
    while effort is False:
        try:
            next_week_cond_click(driver, info[2], w_info[0], w_info[1])  # Goes to next week in calendar if appropriate
            counter = counter + 1
            # Search for register button
            if counter <= 4:
                WebDriverWait(driver, 0.1).until(ec.element_to_be_clickable((By.LINK_TEXT, 'REGISTER')))
            elif 4 < counter <= 7:
                WebDriverWait(driver, 1).until(ec.element_to_be_clickable((By.LINK_TEXT, 'REGISTER')))
            elif 7 < counter <= 12:
                WebDriverWait(driver, 2.5).until(ec.element_to_be_clickable((By.LINK_TEXT, 'REGISTER')))
            else:
                WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.LINK_TEXT, 'REGISTER')))
            button_cond = True
        except TimeoutException:  # if there are no register buttons, refresh the page
            refresh = wait.until(
                ec.element_to_be_clickable((By.XPATH, dashboard)))
            refresh.click()
            button_cond = False
            if counter > 17:  # After the 17th refresh, the program quits
                driver.close()
                driver.quit()
                sys.exit('\nRegistration NOT successful.\n')
            else:
                pass
        finally:
            if button_cond is True:  # When a register button is found, the program checks if it is new as of 9PM
                reg_num = driver.find_elements_by_link_text('REGISTER')
                if st_num == len(
                        reg_num):  # If it was a pre-existing button, refresh the page, and pause proportionally to
                                   # the implicit waits above
                    refresh = wait.until(
                        ec.element_to_be_clickable(
                            (By.XPATH, dashboard)))
                    refresh.click()
                    if counter <= 4:
                        time.sleep(0.2)
                    elif 4 < counter <= 7:
                        time.sleep(1)
                    elif 7 < counter <= 12:
                        time.sleep(2.5)
                    elif 12 < counter <= 17:
                        time.sleep(5)
                    else:  # After the 17th refresh, the program quits
                        driver.close()
                        driver.quit()
                        sys.exit('\nRegistration NOT successful.\n')
                else:
                    effort = True
            else:
                pass

    # If the program finds a new registration button, the while loop is broken. Then ->
    reg_opts = driver.find_elements_by_link_text('REGISTER')
    reg_opts[-1].click()  # Click the last visible register button
    ok = wait.until(ec.element_to_be_clickable((By.CLASS_NAME, 'blueButtonDiv')))
    time.sleep(0.2)
    ok.click()  # Confirm registration on website

    n_tuple = time.localtime()  # get struct_time
    time_string = str(time.strftime("%H:%M:%S", n_tuple))  # Timestamp of registration

    # Refreshes the pages and takes a screenshot of the results, then displays it in default viewer
    refresh = wait.until(
        ec.element_to_be_clickable((By.XPATH, dashboard)))
    time.sleep(0.75)
    refresh.click()
    time.sleep(1)
    next_week_cond_click(driver, info[2], w_info[0], w_info[1])
    time.sleep(1)
    driver.save_screenshot(
        '<PATH-TO-LOCAL-STORAGE>/Sign_up_SS_' + info[0].replace('/', '-') + '.png')
    driver.close()
    driver.quit()
    img_display('<PATH-TO-LOCAL-STORAGE>/Sign_up_SS_' + info[0].replace('/', '-') + '.png')

    return print('\nSuccess! Registration complete at ' + time_string + '\n')


# Service function: unregisters from nearest upcoming appointment in favorites
def unreg_nearest(cookies):
    # Starts webdriver instance, opens MotionVibe website, loads user cookies, then refreshes the page
    driver = webdriver.Chrome()
    url = '<MOTION-VIBE-LOGIN-PORTAL>'
    driver.get(url)
    cookies = pickle.load(open(cookies, "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()

    # Helpful data/vars
    wait = WebDriverWait(driver, 15)
    info = today_info()
    w_info = weeks()
    header = '//*[@id="divHeader"]/div[1]/div/table/tbody/tr/td[4]/div[1]'

    # Loads user favorites registration page, goes to next week in calednar if appropriate
    acct_a = wait.until(
        ec.element_to_be_clickable((By.XPATH, header)))
    acct_a.click()

    # Unregisters from nearest registered appt
    try:
        wait.until(ec.element_to_be_clickable((By.LINK_TEXT, 'UNREGISTER')))
    except TimeoutException:
        driver.close()
        driver.quit()
        sys.exit('\nNo appointments available to unregister from.\n')
    finally:
        unreg_l = driver.find_elements_by_link_text('UNREGISTER')
        unreg_l[0].click()
        ok = wait.until(ec.element_to_be_clickable((By.CLASS_NAME, 'blueButtonDiv')))
        time.sleep(0.25)
        ok.click()

    # Refreshes the pages and takes a screenshot of the results, then displays it in default viewer
    refresh = wait.until(
        ec.element_to_be_clickable((By.XPATH, header)))
    time.sleep(0.75)
    refresh.click()
    time.sleep(1)
    driver.save_screenshot(
        '<PATH-TO-LOCAL-STORAGE>/Unreg_success_SS_' + info[0].replace('/', '-') + '.png')
    driver.close()
    driver.quit()
    img_display(
        '<PATH-TO-LOCAL-STORAGE>/motionvibe/Unreg_success_SS_' + info[0].replace('/', '-') + '.png')

    return print('\nSuccess! Unregistered from nearest appointment.\n')


# Service function: registers user for all available appointments in their favorites upon demand (not at 9PM)
def reg_all(cookies):
    # Starts webdriver instance, opens MotionVibe website, loads user cookies, then refreshes the page
    driver = webdriver.Chrome()
    url = '<MOTION-VIBE-LOGIN-PORTAL>'
    driver.get(url)
    cookies = pickle.load(open(cookies, "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()

    # Helpful data/vars
    wait = WebDriverWait(driver, 15)
    info = today_info()
    w_info = weeks()
    header = '//*[@id="divHeader"]/div[1]/div/table/tbody/tr/td[4]/div[1]'

    # Loads user favorites registration page, goes to next week in calednar if appropriate
    acct_a = wait.until(
        ec.element_to_be_clickable((By.XPATH, header)))
    acct_a.click()
    next_week_cond_click(driver, info[2], w_info[0], w_info[1])

    # Checks how many register buttons there are to begin, then refreshes the page. If none the program quits
    try:
        WebDriverWait(driver, 7).until(ec.element_to_be_clickable((By.LINK_TEXT, 'REGISTER')))
        st_opts = driver.find_elements_by_link_text('REGISTER')
        st_num = len(st_opts)
    except TimeoutException:
        driver.close()
        driver.quit()
        sys.exit('\nNo appointments available for registration.\n')
    finally:
        acct_b = wait.until(
            ec.element_to_be_clickable((By.XPATH, header)))
        acct_b.click()
        next_week_cond_click(driver, info[2], w_info[0], w_info[1])

    # Clicks all known register buttons, and confirms each on website;
    # The logic in the finally statement avoids stale element exceptions
    try:
        wait.until(ec.element_to_be_clickable((By.LINK_TEXT, 'REGISTER')))
    except TimeoutException:
        driver.close()
        driver.quit()
        sys.exit('\nNo appointments available for registration.\n')
    finally:
        reg_l = driver.find_elements_by_link_text('REGISTER')
        count = 0
        for r in range(len(reg_l)):
            try:
                wait.until(ec.element_to_be_clickable((By.LINK_TEXT, 'REGISTER')))
                reg_l2 = driver.find_elements_by_link_text('REGISTER')
                if len(reg_l2) == st_num:
                    pass
                else:
                    count = count + 1
                    r = r - count
                reg_l2[r].click()
                ok = wait.until(ec.element_to_be_clickable((By.CLASS_NAME, 'blueButtonDiv')))
                time.sleep(0.25)
                ok.click()
            except StaleElementReferenceException:
                pass
            finally:
                pass

    # Refreshes the pages and takes a screenshot of the results, then displays it in default viewer
    refresh = wait.until(
        ec.element_to_be_clickable((By.XPATH, header)))
    time.sleep(0.75)
    refresh.click()
    time.sleep(1)
    next_week_cond_click(driver, info[2], w_info[0], w_info[1])
    time.sleep(1)
    driver.save_screenshot(
        '<PATH-TO-LOCAL-STORAGE>/Reg_all_success_SS_' + info[0].replace('/', '-') + '.png')
    driver.close()
    driver.quit()
    img_display(
        '<PATH-TO-LOCAL-STORAGE>/Reg_all_success_SS_' + info[0].replace('/', '-') + '.png')

    return print('\nSuccess! Registered for all available appointments.\n')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import pyotp
from datetime import datetime
import random
from logging_extension import get_logger

logger = get_logger(__name__)


class AutoAttendance():
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://accounts.zoho.com/signin?servicename=Peopleplus&signupurl=https://www.zoho.com/peopleplus/signup.html")
        self.username = ""
        self.password = ""
        self.totp = ""

    def _login(self):
        username = self.driver.find_element(By.ID, "login_id")
        username.send_keys(self.username)
        next_button = self.driver.find_element(By.ID, "nextbtn")
        next_button.click()
        # input password
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.ID, "password"))).send_keys(self.password)
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "nextbtn"))).click()

        # input otp if enabled
        if len(self.totp) > 0:
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.ID, "mfa_totp"))).send_keys(pyotp.TOTP(self.totp).now())
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "nextbtn"))).click()

        # not trust browser
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.grey.trustdevice.notnowbtn"))).click()
        logger.info("Login successfully")

    def _logout(self):
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "zpeople_userimage"))).click()
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "ZPSOut"))).click()
        logger.info("Logout successfully")
        time.sleep(5)
        
    def attendance(self):
        self._login()
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "zp_maintab_attendance"))).click()
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "ZPAtt_check_in_out")))
        time.sleep(5)
        attendance = self.driver.find_element(By.ID, "ZPAtt_check_in_out")
        title = attendance.find_element(By.CLASS_NAME, "type-btn").get_attribute("title")
        logger.info(title)

        if title == "Check-in":
            # time.sleep(random(1, 2) * 60)
            logger.info("Proceed to check-in")
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "ZPAtt_check_in_out"))).click()
            logger.info("Check-in completed")
        
        if title == "Check-out":
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "today-active")))
            today_row = self.driver.find_element(By.CLASS_NAME, "today-active")
            current_duration = datetime.strptime(today_row.find_element(By.CSS_SELECTOR, ".AtPcol.ZPbold").text, "%H:%M:%S Hrs")
            logger.info(f"Current duration: {current_duration.time()}")
            if current_duration.hour < 8:
                remain_duration = datetime.strptime("08:00:00", "%H:%M:%S") - current_duration
                logger.info(f"Remaining time: {remain_duration}")
                rand = remain_duration.seconds + random(1, 2) * 60
                logger.info(f"Waiting {rand} seconds")
                time.sleep(rand)
                WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "ZPAtt_check_in_out"))).click()
            else:
                WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "ZPAtt_check_in_out"))).click()
            logger.info("Check-out successfully")
        time.sleep(10)

        self._logout()
        self.driver.close()
        self.driver.quit()

if __name__ == "__main__":
    auto_attendance = AutoAttendance()
    auto_attendance.attendance()
    # auto_attendance._login()
    # auto_attendance._logout()

    
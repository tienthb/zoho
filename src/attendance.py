from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time
import pyotp
from datetime import datetime, timedelta
import random
from extensions.logging_extension import get_logger
from extensions.dynaconf_extension import settings
import pandas as pd


logger = get_logger(__name__)


class AutoAttendance:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("headless")
        self.driver = webdriver.Chrome(options=self.options)
        # self.driver = webdriver.Chrome()
        self.driver.get("https://accounts.zoho.com/signin?servicename=Peopleplus&signupurl=https://www.zoho.com/peopleplus/signup.html")
        self.username = settings.ZOHO_USERNAME
        self.password = settings.ZOHO_PASSWORD
        self.totp = settings.ZOHO_TOTP
        self.today = datetime.utcnow() + timedelta(hours=7)
        self.today_str = self.today.strftime("%a, %d/%m/%Y")

    def _login(self):
        # input username
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.ID, "login_id"))).send_keys(self.username)
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "nextbtn"))).click()
        # input password
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.ID, "password"))).send_keys(self.password)
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "nextbtn"))).click()

        # input otp if enabled
        if len(self.totp) > 0:
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.ID, "mfa_totp"))).send_keys(pyotp.TOTP(self.totp).now())
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "nextbtn"))).click()

        # not trust browser
        try:
            logger.info("Skip trusted browser")
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.grey.trustdevice.notnowbtn"))).click()
        except TimeoutException:
            pass

        try:
            logger.info("Skip install zoho one")
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "secoundary_btn"))).click()
        except TimeoutException:
            pass
        time.sleep(10)
        logger.info("Login successfully")

    def _logout(self):
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "zpeople_userimage"))).click()
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "ZPSOut"))).click()
        logger.info("Logout successfully")
        time.sleep(5)

    def _is_day_off(self, today_status):
        off = ("Leave", "Holiday")
        if today_status["Status"].item().endswith(off):
            return True
        return False

    def _parse_attendance_table(self):
        today_status = None
        attempt = 0
        driver = self.driver
        while attempt < 3:
            logger.info("Attempt %s" % attempt)
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "zp_maintab_attendance")))
                driver.find_element(By.ID, "zp_maintab_attendance").click()
                logger.info("Click Attendance tab")
                
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "zp_t_attendance_entry_tabularview")))
                driver.find_element(By.ID, "zp_t_attendance_entry_tabularview").click()
                logger.info("Click Tabular View tab")
                # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "zp_t_attendance_entry_tabularview"))).click()
                
                WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "ZPAtt_tabView")))
                attendance_table = driver.find_element(By.ID, "ZPAtt_tabView")
                logger.info("Located attendance table")

                # WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.TAG_NAME, "tr")))
                rows = attendance_table.find_elements(By.TAG_NAME, "tr")
                logger.info("Parse to dataframe")
                cells = []
                for row in rows:
                    cells.append(row.find_elements(By.TAG_NAME, "td"))

                headers = attendance_table.find_elements(By.TAG_NAME, "th")
                header = []
                for h in headers:
                    if h.text != "":
                        header.append(h.text)

                df = []
                for cell in cells:
                    if len(cell) > 0:
                        df.append([c.text for c in cell])  
                df = pd.DataFrame(df)
                df = df.drop([8, 9], axis=1)
                df.columns = header
                df.to_csv(f"/home/tientran/dev/status_{attempt}.csv", index=False)
                # logger.info(len(df))
                today_status = df.loc[df["Date"] == self.today_str]
                today_status.to_csv(f"/home/tientran/dev/today_status_{attempt}.csv", index=False)
                if len(today_status) > 0:
                    break
                else:
                    attempt += 1
                    pass
            except TimeoutException as e:
                logger.info("Timeout Error", e)
                attempt += 1
                time.sleep(5)
            except KeyError as e:
                logger.info("Empty dataframe")
                attempt += 1
                time.sleep(5)

        if attempt == 3 and today_status is None:
            raise ValueError("Failed to parse attendance table")
        else:
            logger.info("Attendance table parsed successfully")
            logger.info(today_status)
        return today_status

    def attendance(self):
        self._login()
        today_status = self._parse_attendance_table()
        is_day_off = self._is_day_off(today_status)

        if is_day_off:
            logger.info("Skip as today is off")
        else:
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "zp_t_attendance_entry_listview"))).click()
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "ZPAtt_check_in_out")))
            time.sleep(5)
            attendance = self.driver.find_element(By.ID, "ZPAtt_check_in_out")
            title = attendance.find_element(By.CLASS_NAME, "type-btn").get_attribute("title")

            if title == "Check-in":
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
                    rand = remain_duration.seconds + random.randint(1, 2) * 60
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
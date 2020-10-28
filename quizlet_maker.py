# Docs: https://selenium-python.readthedocs.io/

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException as TE

SOURCE_PATH = 
TARGET_URL = 

class QuizletMaker:
    def __init__(self, source, target):
        self.driver = webdriver.Safari()
        self.source = source
        self.target = target

    def find_element(self, method, argument, time_wait):
        try:
            element = WebDriverWait(self.driver, time_wait).until(
                EC.presence_of_element_located((method, argument))
            )
            return element
        except TE:
            print("Element not found: TimeOut Exception")
            self.driver.quit()
            exit()

    def find_element_by_xpath(self, xpath, time_wait=10):
        return self.find_element(By.XPATH, xpath, time_wait)
    
    def find_element_by_name(self, name, time_wait=10):
        return self.find_element(By.NAME, name, time_wait)
    
    def find_element_by_class(self, class_name, time_wait=10):
        return self.find_element(By.CLASS_NAME, class_name, time_wait)
    
    def find_element_by_id(self, id, time_wait=10):
        return self.find_element(By.ID, id, time_wait)

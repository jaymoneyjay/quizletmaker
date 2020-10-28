# Docs: https://selenium-python.readthedocs.io/

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException as TE

import os, argparse, time, re

class Scraper:
    def __init__(self, url):
        self.driver = webdriver.Safari()
        self.url = url
        self.driver.get(self.url)

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


#TODO: class QuizletMaker:

SEARCH_BAR_ID = "searchword"
SEARCH_BAR_XPATH = '//*[@id="searchword"]'
PART_OF_SPEACH_XPATH = '//*[@id="page-content"]/div[2]/div[1]/div[2]/div/div[3]/div/div/div[1]/div[2]/div[2]/span[1]'
ENGLISH_BUTTON_XPATH = '/html/body/div[3]/div[1]/div[2]/div/div/div[2]/form/div[2]/div/div/div/span[3]/span'
DEFINITION_XPATH = '//*[@id="page-content"]/div[2]/div[1]/div[2]/div/div[3]/div/div/div/div[3]/div[1]/div[2]/div[1]/div[2]/div'
EXAMPLE_XPATH = '//*[@id="page-content"]/div[2]/div[1]/div[2]/div/div[3]/div/div/div/div[3]/div[1]/div[2]/div[1]/div[3]/div[1]/span'

class DictionaryScraper:
    def __init__(self, data):
        self.filter = ["(n)", "(vb)", "(adj)", "(adv)", "(ppsn)", "AVL", "families"]
        self.data = data

    def _represents_integer(self, character):
        try:
            int(character)
            return True
        except ValueError:
            return False
    
    def _filter_data(self, data_list):
        word_list = [word for word in data_list if not (word in self.filter or self._represents_integer(word[0]))]
        return word_list

    def _read_data(self):
        #TODO: adjust newline
        with open(self.data) as f:
            data_string = f.read()
            data_list = re.split(r" |\n", data_string)
            word_list = self._filter_data(data_list)
            self.word_list = word_list

    def _show_words(self):
        for word in self.word_list:
            print(word)

    def _query_word(self, word):
        search_bar = self.scraper.find_element_by_id(SEARCH_BAR_ID)
        search_bar.send_keys(word)
        search_bar.send_keys(Keys.ENTER)

        part_of_speech = self.scraper.find_element_by_xpath(PART_OF_SPEACH_XPATH).text
        definition = self.scraper.find_element_by_xpath(DEFINITION_XPATH).text
        example = self.scraper.find_element_by_xpath(EXAMPLE_XPATH).text

        time.sleep(3)
        self._reload()
        return (part_of_speech, definition, example)

    def _reload(self):
        self.scraper.driver.get(self.scraper.url)

    def scrape_url(self, dictionary_url):
        self.scraper = Scraper(dictionary_url)
        self._read_data()
        english_button = self.scraper.find_element_by_xpath(ENGLISH_BUTTON_XPATH)
        english_button.click()
        for word in self.word_list:
            pos, definition, example = self._query_word(word)
            print(pos, definition, example, word)

        
        time.sleep(10)


def main(args):
    scraper = DictionaryScraper(args.wordlist)
    scraper.scrape_url(args.dictionary_url)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("wordlist")
    parser.add_argument("dictionary_url")
    parser.add_argument("quizlet_url")

    args = parser.parse_args()
    main(args)
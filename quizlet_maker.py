# Docs: https://selenium-python.readthedocs.io/

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException as TE

import os, argparse, time, re, json

class Scraper:
    def __init__(self, url):
        self.driver = webdriver.Safari()
        self.url = url
        self.driver.execute_script("document.body.style.zoom='100%'")
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


SEARCH_BAR_ID = "searchword"
SEARCH_BAR_XPATH = '//*[@id="searchword"]'
PART_OF_SPEACH_XPATH = '//*[@id="page-content"]/div[2]/div[1]/div[2]/div/div[3]/div/div/div[1]/div[2]/div[2]/span[1]'
ENGLISH_BUTTON_XPATH = '/html/body/div[3]/div[1]/div[2]/div/div/div[2]/form/div[2]/div/div/div/span[3]/span'
DEFINITION_XPATH = '//*[@id="page-content"]/div[2]/div[1]/div[2]/div/div[3]/div/div/div/div[3]/div[1]/div[2]/div[1]/div[2]/div'
EXAMPLE_XPATH = '//*[@id="page-content"]/div[2]/div[1]/div[2]/div/div[3]/div/div/div/div[3]/div[1]/div[2]/div[1]/div[3]/div[1]/span'

JSON_PATH = "card_list.json"

class DictionaryScraper:
    def __init__(self, source, target):
        self.filter = ["","(n)", "(vb)", "(adj)", "(adv)", "(ppsn)", "(advb)", "AVL", "families", "i.e."]
        self.source_path = source
        self.target_path = target
        self.card_list = {}

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
        with open(self.source_path) as f:
            data_string = f.read()
            data_list = re.split(r" |\n", data_string)
            word_list = self._filter_data(data_list)
            return word_list

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
        word_list = self._read_data()
        english_button = self.scraper.find_element_by_xpath(ENGLISH_BUTTON_XPATH)
        english_button.click()
        for word in word_list:
            pos, definition, example = self._query_word(word)
            value = {
                "example": example,
                "definition": definition,
                "pos": pos
                }
            
            print(pos, definition, example, word)
            self.save_to_json(word, value)

    def save_to_json(self, key, value):
        with open(self.target_path, "r") as f:
            content = json.load(f)
        with open(self.target_path, "w") as f:
            content[key] = value
            json.dump(content, f)

LOGIN_XPATH = '//*[@id="SiteHeaderReactTarget"]/header/div[1]/div/div[2]/span[2]/div/div[3]/div/button[1]/span/span'
#GOOGLE_LOGIN_XPATH = '/html/body/div[7]/div/div[2]/div[1]/div[1]/div/a'
INPUT_USERNAME_ID = 'username'
INPUT_PASSWORD_ID = 'password'
INPUT_USERNAME_XPATH = '//*[@id="username"]'
INPUT_PASSWORD_XPATH = '//*[@id="password"]'
USERNAME_PLAIN = "jodok_vieli"
PASSWORD_PLAIN = "Elefant13"

QUIZLET_XPATH = '//*[@id="DashboardPageTarget"]/div/section[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div/div/div/div[2]/a'
EDIT_XPATH = '//*[@aria-label="edit"]/..'
ADD_XPATH = '//*[@id="addRow"]/span/button'
TERM_0_XPATH = '//*[@id="SetPageTarget"]/div/div[2]/div[2]/div/div[1]/div/div[1]/div[1]/div/div[3]/div[1]/div[2]/div/div/div[1]/div/div/div[1]/div/p'



class QuizletMaker:
    def __init__(self, source):
        with open(source) as f:
            self.card_list = json.load(f)

    def _add_card(self, word, example, definition, pos):
        add = self.scraper.find_element_by_xpath(ADD_XPATH)
        add.send_keys(Keys.RETURN)
        
        # Prepare front
        word_upper = word[:1].upper() + word[1:]
        word_lower = word[:1].lower() + word[1:]
        example  = example.replace(word_upper, "[" + pos + "]")
        example  = example.replace(word_lower, "[" + pos + "]").strip(":")
        definition = "[" + pos + "] = " + definition

        front = self.scraper.driver.switch_to_active_element()
        print(front.get_attribute("innerHTML"))
        front.send_keys(example)
        front.send_keys(Keys.RETURN)
        front.send_keys(Keys.RETURN)
        front.send_keys(definition)
        front.send_keys(Keys.TAB)

        back = self.scraper.driver.switch_to_active_element()
        back.send_keys(word)

    def make(self, url):
        self.scraper = Scraper(url)

        login = self.scraper.find_element_by_xpath(LOGIN_XPATH)
        login.click()
        #google_login = self.scraper.find_element_by_xpath(GOOGLE_LOGIN_XPATH)
        #google_login.click()

        input_username = self.scraper.find_element_by_xpath(INPUT_USERNAME_XPATH)
        input_username.send_keys(USERNAME_PLAIN)
        #input_username.send_keys(Keys.RETURN)

        input_password = self.scraper.find_element_by_id(INPUT_PASSWORD_ID)
        input_password.send_keys(PASSWORD_PLAIN)
        input_password.send_keys(Keys.RETURN)

        quizlet = self.scraper.find_element_by_xpath(QUIZLET_XPATH)
        quizlet.click()

        edit = self.scraper.find_element_by_xpath(EDIT_XPATH)
        edit.click()

        for key in self.card_list:
            self._add_card(key, self.card_list[key]["example"], self.card_list[key]["definition"], self.card_list[key]["pos"])


        time.sleep(10)





def main(args):
    wordlist = "input_words.txt"
    dictionary_url = "https://dictionary.cambridge.org/de/"
    quizlet_url = "https://quizlet.com/"
    #dict_scraper = DictionaryScraper(wordlist, JSON_PATH)
    #dict_scraper.scrape_url(dictionary_url)

    quiz_maker = QuizletMaker(JSON_PATH)
    quiz_maker.make(quizlet_url)






if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #parser.add_argument("wordlist")
    #parser.add_argument("dictionary_url")
    #parser.add_argument("quizlet_url")

    args = parser.parse_args()
    main(args)
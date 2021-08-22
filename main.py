import re
import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import patterns

chrome_options = Options()
# chrome_options.add_argument("--disable-extensions")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox") # linux only
chrome_options.add_argument("--headless")

URLS = ["https://travis-ci.org/", "https://app.travis-ci.com/"]
GIT_SOURCES = ["github", "gitlab"]

verbose = True

driver = webdriver.Chrome("./chromedriver", options=chrome_options)
repos = []
repos_name = []
repo_urls = []
config_urls = []
config_data = {}


def fetch_repos(org):
    iterations = 1
    current_iter = 1
    while(current_iter <= iterations):
        for url in URLS:
            for git in GIT_SOURCES:
                if iterations > 1 and current_iter != 1:
                    #?page=6
                    driver.get(url + git + "/" + org + "?page=" + str(current_iter))
                else:
                    driver.get(url + git + "/" + org)
                time.sleep(2)
                elem = driver.find_elements_by_tag_name("a")
                for el in elem:
                    if el.get_attribute("class") == "ember-view label-align":
                        if verbose:
                            print("[%s REPO] %s" % (git.upper(), el.text))
                        repos.append(el)
                        repos_name.append(el.text)
                for repo in repos:
                    repo_urls.append(repo.get_attribute("href"))
                repos.clear()
                elem.clear()
                elem = driver.find_elements_by_class_name("pagination-link ")
                if len(elem) > 0:
                    iterations = int(elem[len(elem) - 1].text)
                # if el.get_attribute("class") == "pagination-link ":
                #     print(el.parent)
        current_iter += 1
    #driver.close()


def fetch_config_urls():
    for url in repo_urls:
        driver.get(url)
        time.sleep(1)
        elem = driver.find_elements_by_tag_name("a")
        for el in elem:
            try:
                if el.get_attribute("title") == "Look at this build's config":
                    if verbose:
                        print(el.get_attribute("href"))
                    config_urls.append(el.get_attribute("href"))
                if el.get_attribute("title") == "Look at this job's config":
                    if verbose:
                        print(el.get_attribute("href"))
                    config_urls.append(el.get_attribute("href"))
            except Exception as ex:
                pass
    #driver.close()


def fetch_travis_ci_config():
    for url in config_urls:
        driver.get(url)
        time.sleep(2)
        elem = driver.find_elements_by_tag_name("code")
        data = ""
        for el in elem:
            data += el.text
        config_data[url] = data


if __name__ == '__main__':

    # with open("token_samples.txt") as file:
    #     for data in file.readlines():


    fetch_repos('att')
    fetch_config_urls()
    fetch_travis_ci_config()
    for k in config_data:
        for data in config_data[k].split("\n"):
            for pattern in patterns.patterns:
                match = re.search(patterns.patterns[pattern], data)
                if (match):
                    print("[%s] %s" % (pattern, match.string))

#TODO: search for a key inside repo and build history
#TODO: SEARCH FOR BUILD JOBS (JOB LOG) https://api.travis-ci.org/v3/job/774292592/log.txt
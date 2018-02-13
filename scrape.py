import csv
import os
import shutil
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions 
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException

# set up directories for file downloads
dir_path = os.path.dirname(os.path.realpath(__file__))
cases_dir = os.path.join(dir_path, "cases")
if not os.path.exists(cases_dir):
    os.makedirs(cases_dir)
download_dir = os.path.join(dir_path, "downloads")
if not os.path.exists(download_dir):
    os.makedirs(download_dir)


class Scraper(object):
    def __init__(self):
        self.f = open(os.path.join(cases_dir, "cases.csv"), 'w')
        self.writer = csv.writer(self.f)
        # headers
        self.writer.writerow(['GeneralOffenseNumber', 'CaseNumber', 'CaseType', 'CaseStatus', 'EndDate', 'FilingDate', 'TotalObligationDue', 'DateOfBirth', 'DefendantName', 'DefenseAttorney'])

        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "profile.default_content_setting_values.automatic_downloads": 1,
        })
        self.driver = webdriver.Chrome(executable_path='./chromedriver', options=options)
        self.driver.get("https://web6.seattle.gov/courts/ECFPortal/default.aspx")

    def close(self):
        self.driver.close()
        self.writer = None
        self.f.close()

    def _search_case(self, go_num, link, type):
        link = self.driver.find_element_by_link_text(link)
        link.click()

        caseNumText = WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable((By.ID, "ContentPlaceHolder1_{}1_CaseSearch1_txtCaseNumber".format(type))))
        caseNumText.click()
        caseNumText.send_keys(go_num)
        search = self.driver.find_element_by_id("ContentPlaceHolder1_{}1_CaseSearch1_btnSearch".format(type))
        search.click()
        try:
            WebDriverWait(self.driver, 2).until(
                    expected_conditions.visibility_of_element_located((By.ID, "ContentPlaceHolder1_{}1_CaseSearch1_RadAjaxLoadingPanel1".format(type))))
        except TimeoutException:
            pass
        WebDriverWait(self.driver, 30).until(
                expected_conditions.invisibility_of_element_located((By.ID, "ContentPlaceHolder1_{}1_CaseSearch1_RadAjaxLoadingPanel1".format(type))))


    def find_case(self, go_num):
        self.find_case_docs(go_num)
        self.find_case_info(go_num)

    def find_case_info(self, go_num):
        self._search_case(go_num, "Case Information", "CaseInfo")

        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_CaseInfo1_rpbCaseInfo_i0_HeaderTemplate_lblCaseDetails")))
        
        fields = [
            "ctl00_ContentPlaceHolder1_CaseInfo1_rpbCaseInfo_i0_CaseDetails1_lblCaseNumber",
            "ctl00_ContentPlaceHolder1_CaseInfo1_rpbCaseInfo_i0_CaseDetails1_lblCaseType",
            "ctl00_ContentPlaceHolder1_CaseInfo1_rpbCaseInfo_i0_CaseDetails1_lblCaseStatus",
            "ctl00_ContentPlaceHolder1_CaseInfo1_rpbCaseInfo_i0_CaseDetails1_lblEndDate",
            "ctl00_ContentPlaceHolder1_CaseInfo1_rpbCaseInfo_i0_CaseDetails1_lblFilingDate",
            "ctl00_ContentPlaceHolder1_CaseInfo1_rpbCaseInfo_i0_CaseDetails1_lblTotalDue",
            "ctl00_ContentPlaceHolder1_CaseInfo1_rpbCaseInfo_i0_CaseDetails1_lblBirthDate",
            "ctl00_ContentPlaceHolder1_CaseInfo1_rpbCaseInfo_i0_CaseDetails1_lblDefendantName",
            "ctl00_ContentPlaceHolder1_CaseInfo1_rpbCaseInfo_i0_CaseDetails1_lbDefenseAttorney",
        ]
        row = [go_num]
        for f in fields:
            row.append(self.driver.find_element_by_id(f).text)
        self.writer.writerow(row)

    def find_case_docs(self, go_num):
        self._search_case(go_num, "Case Documents", "CaseDocuments")

        try:
            t = WebDriverWait(self.driver, 10).until(
                expected_conditions.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_CaseDocuments1_CaseDocumentListAll_rgDocuments_ctl00")))
        except NoSuchElementException:
            return

        trs = WebDriverWait(t, 10).until(
                expected_conditions.visibility_of_all_elements_located((By.XPATH, './/tbody/tr')))
        rows = [x.get_attribute('id') for x in trs if x.get_attribute('class') != "rgNoRecords"]

        for id in rows:
            row = self.driver.find_element_by_id(id)
            columns = row.find_elements_by_xpath(".//td")
            image = columns[0].find_element_by_xpath('.//input[@type="image"]')
            docName = columns[1].text
            image.click()
            print 'downloading ', docName
            doc_path = os.path.join(download_dir, "Document.pdf")
            while not os.path.exists(doc_path):
                time.sleep(0.25)
            os.rename(doc_path, os.path.join(download_dir, docName.replace(' ', '_')+".pdf"))
            print 'downloaded', docName

        if len(rows):
            case_dir = os.path.join(cases_dir, go_num)
            shutil.move(download_dir, case_dir) 
            os.makedirs(download_dir)

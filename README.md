# eMed Selenium Web Scraper

### Setup
+ Download required packages
+ Create a directory to a data folder where all the downloads will go
+ Fill out info in config.ini
+ Run run_niu.py

### Example code block for pulling of specific cpt codes
```python
# Must import CPTs_Report_Page
# from cpt_report import CPTs_Report_Page
def test_cpt(self):
    path = os.path.dirname(os.path.abspath(__file__))
    config = ConfigParser()
    config.read(f"{path}\\config.ini")
    userinfo = config["USERINFO"]
    
    driver = self.driver
    wait = self.wait

    login = LoginPage(driver, wait)
    report = CPTs_Report_Page(driver, wait)

    driver.get("https://service.emedpractice.com/index.aspx")
    login.enter_username(userinfo["loginid"])
    login.enter_password(userinfo["password"])
    login.click_login()

    report.nav_reports()
    report.load_report(report.href)
    report.enter_cpt_code(YOUR_CPT_CODES) # ie: "99214,99123"
    report.set_date_month(report.table_id, "01-01-2022", "07-31-2022")
    report.merge(report.mydir+"merged.csv")
```        

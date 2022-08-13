# Detainee Data Web Scraper

+ Download required packages
+ Create a directory to a data folder where all the downloads will go
+ Change self.mydir in classes.py to the data folder
+ Change self.subdir in xlsx_writer_niu.py to the data folder
+ Add login info in run_niu.py
+ Change dates to specified date in run_niu.py
+ Run run_niu.py

### Example code block for generation of daily .XLSX workbook
```python
driver = self.driver
wait = self.wait

login = LoginPage(driver, wait)
report = ReportPage(driver, wait)
niu = NIU(driver, wait)
dates = ["08-11-2022","08-12-2022"]

driver.get("https://service.emedpractice.com/index.aspx")
login.enter_username("YOUR_USERNAME")
login.enter_password("YOUR_PASSWORD")
login.click_login()

report.nav_reports()
for date in dates:
    report.load_report("AppointmentReportv1")
    niu.stage_apt(date, date)
    apt = niu.scrape_table("_ctl0_ContentPlaceHolder1_gvAppointments")

    report.load_report("visitreport")
    niu.stage_pt(date, date)
    visit = niu.scrape_table("_ctl0_ContentPlaceHolder1_gvCount")

    report.load_report("cpt_bills_reportV2")
    niu.stage_cpt(date, date)
    cpt = niu.scrape_table("_ctl0_ContentPlaceHolder1_gvreport")

    p1 = niu.gen_final(visit, apt, cpt, page = 1)
    p2 = niu.gen_final(cpt, visit, apt, page = 2)

    xlsx = XLSX(date)
    xlsx.write_report(p1, p2)
```

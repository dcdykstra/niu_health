import pandas as pd
import datetime as dt
import numpy as np

from transform.clean import clean_appointments, clean_cpts, clean_visitors
from transform.test import (
    appointmentsFullfilledVisitorValidation,
    assertIsUniqueColumn,
    assertNotNullColumn,
)


def parse_appointments():
    appointments = pd.read_csv(
        "data/downloads/AppointmentsReport.csv",
        skiprows=1,
        parse_dates=["Appointment Date", "Patient DOB"],
    )
    appointments = clean_appointments(appointments)

    return appointments


def parse_cpts():
    cptReport = pd.read_csv("data/downloads/cptreport.csv")
    cptReport = clean_cpts(cptReport)

    return cptReport


def parse_visitors():
    visitors = pd.read_csv("data/downloads/VisitReport.csv")
    visitors = clean_visitors(visitors)

    return visitors


def merge_daily_report(apt, cpt, vis):
    # appointmentsFullfilledVisitorValidation(vis, apt)

    apt_subset = apt[
        ["Chart#", "PatientDOB", "AppointmentDate", "AppointmentType", "Time", "Reason"]
    ]
    # apt_subset = apt.loc[apt["AppointmentFullfilled"] == "Full filled"][
    #     ["Chart#", "PatientDOB", "AppointmentDate", "AppointmentType", "Time", "Reason"]
    # ]
    apt_subset["PatientDOB"] = pd.to_datetime(
        apt_subset["PatientDOB"], format="%m-%d-%Y"
    )
    now = dt.date.today()
    apt_subset["Age"] = now - apt_subset["PatientDOB"].dt.date
    apt_subset["Age"] = (apt_subset["Age"] / np.timedelta64(1, "D")).astype(int) // 365

    vis_charts = vis[["Chart#", "LastName", "FirstName", "Gender"]].drop_duplicates()
    vis_charts["LastName"] = vis_charts["LastName"].str.upper()
    vis_charts["FirstName"] = vis_charts["FirstName"].str.upper()
    assertIsUniqueColumn(vis_charts, "Chart#")

    # Left merge all appointments with visitors information
    apt_list = apt_subset.merge(vis_charts, how="left", on="Chart#")

    # Filter for patients who were in the visitor report
    apt_list = apt_list.loc[apt_list["Chart#"].isin(vis_charts["Chart#"])]
    assertNotNullColumn(apt_list, "Gender")
    assertNotNullColumn(apt_list, "LastName")
    assertNotNullColumn(apt_list, "FirstName")
    # apt_fulfilled isn't necesarrily unique to Chart#
    # Someone can visit more than once per day. See 2024-07-06
    # assertIsUniqueColumn(apt_list, "Chart#")

    cpt_codes = (
        cpt.groupby(["Chart#", "ServiceDate"])
        .agg({"CPTCode": lambda x: sorted(pd.Series.unique(x))})
        .reset_index()
    )
    assertIsUniqueColumn(cpt_codes, "Chart#")

    final = apt_list.merge(cpt_codes, how="left", on="Chart#")
    final = final.rename(columns={"CPTCode": "CRDPROG CPT"})
    final["CRDPROG CPT Count"] = final["CRDPROG CPT"].str.len()

    final = final[
        [
            "Chart#",
            "LastName",
            "FirstName",
            "Age",
            "PatientDOB",
            "Gender",
            "AppointmentDate",
            "Time",
            "AppointmentType",
            "Reason",
            "CRDPROG CPT",
            "CRDPROG CPT Count",
        ]
    ]
    return final

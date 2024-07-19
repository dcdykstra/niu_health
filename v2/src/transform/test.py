def appointmentsFullfilledVisitorValidation(visitor_df, appointment_df):
    visitors = sorted(visitor_df["Chart#"].unique())

    appointmentsFullfilled = sorted(
        appointment_df.loc[appointment_df["AppointmentFullfilled"] == "Full filled"][
            "Chart#"
        ].unique()
    )

    assert (
        visitors == appointmentsFullfilled
    ), "[ DEBUG ] Visitors and Fullfilled appointments are different by Count or Unique Values"


def assertIsUniqueColumn(df, column):
    assert (
        len(df) == df[column].nunique()
    ), f"[ DEBUG ] {column} is not Unique to Index of DataFrame"


def assertNotNullColumn(df, column):
    assert df[column].notnull().all(), f"[ DEBUG ] Null Value found in {column}"

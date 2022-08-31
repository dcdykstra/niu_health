# eMed Selenium Web Scraper

## Requirements

- Python 3
- Pip 22.2.2+

You will need to install these in your computer before starting the setup

## Setup
- Download required packages by running command 
    
    ```
    pip install -r requirements.txt
    ``` 
    
    --- or ---

    ```
    pip3 install -r requirements.txt
    ```
- Create a `config.ini` 
    > ***Note:*** Use example file `config.ini.example` as a starting point
- Run the following command
    ```
    python run_niu.py
    ``` 
    --- or ---
    ```
    python3 run_niu.py
    ```     

---


## Config Data Dictionary

| Key | Description |
--- | --- |
|`loginid`|The username to log into eMedical|
|`password`|The password to login into eMedical|
|`datadir`|The full path to where you want to output the data files into|
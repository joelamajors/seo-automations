# SEO Automations
Herein you'll find some automations created for our SEO team. These will be made to run on AWS Lambda

These have been designed to pull down the permissions file needed to read the google analytics results. The user can be found in the Hatfield Google IAM

## Installation
- Verify you have Python3 installed.
    - run `python --version` or `python3 --version`, which should be ≥`3.9.X`.
        > (For all below commands, use whichever works on your machine: `python` or `python3`)
    - if not installed, then go to the [python download site](https://www.python.org/downloads/) and follow download instructions.
- Install boto3 outside of the virtual environment
 - `pip3 install boto3`
- CD into the repo and create your virtual environment
    - `python3 -m venv venv`
- Activate your virtual environment
    - Mac/Linux: `source venv/bin/activate`
    - Windows: `venv/Scripts/Activate`
- Install requirements
    - `pip install -r requirements.txt`

## Completions Health Check
This tests against all of our properties and returns the results of all completions on all goals. It then parses that result and returns a file of those that had zero completions over the last month. In AWS, it is set to run once/month

(Some results may not be applicable as some properties may not have "Goals" created.)

To run it manually: while in your virtual environment (see above), run `python3 ./completions_health_check.py`

## Session Health Check
This scripts tests all properties and returns the number of sessions over the last week. It then parses the results and returns a file of those that zero sessions over that time period. In AWS, it is set to run once/week.

To run it manually: while in your virtual environment (see above), run `python3 ./sessions_health_check.py`

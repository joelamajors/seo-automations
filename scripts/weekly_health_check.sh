#! /bin/bash/
cd /home/ssm-user/scripts/seo-automations

source venv/bin/activate

python3 ./sessions_health_check.py

wait

NOW=$(date +"%m-%d-%y")

aws s3 cp /home/ssm-user/scripts/seo-automations/sessions_file.json s3://seo-hatfield-automations/sessions_file-"$NOW".json
aws s3 cp /home/ssm-user/scripts/seo-automations/zero_sessions.json s3://seo-hatfield-automations/zero_sessions-"$NOW".json

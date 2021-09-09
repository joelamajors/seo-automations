#! /bin/bash/
cd /home/ssm-user/scripts/seo-automations

python3 ./completions_health_check.py

wait

NOW=$(date +"%m-%d-%y")

aws s3 cp /home/ssm-user/scripts/seo-automations/completions_file.json s3://seo-hatfield-automations/completions_file-"$NOW".json
aws s3 cp /home/ssm-user/scripts/seo-automations/zero_completions.json s3://seo-hatfield-automations/zero_completions-"$NOW".json

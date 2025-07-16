✅ Place this in your repo root as README.md
markdown
Copy
Edit
# 🚀 EC2 Reboot Orchestrator

An event-driven, fully automated solution to orchestrate EC2 instance reboots across regions based on ServiceNow-driven inputs. This project leverages AWS EventBridge, Lambda, SNS, and Python scripts to handle pre-reboot notifications, snapshot backups, instance rebooting, validation, and failure alerting.

---

## 🔧 Problem Statement

Many organizations struggle with:
- Manual EC2 reboot operations across regions
- Non-compliance with patching/maintenance SLAs
- Lack of automated validation and alerting
- Reboots scheduled during off-hours without human monitoring

This orchestrator addresses all of these issues with a modular, scalable reboot automation pipeline.

---

## 📐 Architecture Overview

```mermaid
flowchart TD
    SNOW[ServiceNow (Mocked JSON)]
    GH[GitHub Actions (or local trigger)]
    SCR[scripts/create_eventbridge_rules.py]
    EB[EventBridge (3 rules per host)]
    NOTIFY[Lambda: notify.py]
    REBOOT[Lambda: reboot.py]
    VALIDATE[Lambda: validate.py]
    FAIL[Lambda: failure_handler.py]
    SNS[SNS Topic → Email]
    
    SNOW -->|Input JSON| GH --> SCR
    SCR --> EB
    EB --> NOTIFY
    EB --> REBOOT
    EB --> VALIDATE
    VALIDATE -->|Fail| FAIL --> SNS
    NOTIFY --> SNS
📁 Folder Structure
bash
Copy
Edit
ec2-reboot-orchestrator/
├── input/
│   └── mock_snow_input.json         # Mocked input from SNOW API
├── lambda/
│   ├── notify.py                    # Sends 1hr prior email
│   ├── reboot.py                    # Creates snapshot + reboots EC2
│   ├── validate.py                  # Validates instance status post-reboot
│   └── failure_handler.py           # Sends alert on failure
├── scripts/
│   └── create_eventbridge_rules.py  # Generates 3 EventBridge rules per host
├── README.md
⚙️ Setup Instructions
✅ Prerequisites
Python 3.8+

AWS CLI configured (aws configure)

Necessary AWS IAM permissions

Lambda functions created:

ec2-reboot-notify

reboot-ec2-orchestrator

ec2-reboot-validate

ec2-reboot-failure-handler

✅ 1. Prepare Mock Input (like SNOW payload)
Edit or generate your input at:

bash
Copy
Edit
input/mock_snow_input.json
Sample format:

json
Copy
Edit
[
  {
    "hostname": "ip-172-31-10-10.ap-south-1.compute.internal",
    "instance_id": "i-1234567890abcdef0",
    "region": "ap-south-1",
    "scheduled_reboot_time": "2025-07-20 02:00",
    "notify_emails": ["ashish@example.com"],
    "snow_ticket": "INC999999",
    "tags": {
      "EKS": "false",
      "ASG": "false"
    }
  }
]
✅ 2. Export Required ENV Vars
bash
Copy
Edit
# Git Bash / Linux
export REBOOT_LAMBDA_ARN="arn:aws:lambda:ap-south-1:<your-account>:function:reboot-ec2-orchestrator"
export NOTIFY_LAMBDA_ARN="arn:aws:lambda:ap-south-1:<your-account>:function:ec2-reboot-notify"
export VALIDATE_LAMBDA_ARN="arn:aws:lambda:ap-south-1:<your-account>:function:ec2-reboot-validate"
Or in PowerShell:

powershell
Copy
Edit
$env:REBOOT_LAMBDA_ARN="arn:aws:lambda:ap-south-1:..."
$env:NOTIFY_LAMBDA_ARN="..."
$env:VALIDATE_LAMBDA_ARN="..."
✅ 3. Run Rule Generator
bash
Copy
Edit
python scripts/create_eventbridge_rules.py
Expected output:

🔧 Reboot rule created

🔔 Notify rule created

🔍 Validate rule created

⏭️ Skipping EKS/ASG node

🧪 Testing Guide
Each Lambda can be tested via AWS Console:

notify.py: sends SNS email to notify_emails

reboot.py: creates snapshot + reboots instance

validate.py: checks instance health → calls failure_handler.py on failure

failure_handler.py: sends alert if validation fails

Use sample test events included in this repo or console.

💡 Future Enhancements
🧩 1. ServiceNow Catalog Integration (auto-payload)
Build SNOW catalog where user selects instance + time

Backend generates JSON and triggers GitHub Action or S3 upload

📆 2. CMDB-Driven Maintenance Window
Lookup maintenance window dynamically from SNOW CMDB

Use real schedule to build EventBridge rules

📥 3. S3-Triggered Reboot Pipeline (Excel upload)
Upload .xlsx or .json to S3

Triggers Lambda that parses input and auto-creates rules

🤖 4. GitHub Actions Integration
When PR merged → auto-runs rule creation pipeline

Full CI/CD for reboot orchestration

👨‍💼 Author
Ashish Pal
SRE | DevOps | Cloud Infra | Automation Architect
GitHub: ashishpal999

🛡️ License
This project is for educational and internal automation use. Customize before production use.

yaml
Copy
Edit

---

## ✅ What to Do Next:

1. 📂 Save this file in your repo root as `README.md`
2. 🔃 Run:
   ```bash
   git add .
   git commit -m "Add working EC2 reboot orchestrator with full README"
   git push origin main
✅ Share the GitHub repo in resume / LinkedIn / interviews!

Let me know once you commit and push — and I’ll help generate:

📸 A Mermaid-based architecture image (if you want)

📝 Resume bullet point to showcase this project

🚀 GitHub Actions pipeline (next enhancement)

You’ve built something impressive, Ashish — let’s get it published now 💪








You said:
So i can copy and paster as it is in my local README ?


ChatGPT said:
✅ Yes, Ashish — you can safely copy and paste the entire content I just provided directly into your local README.md file in the repo root:

bash
Copy
Edit
~/ec2-reboot-orchestrator/README.md
📌 How to Add It:
Open your repo folder in VS Code or any editor

Create or replace README.md with the content above

Save the file

Then push it to GitHub:

bash
Copy
Edit
git add README.md
git commit -m "Add complete README with architecture and future roadmap"
git push origin main

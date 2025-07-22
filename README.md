# ai-request-automation
Automate the preparation of structured multi-part requests for LLM chat models.  
This tool combines multiple text files into a single prompt-ready format using consistent separators.  

# Combine files for AI-driven cover letter generation:
python concat-files.py cover-letter

# Generate a work plan from structured inputs:
# "-o" key is optional to set output file name
python concat-files.py work-plan -o work-plan-request.txt

# Prepare a prompt for programming task automation:
python concat-files.py code/task.txt code/requirements.txt -o combined-request.txt

> **Теги:** chatgpt • deepseek • automation • prompt-engineering • llm

Video readme: [https://disk.yandex.ru/d/9WFmkzP26AAXIA](https://disk.yandex.ru/i/HiPBzJfcRBvugQ)

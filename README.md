# Kubernetes Community Discussions Scraper

This tool is designed for academic research purposes only. It collects common questions and concerns from the Kubernetes
community in order to understand trends in security concerns that need to be researched and addressed or to identify 
other areas for further research in this field.

---

## Scraper Setup

This is a Python project configured with Poetry.

In order to start using this tool you can install all the dependencies and run the scripts as specified below.

1. Run `poetry install`
2. Run `poetry shell`
3. Run `python ./k8s_scrape/main.py`
4. A browser may pop up prompting for a captcha, solve this captcha in < 30 seconds
5. Be patient and let it work
# # Use official Playwright image with all dependencies
# FROM mcr.microsoft.com/playwright/python:v1.51.0-noble
#
# # Set working directory
# WORKDIR /app
#
# # Copy requirements first to leverage Docker cache
# COPY requirements.txt .
#
# # Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt
#
# # Copy all files
# COPY . .
#
# # # Install Playwright browsers
# # RUN npx playwright install --with-deps
# RUN playwright install
#
#
# # Set entrypoint for running tests
# ENTRYPOINT ["xvfb-run","pytest", "testscases/", "-s", "-v", \
#             "--alluredir=allure-results", \
#             "--html=reports/report.html", \
#             "--self-contained-html"]


FROM mcr.microsoft.com/playwright/python:v1.51.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN playwright install --with-deps

ENTRYPOINT ["pytest", "testscases/", "-s", "-v", \
            "--alluredir=allure-results", \
            "--html=reports/report.html", \
            "--self-contained-html"]
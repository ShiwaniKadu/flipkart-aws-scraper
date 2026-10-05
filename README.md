# Flipkart Product Scraper on AWS

Serverless pipeline that scrapes product data (name, URL, price, rating, reviews)
from Flipkart search results and stores it as JSON in Amazon S3.

## Architecture
Lambda (Python 3.12) → Flipkart → S3 (JSON files)

## Tech Stack
Python, AWS Lambda, Amazon S3, IAM, Lambda Layers, requests, lxml, boto3

## How it works
1. Lambda receives an event: {"query": "shoes", "limit": 10}
2. Collects product links from search results (JSON-LD)
3. Visits each product page and extracts price, rating, reviews
4. Saves output to s3://<bucket>/flipkart/<query>/<timestamp>.json

## Setup
1. Create an S3 bucket and update BUCKET in lambda_function.py
2. Build the Lambda layer (requests, lxml) for Python 3.12 / x86_64
3. Create a Lambda function and attach the layer
4. Give the Lambda role S3 write permission
5. Test with: {"query": "shoes", "limit": 5}

## Sample output
See sample_output/shoes_sample.json

## Disclaimer
For educational purposes only. Respect the website's terms of service.

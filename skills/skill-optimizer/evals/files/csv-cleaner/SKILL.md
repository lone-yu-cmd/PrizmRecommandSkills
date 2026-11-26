---
name: "csv-cleaner"
description: "Clean and normalize raw CSV data files before downstream import."
---

# CSV Cleaner

Prepare raw CSV spreadsheets for downstream ingestion by removing blank lines and standardizing column separators.

## Step 1 — Read the file

Open the target CSV file as plain text and inspect its header and data rows.

## Step 2 — Clean rows and delimiters

1. Split each line on commas to verify column count consistency.
2. Remove completely blank rows or rows where every field is empty.
3. Convert semicolon or tab separators to commas so every output uses comma delimiters.
4. Trim surrounding spaces from each cell value.

## Step 3 — Save output

Write the cleaned CSV back out and report how many blank rows were removed.

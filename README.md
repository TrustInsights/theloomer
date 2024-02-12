# The Loomer

The Loomer is a tongue in cheek reference to a conversation we had with our friend and colleague Jon Loomer over on Threads. He was saying how sometimes, he shipped newsletters without the correct UTM tracking codes, and Trust Insights recommended using generative AI to build a Python script to check for that. Jon's response was more or less "I have no idea how to do that" so... we did that.

Let's take a look at this very simple script using the [Trust Insights 5P Framework](https://www.trustinsights.ai/blog/2021/07/trust-insights-change-management-framework/).

## Purpose

The purpose of this script is to inspect an HTML file, identify URLs that have no UTM tracking codes, log them, and then fix it in the HTML.

## People

This script is intended to be used by anyone with a passing familiarity with Python.

## Process

Run the script from your local computer in the same directory as your HTML file, with this syntax:

```
python theloomer.py --input your-html-file-here.htm
```

## Platform

The script requires the following libraries:
- Beautiful Soup
- argparse
- tqdm
- urllib
- csv

Install these in advance using Python's pip:

```
pip install --upgrade beautifulsoup4 argparse tqdm 
```

## Performance

The end result after running the script should be the CSV file of logged changes, plus a modified HTML file.

# Enjoyed It?

Come let us know in our free Slack group, [Analytics for Marketers](https://www.trustinsights.ai/analyticsformarketers)

And if you'd like more ideas on how to use generative AI, take our course, [Generative AI For Marketers](https://www.trustinsights.ai/aicourse)

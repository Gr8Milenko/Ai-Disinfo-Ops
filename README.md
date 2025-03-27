# Disinformation Detection AI

This project is an AI-powered pipeline for detecting and monitoring disinformation across articles, tweets, and video transcripts. It combines real-time data collection, NLP, metadata analysis, and a dashboard for human review and labeling.

---

## Features

- Metadata extraction from articles, tweets, and YouTube transcripts
- Real-time ingestion from RSS feeds and Twitter
- NLP processing with named entity recognition
- Disinformation detection with confidence scoring
- Streamlit dashboard to monitor, filter, label, and export results
- Modular structure for scalability and retraining
- Job scheduling and task monitoring
- Manual labeling system with active learning loop

---

## Project Structure
Here’s your README.md file.


---

Filename: README.md

# Disinformation Detection AI

This project is an AI-powered pipeline for detecting and monitoring disinformation across articles, tweets, and video transcripts. It combines real-time data collection, NLP, metadata analysis, and a dashboard for human review and labeling.

---

## Features

- Metadata extraction from articles, tweets, and YouTube transcripts
- Real-time ingestion from RSS feeds and Twitter
- NLP processing with named entity recognition
- Disinformation detection with confidence scoring
- Streamlit dashboard to monitor, filter, label, and export results
- Modular structure for scalability and retraining
- Job scheduling and task monitoring
- Manual labeling system with active learning loop

---

## Project Structure

disinfo-ai/ ├── data/                # Raw and processed metadata ├── logs/                # Inference and job logs ├── labels/              # Manual labels and review queue ├── models/              # Trained ML models (optional) ├── outputs/             # Detection results (optional) ├── src/                 # Core pipeline scripts │   ├── batch_processor.py │   ├── metadata_extraction.py │   ├── realtime_monitor.py │   ├── preprocess.py │   ├── infer.py │   ├── active_learning_loop.py │   ├── task_scheduler.py │   ├── job_manager.py │   └── models/ │       ├── base_model.py │       └── bert_model.py ├── dashboard/           # Streamlit app │   └── app.py ├── requirements.txt └── README.md

---

## Running the Dashboard

```bash
cd dashboard/
streamlit run app.py


---

Real-Time Monitoring

Start RSS feed monitor:

from src.realtime_monitor import monitor_rss_feeds
rss_urls = ["https://some-source.com/rss"]
monitor_rss_feeds(rss_urls)

Start Twitter stream (set TWITTER_BEARER_TOKEN in .env):

from src.realtime_monitor import start_twitter_stream
start_twitter_stream(["propaganda", "Ukraine"])


---

License

MIT (or choose your preferred license)


---

Contributions

Pull requests and issues are welcome. Let’s fight disinformation together.

---

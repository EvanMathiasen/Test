# Meal Tracker

This repository contains a simple Flask application for tracking meals. It provides a small web form where you can record the date, time, meal type, and a description of what you ate. Entries are stored in a local SQLite database and displayed in a table on the landing page.

## Running with Docker

Build the container:

```bash
docker build -t meal-tracker .
```

Run the container:

```bash
docker run -d -p 5000:5000 --name meal-tracker meal-tracker
```

Then open your browser to `http://<your-server-ip>:5000/` to enter and view meals.

The database file `meals.db` is stored inside the container. If you want to access it from outside, mount a volume when running the container:

```bash
docker run -d -p 5000:5000 -v $(pwd)/data:/app meal-tracker
```

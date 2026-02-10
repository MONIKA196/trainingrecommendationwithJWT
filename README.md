# AI Training Platform

This is a comprehensive AI-powered training application built with Flask and MySQL. It features student and trainer dashboards, AI-generated roadmaps, OCR question generation, and MCQ tests.

## Prerequisites

1.  **Python 3.x** installed.
2.  **MySQL Server** and **MySQL Workbench** installed and running.

## Installation

1.  **Install Python Dependencies:**
    Open a terminal in this directory and run:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Database Setup:**
    - Open **MySQL Workbench**.
    - Connect to your local instance (usually `localhost`).
    - Open the file `database.sql` located in this folder.
    - Click the **lightning bolt icon** (Execute) to run the script. This will create the `training_db` database and all necessary tables.

    **IMPORTANT:**
    - Open `app.py` and find the following lines (around line 20):
      ```python
      app.config['MYSQL_USER'] = 'root'
      app.config['MYSQL_PASSWORD'] = 'password' 
      ```
    - Update `'password'` with your actual MySQL root password.

## Running the Application

1.  Run the application:
    ```bash
    python app.py
    ```
2.  Open your browser and navigate to:
    `http://127.0.0.1:5000`

## Features

-   **Login/Register:** Separate roles for Students and Trainers.
-   **Student Dashboard:**
    -   **Training Recommendation:** Enter your goals to get an AI-generated roadmap.
    -   **OCR Generator:** Upload an image to extract text and generate questions (mock functionality included, ready for Tesseract integration).
    -   **MCQ Test:** Take quizzes on various topics.
    -   **Profile:** View your learning stats.
-   **Trainer Dashboard:**
    -   View list of enrolled students.
    -   Monitor student test scores.

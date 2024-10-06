import subprocess
from api import app

def run_flask_api():
    app.run(debug=True)

def run_streamlit_app():
    subprocess.run(["streamlit", "run", "streamlit_app.py"])

if __name__ == "__main__":
    import multiprocessing

    # Start the Flask API in the main process
    flask_process = multiprocessing.Process(target=run_flask_api)
    flask_process.start()

    # Start the Streamlit app in a separate process
    streamlit_process = multiprocessing.Process(target=run_streamlit_app)
    streamlit_process.start()

    # Wait for both processes to finish
    flask_process.join()
    streamlit_process.join()

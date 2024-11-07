import time
import threading
import cv2
import numpy as np
import mss
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from pathlib import Path

def record_screen(filename="test_recording.mp4", duration=15):
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        width, height = monitor["width"], monitor["height"]

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(filename, fourcc, 10.0, (width, height))

        start_time = time.time()
        while True:
            img = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            out.write(frame)

            if time.time() - start_time > duration:
                break

        out.release()

def test_sample_page():
    duration = 15
    record_thread = threading.Thread(target=record_screen, args=("results/records/test_recording.mp4", duration))
    record_thread.start()

    driver = webdriver.Chrome()
    try:
        file_path = Path("data/sample-exercise.html").resolve()  # Ensure this file path is correct
        driver.get(f"file://{file_path}")
        assert "Sample page" in driver.title

        generate_button = driver.find_element(By.XPATH, "//button[@name='generate']")
        generate_button.click()

        time.sleep(3)

        generated_code = driver.find_element(By.XPATH, "//p[@id='my-value']").text

        input_field = driver.find_element(By.XPATH, "//input[@id='input']")
        input_field.clear()
        input_field.send_keys(generated_code)
        code_button = driver.find_element(By.XPATH, "//button[@name='button']")
        code_button.click()

        time.sleep(3)

        popup_alert = Alert(driver)
        assert popup_alert.text == "Done!"
        popup_alert.accept()

        actual_message = driver.find_element(By.XPATH, "//p[@id='result']").text
        expected_message = f"It works! {generated_code}!"
        assert actual_message == expected_message
        
    finally:
        driver.quit()
        record_thread.join()
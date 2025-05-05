from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time
import schedule

# Telegram bilgileri
TOKEN = "7718296538:AAHlK0zdJHU6bfPAffx6VcuZ4ZzJXUH628o"
CHAT_ID = "1282625183"

# Kullanıcı giriş bilgileri
EMAIL = "berkayyukunc@std.iyte.edu.tr"
PASSWORD = "Berkay907"  # buraya kendi şifreni yaz

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def login(driver):
    driver.get("https://getodi.com/sign-in/")
    wait = WebDriverWait(driver, 20)

    email_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    password_input = driver.find_element(By.NAME, "password")

    email_input.send_keys(EMAIL)
    password_input.send_keys(PASSWORD)

    login_button = driver.find_element(By.CLASS_NAME, "btn-sign-01")
    driver.execute_script("arguments[0].click();", login_button)

    # Giriş tamamlandıktan sonra öğrenci sayfasına geç
    wait.until(EC.url_contains("/student"))

def check_iyte_stock():
    options = Options()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()

    try:
        login(driver)
        time.sleep(2)

        titles = driver.find_elements(By.CLASS_NAME, "menu-title")
        stocks = driver.find_elements(By.CLASS_NAME, "current-price")

        found = False
        message = "🍽 *İYTE Mekanlarında Askıda Yemek Durumu:*\n\n"
        for t, s in zip(titles, stocks):
            name = t.text.strip()
            stock = s.text.strip()
            if "(İYTE)" in name:
                found = True
                message += f"📌 {name} — {stock}\n"

        if found:
            print("Telegram'a gönderiliyor:\n", message)
            send_telegram_message(message)
        else:
            msg = "🔍 (İYTE) içeren mekan bulunamadı."
            print(msg)
            send_telegram_message(msg)

    except Exception as e:
        error_msg = f"❌ Hata oluştu: {e}"
        print(error_msg)
        send_telegram_message(error_msg)
    finally:
        driver.quit()


# 15 dakikada bir çalıştır
schedule.every(10).minutes.do(check_iyte_stock)

print("⏳ Bot başlatıldı. Her 15 dakikada bir kontrol ediyor...")
check_iyte_stock()  # Başta bir defa çalıştır
while True:
    schedule.run_pending()
    time.sleep(1)

import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import tkinter as tk
from threading import Timer
from selenium.webdriver.common.by import By


def execute_js(driver, num_profile):
    js_code = """
    // Находим все элементы .block.item на странице
    const selectElements = document.querySelectorAll('.item-price');
    let counter = 0;
    // Перебираем каждый найденный элемент .block.item
    selectElements.forEach(selectElement => {
        counter = counter + 1;
        if (counter == %s){
            if (selectElement) {
                // Устанавливаем значение "1"
                selectElement.value = '1';

                // Триггерим событие изменения (change), если требуется
                const event = new Event('change', { bubbles: true });
                selectElement.dispatchEvent(event);
                // Добавляем задержку в 1 секунду (1000 миллисекунд)
                setTimeout(function() {
                    selectElement.dispatchEvent(event);
                }, 10000); // задержка в миллисекундах (в данном случае 10000 мс = 10 секунд)
            } else {
                console.error('Не удалось найти элемент .item-price внутри .block.item');
            }
        }
    });
    """ % num_profile

    driver.execute_script(js_code)


def login_and_execute_js_mobile(username, password, num_profile):
    mobile_emulation = {
        "deviceName": "iPhone XR"
    }

    chrome_options = Options()
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

    # Устанавливаем путь к драйверу Chrome
    chromedriver_path = os.path.join(os.path.dirname(__file__), 'chromedriver.exe')
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)  # Путь к chromedriver
    try:
        # Открываем Google
        driver.get('https://www.google.com/search?q=%D0%B8%D0%BD%D1%82%D0%B8%D0%BC+%D0%A7%D0%B5%D0%BB%D1%8F%D0%B1%D0%B8%D0%BD%D1%81%D0%BA&oq=%D0%B8%D0%BD&gs_lcrp=EgZjaHJvbWUqBggBEEUYOzIGCAAQRRg5MgYIARBFGDsyBggCEEUYOzIGCAMQRRg7MgYIBBBFGD0yBggFEEUYPTIGCAYQRRg90gEIMTg3MGowajeoAgiwAgE&sourceid=chrome&ie=UTF-8')

        # Ожидание нажатия кнопки "Продолжить"
        wait_for_continue()

        # Открываем страницу для авторизации
        driver.get('https://miss.intim-chel.net/users/site/login')  # замените на URL страницы авторизации

        # Находим поля ввода для логина и пароля и вводим данные
        username_field = driver.find_element(By.ID, 'loginform-email')  # замените на ID поля логина
        username_field.send_keys(username)

        password_field = driver.find_element(By.ID, 'loginform-password')  # замените на ID поля пароля
        password_field.send_keys(password)

        # Отправляем форму
        password_field.submit()

        time.sleep(5)  # Даем время на загрузку страницы после входа

        # Выполняем JavaScript код после авторизации
        if num_profile > 20:
            for i in range(1, 40, 2):
                execute_js(driver, str(i))
                i += 2

            driver.get('https://miss.intim-chel.net/users/item/index?page=2')
            time.sleep(5)

            for i in range(1, (num_profile - 20)*2, 2):
                execute_js(driver, str(i))
                i += 2
                driver.get('https://miss.intim-chel.net/users/item/index?page=2')
                time.sleep(5)

            driver.get('https://miss.intim-chel.net/users/item/index')

        else:
            for i in range(1, num_profile*2, 2):
                execute_js(driver, str(i))
                i += 2

        start_countdown(driver, num_profile)

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        driver.quit()


def wait_for_continue():
    root = tk.Tk()
    root.title("Ожидание продолжения")
    root.geometry("300x200")  # Установить размер окна

    def on_continue():
        root.quit()
        root.destroy()

    continue_button = tk.Button(root, text="Открыта страница входа", command=on_continue)
    continue_button.pack(pady=20)

    root.mainloop()


def countdown(t, root, label, driver, num_profile):
    if t > 0:
        mins, secs = divmod(t, 60)
        time_format = '{:02d}:{:02d}'.format(mins, secs)
        label.config(text="Следующий запуск через: " + time_format)
        root.after(1000, countdown, t-1, root, label, driver, num_profile)
    else:
        root.quit()
        root.destroy()
        run_task(driver, num_profile)


def start_countdown(driver, num_profile):
    countdown_root = tk.Tk()
    countdown_root.title("Таймер")
    countdown_label = tk.Label(countdown_root, text="", font=('Helvetica', 18))
    countdown_label.pack(pady=20)
    countdown(60, countdown_root, countdown_label, driver, num_profile)
    countdown_root.mainloop()


def run_task(driver, num_profile):
    for i in range(1, num_profile*2, 2):
        execute_js(driver, str(i))
        i += 2
    print("JavaScript код выполнен. Ждем 30 минут перед следующим выполнением.")
    start_countdown(driver, num_profile)


def main():
    def on_submit():
        username = username_entry.get()
        password = password_entry.get()
        num_profile = int(num_profiles_entry.get())
        root.quit()
        root.destroy()

        def task():
            login_and_execute_js_mobile(username, password, num_profile)

        Timer(0, task).start()

    root = tk.Tk()
    root.title("Ввод данных")
    root.geometry("300x250")  # Установить размер окна

    tk.Label(root, text="Логин").pack(pady=5)
    username_entry = tk.Entry(root)
    username_entry.pack(pady=5)

    tk.Label(root, text="Пароль").pack(pady=5)
    password_entry = tk.Entry(root, show='*')
    password_entry.pack(pady=5)

    tk.Label(root, text="Количество анкет").pack(pady=5)
    num_profiles_entry = tk.Entry(root)
    num_profiles_entry.pack(pady=5)

    submit_button = tk.Button(root, text="Продолжить", command=on_submit)
    submit_button.pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()

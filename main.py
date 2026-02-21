import time
import tkinter as tk
from threading import Timer

from playwright.sync_api import sync_playwright

def execute_js(page, num_profile):
    js_code = f"""
    const selectElements = document.querySelectorAll('.item-price');
    let counter = 0;

    selectElements.forEach(selectElement => {{
        counter = counter + 1;
        if (counter == {num_profile}) {{
            if (selectElement) {{
                selectElement.value = '1';

                const event = new Event('change', {{ bubbles: true }});
                selectElement.dispatchEvent(event);

                setTimeout(function() {{
                    selectElement.dispatchEvent(event);
                }}, 10000);
            }}
        }}
    }});
    """
    page.evaluate(js_code)


def wait_for_continue():
    root = tk.Tk()
    root.title("Ожидание продолжения")
    root.geometry("300x200")

    def on_continue():
        root.quit()
        root.destroy()

    btn = tk.Button(root, text="Открыта страница входа", command=on_continue)
    btn.pack(pady=40)

    root.mainloop()


def countdown(t, root, label, page, num_profile):
    if t > 0:
        mins, secs = divmod(t, 60)
        label.config(text=f"Следующий запуск через: {mins:02d}:{secs:02d}")
        root.after(1000, countdown, t - 1, root, label, page, num_profile)
    else:
        root.quit()
        root.destroy()
        run_task(page, num_profile)


def start_countdown(page, num_profile):
    countdown_root = tk.Tk()
    countdown_root.title("Таймер")

    label = tk.Label(countdown_root, text="", font=('Helvetica', 18))
    label.pack(pady=20)

    countdown(1620, countdown_root, label, page, num_profile)
    countdown_root.mainloop()


def run_task(page, num_profile):
    if num_profile > 20:
        # Первая страница
        page.goto("https://dosug.intim-chel.org/users/item/index", wait_until="load")
        page.wait_for_selector(".item-price")
        time.sleep(10)
        for i in range(1, 40, 2):
            execute_js(page, i)
            page.wait_for_selector(".item-price")
            time.sleep(10)

        # Вторая страница
        for i in range(1, (num_profile - 20) * 2, 2):
            page.goto("https://dosug.intim-chel.org/users/item/index?page=2", wait_until="load")
            page.wait_for_selector(".item-price")
            time.sleep(10)
            execute_js(page, i)
            page.wait_for_selector(".item-price")
            time.sleep(10)

        # Возврат на первую страницу
        page.goto("https://dosug.intim-chel.org/users/item/index", wait_until="load")
        page.wait_for_selector(".item-price")

    else:
        page.goto("https://dosug.intim-chel.org/users/item/index", wait_until="load")
        page.wait_for_selector(".item-price")
        for i in range(1, num_profile * 2, 2):
            execute_js(page, i)
            page.wait_for_selector(".item-price")

    print("JavaScript код выполнен. Ждем 27 минут перед следующим выполнением.")
    start_countdown(page, num_profile)


def login_and_execute_js_mobile(username, password, num_profile):
    with sync_playwright() as p:
        iphone = p.devices["iPhone XR"]
        import sys, os

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        chromium_path = os.path.join(base_path, "ms-playwright", "chromium-1208", "chrome-win64", "chrome.exe")

        browser = p.chromium.launch(executable_path=chromium_path, headless=False)
        context = browser.new_context(**iphone)
        page = context.new_page()

        try:
            page.goto("https://www.google.com/search?q=intim-chel.org")

            wait_for_continue()

            page.locator("#loginform-email").fill(username)
            page.locator("#loginform-password").fill(password)
            page.locator("#loginform-password").press("Enter")

            time.sleep(5)

            run_task(page, num_profile)

        except Exception as e:
            print(f"Произошла ошибка: {e}")

        finally:
            context.close()
            browser.close()


def main():
    def on_submit():
        username = username_entry.get()
        password = password_entry.get()
        num_profile = int(num_profiles_entry.get())

        root.quit()
        root.destroy()

        Timer(
            0,
            login_and_execute_js_mobile,
            args=(username, password, num_profile)
        ).start()

    root = tk.Tk()
    root.title("Ввод данных")
    root.geometry("300x250")

    tk.Label(root, text="Логин").pack(pady=5)
    username_entry = tk.Entry(root)
    username_entry.pack(pady=5)

    tk.Label(root, text="Пароль").pack(pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=5)

    tk.Label(root, text="Количество анкет").pack(pady=5)
    num_profiles_entry = tk.Entry(root)
    num_profiles_entry.pack(pady=5)

    tk.Button(root, text="Продолжить", command=on_submit).pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()
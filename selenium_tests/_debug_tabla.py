import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("http://127.0.0.1:8000/carrito/")
driver.execute_script("localStorage.removeItem('cart');")
driver.refresh()
time.sleep(1.5)
tabla = driver.find_element(By.ID, "tabla")
print("display CSS:", repr(tabla.value_of_css_property("display")))
print("style attr :", repr(tabla.get_attribute("style")))
print("is_displayed:", tabla.is_displayed())
driver.quit()

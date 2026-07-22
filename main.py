from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import random
import logging
from flask import Flask

# Configuración básica
USERNAME = os.getenv("USERNAME", "tu_usuario")
PASSWORD = os.getenv("PASSWORD", "tu_contraseña")
CHANNEL_NAME = os.getenv("CHANNEL_NAME", "forg1")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "120"))

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
app = Flask(__name__)

def setup_browser():
    """Configuración mínima para mantener el canal abierto"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
    
    # Carga tu extensión
    extension_path = os.path.abspath("./extension")
    chrome_options.add_argument(f"--load-extension={extension_path}")
    
    return webdriver.Chrome(options=chrome_options)

def login_kick(driver):
    """Inicia sesión en Kick de forma simple"""
    logging.info("[*] Iniciando sesión en Kick...")
    driver.get("https://kick.com/login")
    
    # Espera y completa el formulario de login
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
    ).send_keys(USERNAME)
    
    driver.find_element(By.CSS_SELECTOR, "input[name='password']").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    # Verifica que el login fue exitoso
    WebDriverWait(driver, 30).until(
        EC.url_contains("https://kick.com/dashboard")
    )
    logging.info("[+] Sesión iniciada correctamente")

def is_channel_live(driver):
    """Verifica si el canal está en vivo (simple y efectivo)"""
    driver.get(f"https://kick.com/{CHANNEL_NAME}")
    
    try:
        # Busca cualquier indicador de que el canal está en vivo
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.live-status, span.live, .channel-status, .live-badge"))
        )
        return True
    except:
        return False

def keep_channel_active(driver):
    """Mantiene la actividad para que tu extensión siga generando puntos"""
    # Simula actividad humana cada 30-60 segundos (ajustado para tu extensión)
    actions = ActionChains(driver)
    
    # Movimiento de ratón sutil
    actions.move_by_offset(random.randint(1, 5), random.randint(1, 5)).perform()
    time.sleep(0.5)
    actions.move_by_offset(-random.randint(1, 5), -random.randint(1, 5)).perform()
    
    # Pequeño scroll para mantener la página "activa"
    scroll_amount = random.randint(50, 150)
    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
    time.sleep(0.3)
    driver.execute_script(f"window.scrollBy(0, -{scroll_amount});")
    
    logging.info(f"[*] Manteniendo actividad en {CHANNEL_NAME} para generar puntos...")

def main():
    """Lógica principal del bot"""
    driver = None
    try:
        driver = setup_browser()
        login_kick(driver)
        
        logging.info(f"[*] Monitoreando canal '{CHANNEL_NAME}' (verificación cada {CHECK_INTERVAL} segundos)...")
        
        # Bucle principal
        while True:
            if is_channel_live(driver):
                logging.info(f"[+] ¡{CHANNEL_NAME} está EN VIVO! Generando puntos...")
                
                # Navega directamente al canal
                driver.get(f"https://kick.com/{CHANNEL_NAME}")
                time.sleep(5)  # Da tiempo a cargar
                
                # Mantiene actividad mientras el canal está en vivo
                while is_channel_live(driver):
                    keep_channel_active(driver)
                    time.sleep(random.randint(30, 60))  # Intervalo aleatorio para evitar detección
            else:
                logging.info(f"[ ] {CHANNEL_NAME} no está en vivo. Revisando en {CHECK_INTERVAL} segundos...")
                time.sleep(CHECK_INTERVAL)
                
    except Exception as e:
        logging.error(f"[!] Error: {str(e)}")
        if driver:
            driver.quit()
        # Reinicia el proceso
        time.sleep(30)
        main()

@app.route('/health')
def health_check():
    """Endpoint para UptimeRobot - mantiene el servicio despierto"""
    return {"status": "ok", "channel": CHANNEL_NAME}, 200

if __name__ == "__main__":
    # Inicia el bot en segundo plano
    from threading import Thread
    bot_thread = Thread(target=main, daemon=True)
    bot_thread.start()
    
    # Inicia el servidor Flask en el puerto asignado por Render.com
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

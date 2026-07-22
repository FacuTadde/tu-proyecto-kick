from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from threading import Thread
import os
import time
import logging
import signal
import sys

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
app = Flask(__name__)

# Variables de entorno
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
CHANNEL_NAME = os.getenv("CHANNEL_NAME", "forg1")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "120"))

# Manejador de señales para Render.com
def signal_handler(sig, frame):
    logging.info("[*] Señal recibida, limpiando y saliendo...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def setup_browser():
    """Configuración optimizada específicamente para Render.com"""
    chrome_options = Options()
    
    # Configuración esencial para Render.com
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
    
    # Carga tu extensión
    extension_path = os.path.abspath("./extension")
    chrome_options.add_argument(f"--load-extension={extension_path}")
    
    # Anti-detección mejorada (CRÍTICO para Render.com)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Evita que detecten headless (específico para Render)
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    # Configuración específica para entornos de Render
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-setuid-sandbox")
    
    return webdriver.Chrome(options=chrome_options)

def login_kick(driver):
    """Inicia sesión en Kick con tiempos reducidos y anti-detección mejorada"""
    logging.info("[*] Iniciando sesión en Kick...")
    driver.get("https://kick.com")
    
    # Tiempos reducidos para Render.com (evita "Application exited early")
    SHORT_TIMEOUT = 8
    LONG_TIMEOUT = 15
    
    try:
        # 1. Busca el botón "Log In" con tiempo reducido
        try:
            # Intenta encontrar el botón usando múltiples selectores
            login_button = WebDriverWait(driver, SHORT_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Log In')]"))
            )
            logging.info("[+] Botón 'Log In' encontrado")
        except:
            try:
                login_button = WebDriverWait(driver, SHORT_TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-test-id='login-button']"))
                )
                logging.info("[+] Botón 'Log In' encontrado (por data-test-id)")
            except Exception as e:
                logging.error(f"[!] Error: No se encontró el botón de login: {str(e)}")
                # Render necesita capturas específicas para diagnóstico
                driver.save_screenshot("no_login_button.png")
                raise TimeoutError("No login button found")
        
        # Hace clic en el botón de login
        driver.execute_script("arguments[0].click();", login_button)
        logging.info("[+] Modal de login abierto")
        
        # 2. Espera el formulario con tiempo reducido
        try:
            WebDriverWait(driver, SHORT_TIMEOUT).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.modal, form"))
            )
            logging.info("[+] Formulario de login cargado")
        except Exception as e:
            logging.error(f"[!] Error: No se cargó el formulario: {str(e)}")
            driver.save_screenshot("login_modal_error.png")
            raise TimeoutError("Login form not loaded")
        
        # 3. Completa los campos con tiempos reducidos
        try:
            # Campo de usuario
            username_field = WebDriverWait(driver, SHORT_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username'], input[placeholder*='User']"))
            )
            username_field.clear()
            username_field.send_keys(USERNAME)
            logging.info("[+] Usuario ingresado")
            time.sleep(0.5)
            
            # Campo de contraseña
            password_field = WebDriverWait(driver, SHORT_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password'], input[placeholder*='Pass']"))
            )
            password_field.clear()
            password_field.send_keys(PASSWORD)
            logging.info("[+] Contraseña ingresada")
            time.sleep(0.5)
            
            # Botón de submit
            submit_button = WebDriverWait(driver, SHORT_TIMEOUT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], button:contains('Log In')"))
            )
            driver.execute_script("arguments[0].click();", submit_button)
            logging.info("[+] Credenciales enviadas")
            
            # 4. Verifica login exitoso con tiempo reducido
            try:
                WebDriverWait(driver, LONG_TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.user-menu, span.user-name, img.avatar"))
                )
                logging.info("[+] Sesión iniciada correctamente")
                return True
            except:
                # Verifica si hay mensaje de error
                try:
                    error_msg = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.error, .toast-error"))
                    )
                    logging.error(f"[!] Error de login: {error_msg.text}")
                    driver.save_screenshot("login_error_message.png")
                    raise Exception(f"Login failed: {error_msg.text}")
                except:
                    logging.error("[!] Error: Login no completado (sin mensaje específico)")
                    driver.save_screenshot("login_unexpected.png")
                    raise Exception("Login process incomplete")
                    
        except Exception as e:
            logging.error(f"[!] Error durante el login: {str(e)}")
            driver.save_screenshot("login_process_error.png")
            raise
            
    except Exception as e:
        logging.error(f"[!!!] Fallo crítico en login: {str(e)}")
        # En Render.com, necesitamos reiniciar el servicio ante fallos
        os._exit(1)  # Reinicia el servicio (Render lo relanzará automáticamente)

def is_channel_live(driver):
    """Verifica si el canal está en vivo"""
    driver.get(f"https://kick.com/{CHANNEL_NAME}")
    
    try:
        # Busca cualquier indicador de que el canal está en vivo
        live_indicator = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.live-status, span.live, .channel-status, .live-badge"))
        )
        return True
    except:
        return False

def keep_page_active(driver):
    """Mantiene la actividad para que tu extensión siga generando puntos"""
    # Simula actividad humana cada 30-60 segundos (ajustado para tu extensión)
    actions = ActionChains(driver)
    
    # Movimiento de ratón sutil
    actions.move_by_offset(1, 1).perform()
    time.sleep(0.5)
    actions.move_by_offset(-1, -1).perform()
    
    # Pequeño scroll para mantener la página "activa"
    scroll_amount = 50
    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
    time.sleep(0.3)
    driver.execute_script(f"window.scrollBy(0, -{scroll_amount});")
    
    logging.info(f"[*] Manteniendo actividad en {CHANNEL_NAME} para generar puntos...")

def bot_logic():
    """Lógica principal del bot"""
    driver = None
    try:
        driver = setup_browser()
        if not login_kick(driver):
            logging.error("[!] Login fallido, reiniciando en 30 segundos...")
            time.sleep(30)
            return  # Esto hará que Render reinicie el servicio
            
        logging.info(f"[*] Monitoreando canal '{CHANNEL_NAME}' (verificación cada {CHECK_INTERVAL} segundos)...")
        
        # Bucle principal
        while True:
            if is_channel_live(driver):
                logging.info(f"[+] ¡{CHANNEL_NAME} está EN VIVO! Generando puntos...")
                
                # Navega directamente al canal
                driver.get(f"https://kick.com/{CHANNEL_NAME}")
                time.sleep(5)  # Da tiempo a cargar
                
                # Mantiene actividad mientras el canal está en vivo
                last_activity = time.time()
                while is_channel_live(driver):
                    # Mantén actividad cada 30-60 segundos
                    if time.time() - last_activity > 45:
                        keep_page_active(driver)
                        last_activity = time.time()
                    time.sleep(5)
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

def main():
    # Inicia el bot en segundo plano
    from threading import Thread
    bot_thread = Thread(target=bot_logic, daemon=True)
    bot_thread.start()
    
    # Inicia el servidor Flask en el puerto asignado por Render.com
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()

def login_kick(driver):
    """Inicia sesión en Kick usando el modal actual (funciona para 2026)"""
    logging.info("[*] Iniciando sesión en Kick...")
    driver.get("https://kick.com")
    
    # Espera a que cargue la página principal
    time.sleep(3)
    
    # 1. Busca y haz clic en el botón "Log In" (3 opciones posibles)
    login_button = None
    try:
        # Opción 1: Botón con texto "Log In"
        login_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log In')]"))
        )
    except:
        try:
            # Opción 2: Botón con clase común
            login_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test-id='login-button'], button.login-btn, button.btn-login"))
            )
        except:
            try:
                # Opción 3: En el header (si está en un contenedor)
                login_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "header button:contains('Log In')"))
                )
            except Exception as e:
                logging.error(f"[!] Error: No se encontró el botón de login: {str(e)}")
                driver.save_screenshot("no_login_button.png")
                raise
    
    # Hace clic en el botón de login
    driver.execute_script("arguments[0].scrollIntoView();", login_button)
    time.sleep(0.5)
    try:
        login_button.click()
    except:
        # Si el click normal falla, usa JavaScript
        driver.execute_script("arguments[0].click();", login_button)
    
    logging.info("[+] Modal de login abierto")
    
    # 2. Espera a que aparezca el modal de login
    try:
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.modal, div[role='dialog'], form.login-form"))
        )
        logging.info("[+] Formulario de login cargado")
    except Exception as e:
        logging.error(f"[!] Error: No se cargó el formulario de login: {str(e)}")
        driver.save_screenshot("login_modal_error.png")
        raise
    
    # 3. Completa los campos (con múltiples selectores para mayor compatibilidad)
    try:
        # Campo de usuario (3 opciones)
        username_field = None
        try:
            username_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username'], input[placeholder='Username'], input[data-test-id='username']"))
            )
        except:
            try:
                username_field = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Username')]"))
                )
            except Exception as e:
                logging.error(f"[!] Error: No se encontró el campo de usuario: {str(e)}")
                driver.save_screenshot("no_username_field.png")
                raise
        
        username_field.clear()
        username_field.send_keys(USERNAME)
        logging.info("[+] Usuario ingresado")
        time.sleep(1)
        
        # Campo de contraseña (3 opciones)
        password_field = None
        try:
            password_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password'], input[placeholder='Password'], input[data-test-id='password']"))
            )
        except:
            try:
                password_field = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Password')]"))
                )
            except Exception as e:
                logging.error(f"[!] Error: No se encontró el campo de contraseña: {str(e)}")
                driver.save_screenshot("no_password_field.png")
                raise
        
        password_field.clear()
        password_field.send_keys(PASSWORD)
        logging.info("[+] Contraseña ingresada")
        time.sleep(1)
        
        # Botón de submit (3 opciones)
        submit_button = None
        try:
            submit_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], button.login-submit, button[data-test-id='login-submit']"))
            )
        except:
            try:
                submit_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log In') or contains(., 'Sign In')]"))
                )
            except Exception as e:
                logging.error(f"[!] Error: No se encontró el botón de submit: {str(e)}")
                driver.save_screenshot("no_submit_button.png")
                raise
        
        # Hace clic en el botón de submit
        driver.execute_script("arguments[0].scrollIntoView();", submit_button)
        time.sleep(0.5)
        try:
            submit_button.click()
        except:
            driver.execute_script("arguments[0].click();", submit_button)
        
        logging.info("[+] Credenciales enviadas")
        
        # 4. Verifica que el login fue exitoso (espera por elementos del dashboard)
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.user-menu, span.user-name, img.user-avatar"))
            )
            logging.info("[+] Sesión iniciada correctamente")
        except:
            # Verifica si hay un mensaje de error
            try:
                error_message = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.error-message, .error-text, .toast-error"))
                )
                logging.error(f"[!] Error de login: {error_message.text}")
                driver.save_screenshot("login_error_message.png")
                raise Exception(f"Login failed: {error_message.text}")
            except:
                logging.error("[!] Error: No se completó el login (sin mensaje de error específico)")
                driver.save_screenshot("login_unexpected.png")
                raise
    
    except Exception as e:
        logging.error(f"[!] Error durante el login: {str(e)}")
        driver.save_screenshot("login_process_error.png")
        raise

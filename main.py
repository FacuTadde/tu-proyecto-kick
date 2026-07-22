def login_kick(driver):
    """Inicia sesión en Kick usando el modal actual"""
    logging.info("[*] Iniciando sesión en Kick...")
    driver.get("https://kick.com")
    
    # Espera a que cargue la página principal
    time.sleep(2)
    
    # 1. Haz clic en el botón "Log In" (ajusta el selector según la estructura actual)
    try:
        # Opción 1: Busca por texto
        login_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log In')]"))
        )
        login_button.click()
        logging.info("[+] Modal de login abierto")
    except:
        try:
            # Opción 2: Busca por clase común
            login_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.login-button, button[data-test-id='login-button']"))
            )
            login_button.click()
            logging.info("[+] Modal de login abierto")
        except Exception as e:
            logging.error(f"[!] Error al abrir modal de login: {str(e)}")
            raise
    
    # 2. Espera a que aparezca el modal de login
    try:
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.modal-content, form.login-form"))
        )
        logging.info("[+] Formulario de login cargado")
    except Exception as e:
        logging.error(f"[!] Error: No se cargó el formulario de login: {str(e)}")
        # Captura screenshot para diagnóstico
        driver.save_screenshot("login_error.png")
        raise
    
    # 3. Completa los campos (ajusta los selectores)
    try:
        # Campo de usuario
        username_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username'], input[placeholder='Username'], input[data-test-id='username']"))
        )
        username_field.clear()
        username_field.send_keys(USERNAME)
        
        # Campo de contraseña
        password_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password'], input[placeholder='Password'], input[data-test-id='password']"))
        )
        password_field.clear()
        password_field.send_keys(PASSWORD)
        
        # Botón de submit
        submit_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], button.login-submit"))
        )
        submit_button.click()
        
        logging.info("[+] Credenciales enviadas")
        
        # 4. Verifica que el login fue exitoso
        WebDriverWait(driver, 30).until(
            EC.url_contains("https://kick.com/dashboard") or 
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.user-avatar, span.user-name"))
        )
        logging.info("[+] Sesión iniciada correctamente")
        
    except Exception as e:
        logging.error(f"[!] Error durante el login: {str(e)}")
        driver.save_screenshot("login_process_error.png")
        raise

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import threading
import os
import sys
import logging
import time


class SifamaLogin:
    def __init__(self, chromedriver_path, saved_user=None, saved_password=None):
        if not os.path.isfile(chromedriver_path):
            logging.error(f"Chromedriver não encontrado: {chromedriver_path}")
            raise FileNotFoundError("Chromedriver não encontrado.")
        
        # Configurações do ChromeDriver
        download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "download_extrato")

        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")  # Modo headless maximized

        # Inicializa o ChromeDriver com logs detalhados
        service = Service(chromedriver_path)
        try:
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            logging.error(f"Erro ao inicializar o ChromeDriver: {e}")
            raise
        self.driver.set_page_load_timeout(600)

        self.root = tk.Tk()
        self.root.withdraw()

        self.saved_user = saved_user
        self.saved_password = saved_password

    def parcelamento_div(self):
        WebDriverWait(self.driver, 360).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="parcelamento"]'))
        )
    def progress_div(self):
        WebDriverWait(self.driver, 260).until(
            EC.invisibility_of_element_located((By.XPATH, '//*[@id="Progress_UpdateProgress"]/div'))
        )

    # Função para realizar login no sistema SIFAMA
    def login_action(self, user=None, password=None):
        try:
            # Usa os valores salvos, se nenhum novo valor for fornecido
            user = user or self.saved_user
            password = password or self.saved_password

            # Valida se as credenciais estão disponíveis momentaniamente
            if not user or not password:
                logging.error("Usuário ou senha não fornecidos.")
                return False

            # Salva os valores fornecidos para reutilização futura
            self.saved_user = user
            self.saved_password = password

            # Localiza os campos de entrada
            user_field = self.driver.find_element(By.CSS_SELECTOR, '*[id*="TextBoxUsuario"]')
            password_field = self.driver.find_element(By.CSS_SELECTOR, '*[id*="TextBoxSenha"]')
            login_button = self.driver.find_element(By.CSS_SELECTOR, '*[id*="ButtonOk"]')

            # Preenche os campos de entrada
            user_field.send_keys(user)
            password_field.send_keys(password)
            login_button.click()

            return True
        except Exception as e:
            logging.error(f"Erro durante a execução de login_action: {e}")
            return False

    def bem_vindo(self):
        WebDriverWait(self.driver, 120).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="ContentPlaceHolderCorpo_LabelBemVindo"]'))
        )

    def erro_sistema(self):
            return "Exceção de Sistema" in self.driver.page_source

    def erro_servidor(self):
            return "Server Error in '/sar' Application" in self.driver.page_source

    def recarregar_erro(self, sifama_site):

        if self.erro_sistema() or self.erro_servidor():
            logging.warning("Erro no sistema detectado. Recarregando a página.")
            self.driver.delete_network_conditions()
            self.driver.delete_all_cookies()
            self.driver.refresh()
            WebDriverWait(self.driver, 30).until(
                 EC._element_if_visible((By.CSS_SELECTOR, '*[id*="TextBoxUsuario"]'))
            )
            self.driver.get(sifama_site)
            self.login_action()
                
            logging.info("Página recarregada com sucesso.")
            time.sleep(3)  # Pequeno atraso entre as tentativas
            return
        else:
            return

    def reiniciar_selenium(self, chromedriver_path, sifama_site):
        try:
            self.driver.quit()
            logging.info("Driver fechado com sucesso.")
        except Exception as e:
            logging.warning(f"Erro ao fechar o driver: {e}")
        finally:
            time.sleep(2)
            novo_sifama = SifamaLogin(chromedriver_path, saved_user=self.saved_user, saved_password=self.saved_password)
            novo_sifama.driver.get(sifama_site)
            time.sleep(2)
            novo_sifama.login_action(novo_sifama.saved_user, novo_sifama.saved_password)
            novo_sifama.bem_vindo()
            return novo_sifama

    def login(self, user, password):
        user_field = self.driver.find_element(By.CSS_SELECTOR, '*[id*="TextBoxUsuario"]')
        password_field = self.driver.find_element(By.CSS_SELECTOR, '*[id*="TextBoxSenha"]')
        logging.info('Acessando o SIFAMA')   
        logging.info("------------------------------------------------")
        try:
            self.login_action(user, password)  # Chama o método login_action
            # Aguarda a página carregar e verifica se o login foi bem-sucedido
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ContentPlaceHolderCorpo_LabelBemVindo"))
            )
            self.root.after(0, lambda: messagebox.showinfo("Sucesso", "Login efetuado com sucesso!"))
            return True

        except TimeoutException:
            # Caso o elemento de sucesso não seja encontrado, verifica a mensagem de erro
            try:
                error_message_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "MessageBox_LabelMensagem"))
                )
                error_message = error_message_element.text
                logging.info(f"Mensagem de erro: {error_message}")
                self.root.after(0, lambda: messagebox.showwarning("Aviso", error_message))
                try:
                    ok_button = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'MessageBox_ButtonOk'))
                    )
                    ok_button.click()
                    logging.info("Botão ok selecionado com sucesso")
                except TimeoutException:
                    logging.error("Botão não encontrado dentro do tempo")

                user_field.clear()
                password_field.clear()

            except TimeoutException:
                logging.info("Nenhuma mensagem de erro encontrada.")
            return False
        except Exception as e:
            logging.error(f"Erro durante o login: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erro", "Erro inesperado durante o login."))
            return False
      
    def prompt_window(self):
        prompt_window = tk.Toplevel(self.root)
        prompt_window.title("Log de Execução")

        prompt_window.configure(bg="white")

        output_text = scrolledtext.ScrolledText(
            prompt_window,
            height=30,
            width=130,
            bg="lightgray",
            fg="black",
            font=("Arial",12),
            insertbackground="white",
        )
        output_text.grid(row=0, column=0, padx=10, pady=10)

        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            def emit(self, record):
                log_entry = self.format(record)
                self.text_widget.insert(tk.END, log_entry + "\n")
                self.text_widget.see(tk.END)
        
        text_handler = TextHandler(output_text)
        text_handler.setFormatter(logging.Formatter("%(message)s"))
        logging.getLogger().addHandler(text_handler)

        # Botão para fechar a janela
        close_button = tk.Button(
            prompt_window,
            text="Fechar",
            command=lambda: (sys.exit()),
            font=("Arial", 10),
            bg="#800000",
            fg="#FFC0CB",
            )
        close_button.grid(row=1, column=0, pady=10)

    def login_window(self):
        # Criação da interface gráfica para entrada de login e senha
        login_window = tk.Toplevel(self.root)
        login_window.title("Login SIFAMA")
        login_window.geometry("250x125")
        login_window.resizable(False, False)

        # Labels e campos de entrada de Usuario
        tk.Label(login_window, text="Usuário:", font=("Arial", 10)).grid(row=0, column=0, padx=20, pady=10)
        login_entry = tk.Entry(login_window, bg="#DCDCDC")
        login_entry.grid(row=0, column=1, padx=5, pady=10)

        # Campo de entrada de Senha
        tk.Label(login_window, text="Senha:", font=("Arial", 10)).grid(row=1, column=0, padx=20, pady=10)
        password_entry = tk.Entry(login_window, bg="#DCDCDC", show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=10)
        password_entry.bind("<Return>", lambda event: login_submit())

        # Variável para armazenar o frame de sobreposição
        overlay_frame = None
        spinner_canvas = None
        arc = None

        def animate_spinner(angle=0):
            if spinner_canvas and arc and spinner_canvas.winfo_exists():  # Verifica se o spinner_canvas e o arco foram criados
                spinner_canvas.itemconfig(arc, start=angle)
                spinner_canvas.update()
                self.spinner_animation = login_window.after(50, animate_spinner, (angle + 10) % 360)

        def show_spinner():
            nonlocal overlay_frame, spinner_canvas, arc  # Declara as variáveis como não locais
            if overlay_frame is not None:
                overlay_frame.destroy()  # Remove o frame anterior, se existir

            overlay_frame = tk.Frame(login_window)
            overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)  # Ocupa toda a janela
            overlay_frame.grid_propagate(False)

            # Conteúdo do overlay (spinner e mensagem)
            spinner_canvas = tk.Canvas(overlay_frame, width=100, height=100, highlightthickness=0)
            spinner_canvas.place(relx=0.5, rely=0.4, anchor="center")  # Centraliza o spinner
            arc = spinner_canvas.create_arc(10, 10, 90, 90, start=0, extent=150, outline="#4682B4", width=5, style="arc")
            animate_spinner()

        def hide_spinner():
            nonlocal overlay_frame  # Permite acessar a variável overlay_frame
            if overlay_frame is not None:
                overlay_frame.destroy()  # Remove o frame de sobreposição
            if hasattr(self, 'spinner_animation'):
                login_window.after_cancel(self.spinner_animation)

        def login_submit():
            user = login_entry.get()
            password = password_entry.get()
            if user and password:
                show_spinner()
                threading.Thread(target=process_login, args=(user, password)).start()
            else:
                messagebox.showwarning("Aviso", "Por favor, preencha todos os campos")

        def process_login(user, password):
            if self.login(user, password):
                login_window.destroy()
            else:
                login_entry.delete(0, tk.END)
                password_entry.delete(0, tk.END)
            hide_spinner()

        # Botão de envio
        submit_button = tk.Button(
            login_window,
            text="Entrar",
            font=("Arial", 10),
            bg="#90EE90",
            fg="#006400",
            command=login_submit)
        submit_button.grid(row=2, column=1, pady=10)

        # Botão para fechar a janela
        close_button = tk.Button(
            login_window,
            text="Cancelar",
            command=lambda: (sys.exit()),
            font=("Arial", 9),
            bg="#800000",
            fg="#FFC0CB"
            )
        close_button.grid(row=2, column=0, columnspan=1, pady=10)
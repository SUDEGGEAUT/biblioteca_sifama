from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
import selenium.webdriver.common.keys as Keys
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import threading
import os
import sys
import logging

class SifamaLogin:
    def __init__(self, chromedriver_path):
        if not os.path.isfile(chromedriver_path):
            logging.error(f"Chromedriver não encontrado: {chromedriver_path}")
            raise FileNotFoundError("Chromedriver não encontrado.")
        
        site_sifama = r'https://appweb1.antt.gov.br/sca/Site/Login.aspx?ReturnUrl=%2fsar%2fSite'
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service(chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        #self.driver.get(site_sifama)
       
        self.root = tk.Tk()
        self.root.withdraw()
        
    # Função para realizar login no sistema SIFAMA
    def login(self, user, password):
        logging.info('Acessando o SIFAMA')
        try:
            # Localiza os campos de usuário e senha
            user_field = self.driver.find_element(By.CSS_SELECTOR, '*[id*="TextBoxUsuario"]')
            password_field = self.driver.find_element(By.CSS_SELECTOR, '*[id*="TextBoxSenha"]')
            login_button = self.driver.find_element(By.CSS_SELECTOR, '*[id*="ButtonOk"]')

            # Preenche os campos e clica no botão de login
            user_field.send_keys(user)
            password_field.send_keys(password)
            login_button.click()

            # Aguarda a página carregar e verifica se o login foi bem-sucedido
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ContentPlaceHolderCorpo_LabelBemVindo"))
            )
            messagebox.showinfo("Sucesso", "Login efetuado com sucesso!")
            return True
        except TimeoutException:
            # Caso o elemento de sucesso não seja encontrado, verifica a mensagem de erro
            try:
                error_message_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "MessageBox_LabelMensagem"))
                )
                error_message = error_message_element.text
                logging.info(f"Mensagem de erro: {error_message}")
                messagebox.showwarning("Aviso", error_message)
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
            messagebox.showerror("Erro", "Erro inesperado durante o login.")
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
            command=lambda: (self.driver.quit(), prompt_window.destroy(), sys.exit()),
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
            command=lambda: (self.driver.quit(), sys.exit()),
            font=("Arial", 9),
            bg="#800000",
            fg="#FFC0CB"
            )
        close_button.grid(row=2, column=0, columnspan=1, pady=10)

if __name__ == "__main__":
    # O caminho do arquivo que você quer enviar
    atual_dir = os.path.dirname(os.path.abspath(__file__))
    chromedriver_path = os.path.join(atual_dir, "chromedriver-win64", "chromedriver.exe")
    
    sifama = SifamaLogin(chromedriver_path)
    sifama.login_window()
    sifama.prompt_window()
    sifama.root.mainloop()
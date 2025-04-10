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
        self.driver.get(site_sifama)
       
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

        prompt_window.configure(bg="lightgray")

        output_text = scrolledtext.ScrolledText(
            prompt_window,
            height=30,
            width=130,
            bg="lightgray",
            fg="black",
            insertbackground="white",
            font=("Courier", 10)
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
            command=lambda: (prompt_window.destroy(), self.driver.quit(), sys.exit()),
            bg="red",
            fg="white"
            )
        close_button.grid(row=1, column=0, pady=10)

    def login_window(self):
        # Criação da interface gráfica para entrada de login e senha
        login_window = tk.Toplevel(self.root)
        login_window.title("Login SIFAMA")

        # Labels e campos de entrada
        tk.Label(login_window, text="Usuário:").grid(row=0, column=0, padx=20, pady=10)
        login_entry = tk.Entry(login_window)
        login_entry.grid(row=0, column=1, padx=40, pady=10)

        tk.Label(login_window, text="Senha:").grid(row=1, column=0, padx=20, pady=10)
        password_entry = tk.Entry(login_window, show="*")
        password_entry.grid(row=1, column=1, padx=40, pady=10)

        def login_submit():
            user = login_entry.get()
            password = password_entry.get()

            if user and password:
                if self.login(user, password):
                    login_window.destroy()
                else:
                    login_entry.delete(0, tk.END)
                    password_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Aviso", "Por favor, preencha todos os campos")

        # Botão de envio
        submit_button = tk.Button(login_window, text="Entrar", command=login_submit)
        submit_button.grid(row=2, column=0, columnspan=2, pady=10)


if __name__ == "__main__":
    # O caminho do arquivo que você quer enviar
    atual_dir = os.path.dirname(os.path.abspath(__file__))
    chromedriver_path = os.path.join(atual_dir, "chromedriver-win64", "chromedriver.exe")
    
    sifama = SifamaLogin(chromedriver_path)
    sifama.login_window()
    sifama.prompt_window()
    sifama.root.mainloop()
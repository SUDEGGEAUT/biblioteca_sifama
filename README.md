# **SIFAMA Login Automation**

## **Descrição**

`Este projeto automatiza o processo de login no sistema SIFAMA da ANTT utilizando o Selenium WebDriver e Tkinter para a interface gráfica. Ele permite realizar login de forma automatizada e exibir logs detalhados da execução, além de fornecer uma janela gráfica para o usuário inserir o nome de usuário e senha.`

## **Funcionalidades**

- **Login automatizado no SIFAMA**: `Realiza login utilizando o usuário e senha fornecidos.`

- **Interface gráfica**:` A interface gráfica foi construída com Tkinter e permite a entrada de dados como nome de usuário e senha.`

- **Logs em tempo real**: `Registra o progresso do login em uma janela de logs, exibindo mensagens de sucesso e erro.`

- **Mensagens de erro detalhadas**: Caso o login falhe, o erro será mostrado em uma janela pop-up.

- **Modo headless**: A aplicação pode ser executada sem abrir o navegador visivelmente, otimizando o desempenho.

## Requisitos

- **Python 3.x**

- **Selenium** (instalado via pip)

- **Tkinter** (vem com a instalação padrão do Python)

- **Chrome WebDriver** (compartilhar o caminho do driver para o navegador Chrome)

### Instalação dos pacotes necessários

1. Instalar o `Selenium`:

$`bash`$

`Copiar`

`pip install selenium`

2. Baixar o **ChromeDriver** para sua versão do navegador aqui e extraí-lo para a pasta do seu projeto.

## Uso

1. **Configuração**: Antes de executar, certifique-se de ter o **ChromeDriver** instalado e o caminho configurado corretamente no código, ajustando o parâmetro `chromedriver_path`.

2. **Execução**: Para rodar o programa, basta executar o script:

bash

Copiar

`python sifama_login.py`

3. **Login**: Após iniciar o programa, uma janela de login aparecerá. Insira seu nome de usuário e senha para realizar o login.

4. **Janela de Logs**: Uma janela adicional será aberta mostrando os logs da execução, com mensagens sobre o processo de login, como "Sucesso", "Aviso" e "Erro".

## Estrutura do Código

- **`SifamaLogin`**: Classe principal que gerencia o processo de login e a interface gráfica.

- **Função `login`**: Função que realiza a automação do login e lida com erros de forma adequada.

- **Função `login_window`**: Exibe a janela para a entrada de dados de login e senha.

- **Função `prompt_window`**: Exibe a janela de logs para visualização da execução.

## Contribuição

1. Faça o fork do repositório.

2. Crie uma branch para a sua modificação (`git checkout -b feature/nova-funcionalidade`).

3. Faça o commit das suas alterações (`git commit -am 'Adicionando nova funcionalidade'`).

4. Envie para o repositório remoto (`git push origin feature/nova-funcionalidade`).

5. Abra um pull request para a branch principal.

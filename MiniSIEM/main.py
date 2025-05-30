# Importa o CustomTkinter para UI moderna e o filedialog para selecionar arquivos
import customtkinter as ctk
from tkinter import filedialog
import time
import threading
from collections import defaultdict

# Número de tentativas de login falhas antes de gerar um alerta
FAILED_THRESHOLD = 3

# Classe principal da aplicação SIEM baseada em interface gráfica
class SIEMApp(ctk.CTk):

    # Função para limpar o conteúdo da caixa de texto
    def clear_log(self):
        self.log_box.delete("1.0", "end")

    # Construtor da aplicação
    def __init__(self):
        super().__init__()
        self.title("Mini SIEM - Python")         # Título da janela
        self.geometry("800x500")                # Tamanho da janela
        self.configure(bg_color="#1a1a2e")      # Cor de fundo personalizada

        ctk.set_appearance_mode("dark")         # Define o tema escuro

        # Caixa de texto para exibir os logs
        self.log_box = ctk.CTkTextbox(self, width=750, height=400)
        self.log_box.pack(pady=20)

        # Botão para selecionar o arquivo de log
        self.button = ctk.CTkButton(self, text="Selecionar Log", command=self.select_file)
        self.button.pack()

        # Botão para limpar a tela
        self.clear_button = ctk.CTkButton(self, text="Limpar Tela", command=self.clear_log)
        self.clear_button.pack(pady=10)

        # Dicionário para contar tentativas de login falhas por usuário
        self.failed_attempts = defaultdict(int)

    # Função chamada ao clicar em "Selecionar Log"
    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            # Cria uma thread para monitorar o log sem travar a interface
            threading.Thread(target=self.monitor_log, args=(file_path,), daemon=True).start()

    # Lógica para detectar ameaças (múltiplas falhas de login)
    def detect_threat(self, line):
        if "LOGIN FAILED" in line:
            user = line.split("user: ")[-1].strip()
            self.failed_attempts[user] += 1
            if self.failed_attempts[user] >= FAILED_THRESHOLD:
                return True, user
        elif "LOGIN SUCCESS" in line:
            # Reset das falhas se o login for bem-sucedido
            user = line.split("user: ")[-1].strip()
            self.failed_attempts[user] = 0
        return False, None

    # Função que monitora o arquivo de log em tempo real
    def monitor_log(self, path):
        with open(path, "r") as f:
            f.seek(0)  # Garante que começamos do início do arquivo
            while True:
                line = f.readline()
                if line:
                    # Verifica se a linha representa uma ameaça
                    threat, user = self.detect_threat(line)
                    if threat:
                        self.log_box.insert("end", f"[ALERTA] Múltiplas falhas de login para {user}\n", "alerta")
                    else:
                        self.log_box.insert("end", line)
                    self.log_box.see("end")  # Rola automaticamente para a última linha
                time.sleep(0.5)  # Espera antes de verificar a próxima linha

        # Define o estilo das mensagens de alerta
        self.log_box.tag_config("alerta", foreground="red", font=("Arial", 12, "bold"))

# Ponto de entrada da aplicação
if __name__ == "__main__":
    app = SIEMApp()
    app.mainloop()

  
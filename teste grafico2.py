import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Função para criar o banco de dados e as tabelas
def criar_banco():
    conn = sqlite3.connect('ubs.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS ubs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        valor_federal REAL NOT NULL,
                        valor_estadual REAL NOT NULL,
                        valor_municipal REAL NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS despesas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ubs_id INTEGER NOT NULL,
                        descricao TEXT NOT NULL,
                        valor REAL NOT NULL,
                        FOREIGN KEY (ubs_id) REFERENCES ubs(id))''')

    conn.commit()
    conn.close()

# Função para cadastrar uma nova UBS
def cadastrar_ubs(nome, valor_federal, valor_estadual, valor_municipal):
    conn = sqlite3.connect('ubs.db')
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO ubs (nome, valor_federal, valor_estadual, valor_municipal)
                      VALUES (?, ?, ?, ?)''', (nome, valor_federal, valor_estadual, valor_municipal))

    conn.commit()
    conn.close()

# Função para registrar uma despesa para uma UBS específica
def registrar_despesa(ubs_id, descricao, valor):
    conn = sqlite3.connect('ubs.db')
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO despesas (ubs_id, descricao, valor)
                      VALUES (?, ?, ?)''', (ubs_id, descricao, valor))

    conn.commit()
    conn.close()

# Função para gerar o gráfico de uma UBS específica
def gerar_relatorio_ubs(ubs_id, canvas):
    conn = sqlite3.connect('ubs.db')
    cursor = conn.cursor()

    cursor.execute('SELECT nome, valor_federal, valor_estadual, valor_municipal FROM ubs WHERE id = ?', (ubs_id,))
    ubs = cursor.fetchone()

    if ubs is None:
        messagebox.showerror("Erro", "UBS não encontrada.")
        return None

    nome, valor_federal, valor_estadual, valor_municipal = ubs

    cursor.execute('SELECT valor FROM despesas WHERE ubs_id = ?', (ubs_id,))
    despesas = cursor.fetchall()

    conn.close()

    total_despesas = sum(d[0] for d in despesas) if despesas else 0

    # Valores para o gráfico
    receitas = [valor_federal, valor_estadual, valor_municipal, total_despesas]
    labels = ['Federal', 'Estadual', 'Municipal', 'Despesas']

    # Limpa o canvas
    canvas.delete("all")

    # Desenha o gráfico
    largura = 500
    altura = 400
    x_inicial = 50
    largura_barra = 80
    max_valor = max(receitas) if receitas else 1

    for i, (valor, label) in enumerate(zip(receitas, labels)):
        altura_barra = (valor / max_valor) * (altura - 20)  # Normaliza a altura da barra
        x = x_inicial + i * (largura_barra + 20)
        y = altura - altura_barra

        # Desenha a barra
        color = "#4CAF50" if label != "Despesas" else "#FF9800"  # Verde para receitas, laranja para despesas
        canvas.create_rectangle(x, y, x + largura_barra, altura, fill=color)  
        canvas.create_text(x + largura_barra / 2, altura + 10, text=label, fill="#2E7D32")  

# Função para gerar um gráfico geral de todas as UBS
def gerar_relatorio_geral(canvas):
    conn = sqlite3.connect('ubs.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, nome, valor_federal, valor_estadual, valor_municipal FROM ubs')
    ubs_list = cursor.fetchall()

    conn.close()

    if not ubs_list:
        messagebox.showinfo("Info", "Nenhuma UBS cadastrada.")
        return None

    # Limpa o canvas
    canvas.delete("all")
    
    largura = 600
    altura = 400
    y_inicial = 50
    largura_barra = 20
    max_valor = 0

    # Calcula o total para normalização
    totals = {}
    for ubs in ubs_list:
        ubs_id, nome, valor_federal, valor_estadual, valor_municipal = ubs

        conn = sqlite3.connect('ubs.db')
        cursor = conn.cursor()
        cursor.execute('SELECT valor FROM despesas WHERE ubs_id = ?', (ubs_id,))
        despesas = cursor.fetchall()
        conn.close()

        total_despesas = sum(d[0] for d in despesas) if despesas else 0

        total = valor_federal + valor_estadual + valor_municipal + total_despesas
        totals[nome] = total
        max_valor = max(max_valor, total)

    # Estilos de cores
    colors = ["#4CAF50", "#2196F3", "#FF9800", "#F44336", "#9C27B0", "#3F51B5", "#FFEB3B"]

    # Desenha o gráfico
    for i, (nome, total) in enumerate(totals.items()):
        largura_barra_atual = (total / max_valor) * (largura - 100)  # Normaliza a largura da barra
        y = y_inicial + i * (largura_barra + 30)

        # Desenha a barra horizontal com bordas
        canvas.create_rectangle(50, y, 50 + largura_barra_atual, y + largura_barra, fill=colors[i % len(colors)], outline="black", width=1)

        # Adiciona rótulo ao lado da barra
        canvas.create_text(50 + largura_barra_atual + 10, y + largura_barra / 2, text=f"{total:.2f}", fill="black", font=("Arial", 10, "bold"))

    # Desenha o eixo X
    canvas.create_line(50, altura - 20, largura + 50, altura - 20)
    canvas.create_text(largura + 70, altura - 20, text="Total", font=("Arial", 10, "bold"))

    # Desenha o eixo Y
    canvas.create_line(50, y_inicial, 50, altura - 20)

    # Adiciona rótulos ao eixo Y
    for i, nome in enumerate(totals.keys()):
        y = y_inicial + i * (largura_barra + 30) + largura_barra / 2
        canvas.create_text(20, y, text=nome, anchor="e", font=("Arial", 10))

    # Adiciona título ao gráfico
    canvas.create_text(largura / 2 + 50, 20, text="Relatório Geral de UBS", font=("Arial", 16, "bold"), fill="#333")

    # Adiciona legenda
    for i, (nome, color) in enumerate(zip(totals.keys(), colors)):
        canvas.create_rectangle(10, 10 + i * 30, 30, 30 + i * 30, fill=color)
        canvas.create_text(40, 20 + i * 30, text=nome, anchor="w", font=("Arial", 10))

# Interface gráfica usando Tkinter
class UBSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gerenciamento de UBS")
        self.root.geometry("800x600")  # Aumentando a janela

        # Cores da interface
        self.root.configure(bg="#E3F2FD")  # Azul claro

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True)

        self.frame_cadastro = ttk.Frame(self.notebook, width=800, height=400, relief="sunken", borderwidth=2)
        self.frame_despesa = ttk.Frame(self.notebook, width=800, height=400, relief="sunken", borderwidth=2)
        self.frame_relatorio_ubs = ttk.Frame(self.notebook, width=800, height=400, relief="sunken", borderwidth=2)
        self.frame_relatorio_geral = ttk.Frame(self.notebook, width=800, height=400, relief="sunken", borderwidth=2)

        self.frame_cadastro.pack(fill="both", expand=True)
        self.frame_despesa.pack(fill="both", expand=True)
        self.frame_relatorio_ubs.pack(fill="both", expand=True)
        self.frame_relatorio_geral.pack(fill="both", expand=True)

        self.notebook.add(self.frame_cadastro, text="Cadastrar UBS")
        self.notebook.add(self.frame_despesa, text="Registrar Despesa")
        self.notebook.add(self.frame_relatorio_ubs, text="Relatório de UBS")
        self.notebook.add(self.frame_relatorio_geral, text="Relatório Geral")

        # Componentes do Frame de Cadastro
        self.label_nome = tk.Label(self.frame_cadastro, text="Nome da UBS:", bg="#E3F2FD")
        self.label_nome.pack(pady=5)

        self.entry_nome = tk.Entry(self.frame_cadastro)
        self.entry_nome.pack(pady=5)

        self.label_valor_federal = tk.Label(self.frame_cadastro, text="Valor Federal:", bg="#E3F2FD")
        self.label_valor_federal.pack(pady=5)

        self.entry_valor_federal = tk.Entry(self.frame_cadastro)
        self.entry_valor_federal.pack(pady=5)

        self.label_valor_estadual = tk.Label(self.frame_cadastro, text="Valor Estadual:", bg="#E3F2FD")
        self.label_valor_estadual.pack(pady=5)

        self.entry_valor_estadual = tk.Entry(self.frame_cadastro)
        self.entry_valor_estadual.pack(pady=5)

        self.label_valor_municipal = tk.Label(self.frame_cadastro, text="Valor Municipal:", bg="#E3F2FD")
        self.label_valor_municipal.pack(pady=5)

        self.entry_valor_municipal = tk.Entry(self.frame_cadastro)
        self.entry_valor_municipal.pack(pady=5)

        self.button_cadastrar = tk.Button(self.frame_cadastro, text="Cadastrar", command=self.cadastrar)
        self.button_cadastrar.pack(pady=10)

        # Componentes do Frame de Despesas
        self.label_ubs_id = tk.Label(self.frame_despesa, text="ID da UBS:", bg="#E3F2FD")
        self.label_ubs_id.pack(pady=5)

        self.entry_ubs_id = tk.Entry(self.frame_despesa)
        self.entry_ubs_id.pack(pady=5)

        self.label_descricao = tk.Label(self.frame_despesa, text="Descrição da Despesa:", bg="#E3F2FD")
        self.label_descricao.pack(pady=5)

        self.entry_descricao = tk.Entry(self.frame_despesa)
        self.entry_descricao.pack(pady=5)

        self.label_valor = tk.Label(self.frame_despesa, text="Valor:", bg="#E3F2FD")
        self.label_valor.pack(pady=5)

        self.entry_valor = tk.Entry(self.frame_despesa)
        self.entry_valor.pack(pady=5)

        self.button_registrar = tk.Button(self.frame_despesa, text="Registrar Despesa", command=self.registrar_despesa)
        self.button_registrar.pack(pady=10)

        # Componentes do Frame de Relatório de UBS
        self.label_selecionar_ubs = tk.Label(self.frame_relatorio_ubs, text="Selecione o ID da UBS para gerar o relatório:", bg="#E3F2FD")
        self.label_selecionar_ubs.pack(pady=5)

        self.entry_selecionar_ubs = tk.Entry(self.frame_relatorio_ubs)
        self.entry_selecionar_ubs.pack(pady=5)

        self.button_gerar_relatorio_ubs = tk.Button(self.frame_relatorio_ubs, text="Gerar Relatório", command=lambda: self.gerar_relatorio_ubs())
        self.button_gerar_relatorio_ubs.pack(pady=10)

        self.canvas_ubs = tk.Canvas(self.frame_relatorio_ubs, width=500, height=400, bg="#FFFFFF")
        self.canvas_ubs.pack(pady=10)

        # Componentes do Frame de Relatório Geral
        self.button_gerar_relatorio_geral = tk.Button(self.frame_relatorio_geral, text="Gerar Relatório Geral", command=self.gerar_relatorio_geral)
        self.button_gerar_relatorio_geral.pack(pady=10)

        self.canvas_geral = tk.Canvas(self.frame_relatorio_geral, width=600, height=400, bg="#FFFFFF")
        self.canvas_geral.pack(pady=10)

        criar_banco()

    def cadastrar(self):
        nome = self.entry_nome.get()
        valor_federal = float(self.entry_valor_federal.get())
        valor_estadual = float(self.entry_valor_estadual.get())
        valor_municipal = float(self.entry_valor_municipal.get())

        cadastrar_ubs(nome, valor_federal, valor_estadual, valor_municipal)
        messagebox.showinfo("Sucesso", "UBS cadastrada com sucesso!")

    def registrar_despesa(self):
        ubs_id = int(self.entry_ubs_id.get())
        descricao = self.entry_descricao.get()
        valor = float(self.entry_valor.get())

        registrar_despesa(ubs_id, descricao, valor)
        messagebox.showinfo("Sucesso", "Despesa registrada com sucesso!")

    def gerar_relatorio_ubs(self):
        ubs_id = int(self.entry_selecionar_ubs.get())
        gerar_relatorio_ubs(ubs_id, self.canvas_ubs)

    def gerar_relatorio_geral(self):
        gerar_relatorio_geral(self.canvas_geral)

if __name__ == "__main__":
    root = tk.Tk()
    app = UBSApp(root)
    root.mainloop()

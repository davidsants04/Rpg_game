import tkinter as tk
from tkinter import scrolledtext, messagebox, font, Toplevel, Label, Button, Frame, Listbox, Scrollbar, SINGLE, END
import random
import textwrap
# os is no longer needed for images, but might be useful for other things later.
# import os # Para verificar se os arquivos de imagem existem

# Tenta importar Pillow, se não conseguir, exibe uma mensagem de erro mais clara
try:
    # Import necessary Pillow components
    from PIL import Image, ImageTk, ImageDraw, ImageFont
except ImportError:
    print("Erro: A biblioteca Pillow não está instalada.")
    print("Execute: pip install Pillow")
    exit() # Sai do script se Pillow não estiver disponível

# --- Constantes de Estilo ---
COR_FUNDO = '#2E2E2E'
COR_TEXTO_AREA = '#1C1C1C'
COR_TEXTO_FG = '#E0E0E0'
COR_HP = '#FF4500' # Laranja avermelhado
COR_STAMINA = '#32CD32' # Verde limão
COR_ALMAS = '#ADD8E6' # Azul claro
COR_ESTUS = '#FFA500' # Laranja
COR_NIVEL = '#DAA520' # Dourado
COR_ATAQUE = '#DC143C' # Carmesim
COR_DEFESA = '#4682B4' # Azul aço
COR_BOTAO_BG = '#4A4A4A'
COR_BOTAO_FG = '#FFFFFF'
COR_BOTAO_DISABLED = '#333333'
COR_PAINEL_STATUS = '#252525' # Um pouco mais escuro que o fundo
COR_LISTBOX_BG = '#383838'
COR_LISTBOX_FG = '#E0E0E0'
COR_LISTBOX_SELECT = '#5A5A5A'

# Cores para Imagens Geradas
IMG_COR_CHAO_PEDRA = '#5A5A5A'
IMG_COR_ARVORE_TRONCO = '#5C4033'
IMG_COR_ARVORE_FOLHA = '#228B22'
IMG_COR_PONTE_MADEIRA = '#8B4513'
IMG_COR_ABISMO = '#1A1A1A'
IMG_COR_FOGO = '#FF8C00'
IMG_COR_PAREDE_SANTUARIO = '#404040'
IMG_COR_MERCADOR_CAPUZ = '#303030'
IMG_COR_MERCADOR_OLHOS = '#FFFF00'
IMG_COR_INIMIGO_GENERICO = '#8B0000' # Vermelho escuro
IMG_COR_BOSS = '#6A0DAD' # Roxo

FONTE_TEXTO = ("Courier New", 10)
FONTE_STATUS_TITULO = ("Arial", 12, "bold", "underline")
FONTE_STATUS_LABEL = ("Arial", 10, "bold")
FONTE_STATUS_VALOR = ("Arial", 10)
FONTE_BOTAO = ('Arial', 10)
FONTE_LOJA_ITEM = ('Arial', 9)
FONTE_LOJA_DESC = ('Arial', 8, 'italic')
# Tenta carregar uma fonte para usar nas imagens geradas
try:
    # Ajuste o caminho e o nome da fonte se necessário (use 'arial.ttf' se estiver no Windows)
    # Em Linux pode ser algo como '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    FONTE_IMAGEM_PADRAO = ImageFont.truetype("cour.ttf", 18) # Courier New Bold
    FONTE_IMAGEM_TITULO = ImageFont.truetype("courbd.ttf", 24) # Courier New Bold
except IOError:
    print("Aviso: Fonte 'cour.ttf'/'courbd.ttf' não encontrada. Usando fonte padrão da PIL.")
    FONTE_IMAGEM_PADRAO = ImageFont.load_default()
    FONTE_IMAGEM_TITULO = ImageFont.load_default()


# --- Constantes de Jogo ---
STAMINA_CUSTO_ATAQUE = 10
STAMINA_CUSTO_ESQUIVA = 15
STAMINA_REGEN_TURNO = 12
STAMINA_REGEN_MOVIMENTO = 5
CHANCE_ESQUIVA = 0.60
CURA_ESTUS_PERCENTUAL = 0.4
NIVEL_BASE_CUSTO = 100
NIVEL_CUSTO_INCREMENTO = 75

IMAGEM_LARGURA = 400
IMAGEM_ALTURA = 250
# CAMINHO_IMAGENS = "imagens" # Não é mais necessário para arquivos externos
# IMAGEM_DEFAULT = os.path.join(CAMINHO_IMAGENS, "default.png") # Não é mais necessário

# --- Classe para Janela de Subir Nível (Sem alterações) ---
class JanelaSubirNivel(Toplevel):
    def __init__(self, parent, jogador_atributos, callback_subir_nivel):
        super().__init__(parent)
        self.transient(parent) # Mantém a janela no topo da janela pai
        self.grab_set() # Bloqueia interação com a janela principal
        self.title("Subir de Nível")
        self.configure(bg=COR_FUNDO)
        self.resizable(False, False)

        self.jogador_atributos = jogador_atributos
        self.callback = callback_subir_nivel
        self.atributo_escolhido = None

        custo = jogador_atributos['proximo_nivel_custo']
        almas = jogador_atributos['almas']

        Label(self, text=f"Almas Atuais: {almas}", bg=COR_FUNDO, fg=COR_ALMAS, font=FONTE_STATUS_LABEL).pack(pady=5)
        Label(self, text=f"Custo para Nível {jogador_atributos['nivel'] + 1}: {custo} Almas", bg=COR_FUNDO, fg=COR_TEXTO_FG, font=FONTE_STATUS_LABEL).pack(pady=5)

        if almas < custo:
            Label(self, text="Almas insuficientes!", bg=COR_FUNDO, fg=COR_HP, font=FONTE_STATUS_LABEL).pack(pady=10)
            Button(self, text="Fechar", command=self.destroy, bg=COR_BOTAO_BG, fg=COR_BOTAO_FG, width=15, font=FONTE_BOTAO).pack(pady=10, padx=20)
        else:
            Label(self, text="Escolha um atributo para aumentar:", bg=COR_FUNDO, fg=COR_TEXTO_FG, font=FONTE_STATUS_LABEL).pack(pady=10)

            frame_botoes = Frame(self, bg=COR_FUNDO)
            frame_botoes.pack(pady=5, padx=20, fill=tk.X)
            frame_botoes.grid_columnconfigure(0, weight=1)
            frame_botoes.grid_columnconfigure(1, weight=1)
            frame_botoes.grid_columnconfigure(2, weight=1) # Adiciona coluna para Defesa

            # --- Botões de Atributos ---
            # HP Máx: +5
            Button(frame_botoes, text=f"Vigor (+5 HP)", command=lambda: self.escolher_atributo('max_hp', 5, 'Vigor'),
                   bg=COR_BOTAO_BG, fg=COR_HP, width=15, font=FONTE_BOTAO).grid(row=0, column=0, padx=5, pady=5)
            # Stamina Máx: +4
            Button(frame_botoes, text=f"Fôlego (+4 Stam)", command=lambda: self.escolher_atributo('max_stamina', 4, 'Fôlego'),
                   bg=COR_BOTAO_BG, fg=COR_STAMINA, width=15, font=FONTE_BOTAO).grid(row=0, column=1, padx=5, pady=5)
            # Ataque: +2
            Button(frame_botoes, text=f"Força (+2 Ataque)", command=lambda: self.escolher_atributo('poder_ataque', 2, 'Força'),
                   bg=COR_BOTAO_BG, fg=COR_ATAQUE, width=15, font=FONTE_BOTAO).grid(row=0, column=2, padx=5, pady=5)
             # Defesa: +1
            Button(frame_botoes, text=f"Resist. (+1 Defesa)", command=lambda: self.escolher_atributo('defesa', 1, 'Resistência'),
                  bg=COR_BOTAO_BG, fg=COR_DEFESA, width=15, font=FONTE_BOTAO).grid(row=1, column=0, columnspan=3, padx=5, pady=5) # Span para centralizar

            Button(self, text="Cancelar", command=self.destroy, bg=COR_BOTAO_BG, fg=COR_BOTAO_FG, width=15, font=FONTE_BOTAO).pack(pady=10)

        # Centralizar a janela
        self.update_idletasks()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        win_width = self.winfo_width()
        win_height = self.winfo_height()
        x = parent_x + (parent_width // 2) - (win_width // 2)
        y = parent_y + (parent_height // 2) - (win_height // 2)
        self.geometry(f"+{x}+{y}")

    def escolher_atributo(self, atributo, valor_aumento, nome_atributo):
        self.atributo_escolhido = (atributo, valor_aumento, nome_atributo)
        self.callback(self.atributo_escolhido) # Chama a função de volta no jogo principal
        self.destroy()

# --- Classe para Janela da Loja de Acessórios (Sem alterações) ---
class JanelaLoja(Toplevel):
    def __init__(self, parent, jogador_atributos, inventario_loja, callback_compra):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title("Mercador - Acessórios")
        self.configure(bg=COR_FUNDO)
        self.resizable(False, False)
        self.geometry("550x450") # Ajuste o tamanho conforme necessário

        self.jogador_atributos = jogador_atributos
        self.inventario_loja = inventario_loja
        self.callback = callback_compra
        self.item_selecionado_id = None

        # --- Layout ---
        frame_topo = Frame(self, bg=COR_FUNDO)
        frame_topo.pack(pady=10, fill=tk.X, padx=10)
        Label(frame_topo, text="Acessórios Disponíveis", bg=COR_FUNDO, fg=COR_TEXTO_FG, font=FONTE_STATUS_TITULO).pack(side=tk.LEFT)
        self.label_almas = Label(frame_topo, text=f"Almas: {jogador_atributos['almas']}", bg=COR_FUNDO, fg=COR_ALMAS, font=FONTE_STATUS_LABEL)
        self.label_almas.pack(side=tk.RIGHT)

        frame_meio = Frame(self, bg=COR_FUNDO)
        frame_meio.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        frame_meio.grid_columnconfigure(0, weight=2)
        frame_meio.grid_columnconfigure(1, weight=3)
        frame_meio.grid_rowconfigure(0, weight=1)

        frame_lista = Frame(frame_meio, bg=COR_FUNDO)
        frame_lista.grid(row=0, column=0, sticky="nswe", padx=(0, 5))
        scrollbar = Scrollbar(frame_lista, orient=tk.VERTICAL)
        self.listbox_itens = Listbox(frame_lista, selectmode=SINGLE, exportselection=False,
                                     bg=COR_LISTBOX_BG, fg=COR_LISTBOX_FG,
                                     selectbackground=COR_LISTBOX_SELECT,
                                     selectforeground=COR_TEXTO_FG,
                                     font=FONTE_LOJA_ITEM, height=15,
                                     yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox_itens.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_itens.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox_itens.bind('<<ListboxSelect>>', self.mostrar_detalhes_item)

        frame_detalhes = Frame(frame_meio, bg=COR_PAINEL_STATUS, bd=1, relief=tk.SUNKEN)
        frame_detalhes.grid(row=0, column=1, sticky="nswe", padx=(5, 0))
        frame_detalhes.grid_columnconfigure(0, weight=1)
        self.label_item_nome = Label(frame_detalhes, text="Selecione um item", bg=COR_PAINEL_STATUS, fg=COR_TEXTO_FG, font=("Arial", 11, "bold"), wraplength=240)
        self.label_item_nome.grid(row=0, column=0, pady=(10, 5), padx=10, sticky="w")
        self.label_item_custo = Label(frame_detalhes, text="", bg=COR_PAINEL_STATUS, fg=COR_ALMAS, font=FONTE_STATUS_LABEL)
        self.label_item_custo.grid(row=1, column=0, pady=2, padx=10, sticky="w")
        self.label_item_bonus = Label(frame_detalhes, text="", bg=COR_PAINEL_STATUS, fg=COR_TEXTO_FG, font=FONTE_LOJA_DESC, justify=tk.LEFT, wraplength=240)
        self.label_item_bonus.grid(row=2, column=0, pady=2, padx=10, sticky="w")
        self.label_item_desc = Label(frame_detalhes, text="", bg=COR_PAINEL_STATUS, fg=COR_TEXTO_FG, font=FONTE_LOJA_DESC, justify=tk.LEFT, wraplength=240)
        self.label_item_desc.grid(row=3, column=0, pady=5, padx=10, sticky="nw")
        self.label_item_aviso = Label(frame_detalhes, text="", bg=COR_PAINEL_STATUS, fg=COR_HP, font=FONTE_LOJA_DESC, justify=tk.LEFT, wraplength=240)
        self.label_item_aviso.grid(row=4, column=0, pady=5, padx=10, sticky="w")

        frame_botoes = Frame(self, bg=COR_FUNDO)
        frame_botoes.pack(pady=10, fill=tk.X, padx=10)
        frame_botoes.grid_columnconfigure(0, weight=1)
        frame_botoes.grid_columnconfigure(1, weight=1)
        self.btn_comprar = Button(frame_botoes, text="Comprar", command=self.comprar_item,
                                   bg=COR_BOTAO_BG, fg=COR_BOTAO_FG, width=15, font=FONTE_BOTAO, state=tk.DISABLED)
        self.btn_comprar.grid(row=0, column=0, padx=5, sticky="e")
        Button(frame_botoes, text="Fechar", command=self.destroy,
               bg=COR_BOTAO_BG, fg=COR_BOTAO_FG, width=15, font=FONTE_BOTAO).grid(row=0, column=1, padx=5, sticky="w")

        self.atualizar_lista_itens()

        self.update_idletasks()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        win_width = self.winfo_width()
        win_height = self.winfo_height()
        x = parent_x + (parent_width // 2) - (win_width // 2)
        y = parent_y + (parent_height // 2) - (win_height // 2)
        self.geometry(f"+{x}+{y}")

    def atualizar_lista_itens(self):
        self.listbox_itens.delete(0, END)
        ja = self.jogador_atributos
        for item_id, item_data in self.inventario_loja.items():
            texto_item = f"{item_data['nome']} ({item_data['custo']} Almas)"
            self.listbox_itens.insert(END, texto_item)
            self.listbox_itens.itemconfig(END, {'fg': COR_LISTBOX_FG})
            if item_id in ja['acessorios_possuidos']:
                self.listbox_itens.itemconfig(END, {'fg': 'grey', 'selectforeground': 'grey'})
            elif ja['almas'] < item_data['custo']:
                 self.listbox_itens.itemconfig(END, {'fg': '#AAAAAA'})
        self.limpar_detalhes()

    def limpar_detalhes(self):
         self.label_item_nome.config(text="Selecione um item")
         self.label_item_custo.config(text="")
         self.label_item_bonus.config(text="")
         self.label_item_desc.config(text="")
         self.label_item_aviso.config(text="")
         self.btn_comprar.config(state=tk.DISABLED)
         self.item_selecionado_id = None

    def mostrar_detalhes_item(self, event=None):
        selecao = self.listbox_itens.curselection()
        if not selecao:
            self.limpar_detalhes()
            return
        index = selecao[0]
        item_id_list = list(self.inventario_loja.keys())
        if index >= len(item_id_list):
             self.limpar_detalhes()
             return
        self.item_selecionado_id = item_id_list[index]
        item_data = self.inventario_loja[self.item_selecionado_id]
        ja = self.jogador_atributos
        self.label_item_nome.config(text=item_data['nome'])
        self.label_item_custo.config(text=f"Custo: {item_data['custo']} Almas")
        bonus_texto = "Bônus:\n"
        for atr, val in item_data.get('bonus', {}).items():
             nome_atr = atr.replace("max_", "").replace("_", " ").title()
             bonus_texto += f"  + {val} {nome_atr}\n"
        self.label_item_bonus.config(text=bonus_texto.strip())
        self.label_item_desc.config(text=f"Descrição: {item_data['descricao']}")
        self.label_item_aviso.config(text="")
        if self.item_selecionado_id in ja['acessorios_possuidos']:
            self.btn_comprar.config(state=tk.DISABLED)
            self.label_item_aviso.config(text="Você já possui este item.", fg="grey")
        elif ja['almas'] < item_data['custo']:
            self.btn_comprar.config(state=tk.DISABLED)
            self.label_item_aviso.config(text="Almas insuficientes.", fg=COR_HP)
        else:
            self.btn_comprar.config(state=tk.NORMAL, bg=COR_BOTAO_BG, fg=COR_BOTAO_FG)

    def comprar_item(self):
        if self.item_selecionado_id:
            item_data = self.inventario_loja[self.item_selecionado_id]
            ja = self.jogador_atributos
            if self.item_selecionado_id in ja['acessorios_possuidos']:
                messagebox.showwarning("Aviso", "Você já possui este item.")
                return
            if ja['almas'] < item_data['custo']:
                messagebox.showerror("Erro", "Almas insuficientes!")
                return
            compra_sucesso = self.callback(self.item_selecionado_id, item_data)
            if compra_sucesso:
                self.label_almas.config(text=f"Almas: {self.jogador_atributos['almas']}")
                self.atualizar_lista_itens()
                self.limpar_detalhes()
                messagebox.showinfo("Compra Realizada", f"Você adquiriu {item_data['nome']}!")

# --- Classe Principal do Jogo ---
class RPGTextoEstiloSouls:
    def __init__(self, janela_principal):
        self.janela = janela_principal
        janela_principal.title("Jornada Textual do Cinéreo v4 - Boss e Lore") # Versão atualizada
        janela_principal.geometry("1000x700")
        janela_principal.configure(bg=COR_FUNDO)

        # --- Estado do Jogo ---
        self.jogador_atributos = {
            "nivel": 1, "hp": 100, "max_hp": 100, "stamina": 50, "max_stamina": 50,
            "almas": 0, "estus_cargas": 3, "max_estus": 3, "poder_ataque": 12,
            "defesa": 5, "proximo_nivel_custo": NIVEL_BASE_CUSTO,
            "localizacao": "santuario_decadente", "ultimo_santuario": "santuario_decadente",
            "acessorios_possuidos": set()
        }
        self.inimigo_atual = None
        self.jogo_terminado = False
        self.imagem_tk_atual = None # Armazena a PhotoImage para evitar garbage collection

        # --- História / Lore Inicial ---
        self.lore_inicial = [
            "O ciclo se repete. As cinzas se agitam e você desperta, um 'Cinéreo', um ser marcado para reacender a Primeira Chama.",
            "Ou talvez... para deixá-la apagar de vez.",
            "Seu passado é nebuloso, sua motivação incerta, mas o caminho à frente exige força e resiliência.",
            "Erga-se, Cinéreo, pois Lordran ainda clama por campeões, mesmo que amaldiçoados."
        ]

        # --- Mundo do Jogo (com chaves de imagem em vez de caminhos) ---
        self.mundo = {
            "santuario_decadente": {
                "nome": "Santuário Decadente",
                "descricao": ("O ar é pesado com poeira milenar e a luz fraca de uma fogueira solitária dança nas paredes rachadas. "
                              "Restos de estátuas quebradas sugerem uma glória há muito perdida. Dizem que este lugar já foi um elo vital, agora é apenas um refúgio precário. "
                              "Um caminho leva ao norte, por onde o vento traz uivos distantes. Uma figura encapuzada permanece nas sombras do canto."),
                "saidas": {"norte": "trilha_sombria", "canto": "mercador_sombrio"},
                "acoes": ["Descansar (Restaurar)", "Subir de Nível"],
                "imagem": "santuario" # Chave para geração de imagem
            },
            "trilha_sombria": {
                "nome": "Trilha Sombria",
                "descricao": ("Árvores retorcidas, como dedos esqueléticos, margeiam esta trilha mal definida. "
                              "Ossos roídos e equipamento quebrado espalham-se pelo chão, testemunho de outros viajantes azarados. "
                              "O caminho continua para leste, onde uma estrutura precária atravessa um abismo, ou volta para sul."),
                "saidas": {"sul": "santuario_decadente", "leste": "ponte_apodrecida"},
                "chance_inimigo": 0.6,
                "tipo_inimigo": "soldado_vasio",
                "imagem": "trilha" # Chave para geração de imagem
            },
             "ponte_apodrecida": {
                "nome": "Ponte Apodrecida",
                "descricao": ("Vigas de madeira gemem sob seus pés. Abaixo, um abismo sem fundo parece engolir a luz e ecoa grunhidos bestiais. "
                              "A ponte oscila perigosamente, mas parece levar a uma entrada de caverna escura a leste. Voltar para oeste é mais seguro."),
                "saidas": {"oeste": "trilha_sombria", "leste": "covil_do_vigia"}, # Saída Leste leva ao Boss
                "chance_inimigo": 0.8,
                "tipo_inimigo": "rato_gigante",
                "imagem": "ponte" # Chave para geração de imagem
            },
            "covil_do_vigia": {
                "nome": "Covil do Vigia",
                "descricao": ("A ponte termina em uma caverna úmida e fétida. Pilhas de ossos se acumulam nos cantos. "
                              "No centro, bloqueando a passagem adiante (que parece inexistente), repousa uma figura corpulenta e blindada, armada com um grande martelo. "
                              "Seus olhos vazios fixam-se em você. Ele é o Vigia desta passagem esquecida."),
                "saidas": {"oeste": "ponte_apodrecida"}, # Apenas retorno por enquanto
                "tipo_inimigo": "vigia_da_ponte", # BOSS! Aparece sempre
                "chance_inimigo": 1.0, # Garante o encontro
                "imagem": "covil_boss" # Chave para geração de imagem
            },
            "mercador_sombrio": {
                "nome": "Mercador Sombrio",
                "descricao": ("Escondido nas sombras, um capuz esconde o rosto da figura. Bugigangas brilham fracamente em um manto estendido no chão. "
                              "'Muitos Cinéreos passaram por aqui... poucos continuaram. Tens almas? Troco por fragmentos de poder...', ele sibila."),
                "saidas": {"santuario": "santuario_decadente"},
                "acoes": ["Comprar Acessórios"],
                "imagem": "mercador" # Chave para geração de imagem
            }
        }

        # --- Tipos de Inimigos (Incluindo o Boss) ---
        self.inimigos = {
            "soldado_vasio": {
                "nome": "Soldado Vasio", "hp": 55, "ataque": 11, "defesa": 4, "almas": 80,
                "imagem": "inimigo_padrao" # Chave de imagem
             },
            "rato_gigante": {
                "nome": "Rato Gigante", "hp": 40, "ataque": 9, "defesa": 2, "almas": 45,
                "imagem": "inimigo_padrao" # Chave de imagem
             },
             "vigia_da_ponte": { # BOSS
                 "nome": "Vigia da Ponte Decadente", "hp": 250, "ataque": 20, "defesa": 8, "almas": 500,
                 "imagem": "inimigo_boss" # Chave de imagem
             }
        }

        # --- Loja de Acessórios (Sem alterações) ---
        self.loja_acessorios = {
            "anel_vitalidade": { "nome": "Anel da Vitalidade Lascado", "custo": 300, "descricao": "Um anel simples que emana um leve calor. Parece revigorar o portador.", "bonus": {"max_hp": 15} },
            "amuleto_cacador": { "nome": "Amuleto do Caçador Desgastado", "custo": 350, "descricao": "Gravado com bestas primitivas, inspira uma fúria contida.", "bonus": {"poder_ataque": 3} },
            "bracadeira_tartaruga": { "nome": "Braçadeira da Tartaruga Anciã", "custo": 400, "descricao": "Feita de um casco estranhamente resistente, acelera a recuperação.", "bonus": {"max_stamina": 10} },
            "placa_ferro": { "nome": "Placa de Ferro Enferrujada", "custo": 250, "descricao": "Um pedaço de armadura improvisada. Melhor que nada.", "bonus": {"defesa": 2} },
            "anel_serpente_prata": { "nome": "Anel da Serpente Prateada (Falso)", "custo": 600, "descricao": "Brilha palidamente. Dizem aumentar a absorção de almas, mas parece suspeito...", "bonus": {"almas_bonus_percent": 0.10} }
        }

        # --- Dicionário de Geradores de Imagem ---
        # Mapeia chaves (de locais, inimigos, etc.) para funções que criam imagens PIL
        self.geradores_imagem = {
            "default": self._gerar_imagem_default,
            "santuario": self._gerar_imagem_santuario,
            "trilha": self._gerar_imagem_trilha,
            "ponte": self._gerar_imagem_ponte,
            "covil_boss": self._gerar_imagem_covil_boss,
            "mercador": self._gerar_imagem_mercador,
            "combate": self._gerar_imagem_combate,
            "inimigo_padrao": self._gerar_imagem_inimigo_padrao,
            "inimigo_boss": self._gerar_imagem_inimigo_boss,
            "morte": self._gerar_imagem_morte,
        }

        # --- Configuração da Interface Gráfica ---
        self._configurar_interface()

        # --- Iniciar Jogo ---
        self._escrever_texto("\n".join(self.lore_inicial) + "\n") # Exibe a lore inicial
        self._atualizar_painel_status()
        self.mostrar_localizacao_atual()

    # --- Funções de Geração de Imagem ---

    def _gerar_imagem_base(self, cor_fundo=COR_FUNDO):
        """Cria uma imagem base com fundo sólido."""
        return Image.new('RGB', (IMAGEM_LARGURA, IMAGEM_ALTURA), color=cor_fundo)

    def _centralizar_texto(self, draw, texto, fonte, cor_texto=COR_TEXTO_FG):
         """Desenha texto centralizado na imagem."""
         largura_texto, altura_texto = draw.textsize(texto, font=fonte)
         x = (IMAGEM_LARGURA - largura_texto) // 2
         y = (IMAGEM_ALTURA - altura_texto) // 2
         draw.text((x, y), texto, font=fonte, fill=cor_texto)

    def _gerar_imagem_default(self):
        """Imagem padrão genérica."""
        img = self._gerar_imagem_base(COR_PAINEL_STATUS)
        draw = ImageDraw.Draw(img)
        self._centralizar_texto(draw, "?", FONTE_IMAGEM_TITULO, COR_TEXTO_FG)
        return img

    def _gerar_imagem_santuario(self):
        """Gera imagem para o Santuário Decadente."""
        img = self._gerar_imagem_base(IMG_COR_CHAO_PEDRA)
        draw = ImageDraw.Draw(img)
        # Parede de fundo
        draw.rectangle([0, 0, IMAGEM_LARGURA, IMAGEM_ALTURA // 2], fill=IMG_COR_PAREDE_SANTUARIO)
        # Fogueira (simples representação)
        fogo_x, fogo_y, fogo_r = IMAGEM_LARGURA // 2, IMAGEM_ALTURA * 3 // 4, 15
        draw.ellipse([fogo_x - fogo_r, fogo_y - fogo_r, fogo_x + fogo_r, fogo_y + fogo_r], fill=IMG_COR_FOGO)
        draw.ellipse([fogo_x - fogo_r//2, fogo_y - fogo_r//2, fogo_x + fogo_r//2, fogo_y + fogo_r//2], fill='#FFFF00') # Miolo
        draw.text((fogo_x - 35, fogo_y + fogo_r + 5), "Fogueira", font=FONTE_IMAGEM_PADRAO, fill=COR_TEXTO_FG)
        return img

    def _gerar_imagem_trilha(self):
        """Gera imagem para a Trilha Sombria."""
        img = self._gerar_imagem_base(IMG_COR_CHAO_PEDRA)
        draw = ImageDraw.Draw(img)
        # Árvores simples nas laterais
        largura_arvore = 30
        altura_arvore = IMAGEM_ALTURA // 2
        for i in range(3):
            # Esquerda
            x_e = 20 + i * 50 + random.randint(-10, 10)
            draw.rectangle([x_e, IMAGEM_ALTURA - altura_arvore, x_e + largura_arvore, IMAGEM_ALTURA], fill=IMG_COR_ARVORE_TRONCO)
            draw.ellipse([x_e - 10, IMAGEM_ALTURA - altura_arvore - 20, x_e + largura_arvore + 10, IMAGEM_ALTURA - altura_arvore + 30], fill=IMG_COR_ARVORE_FOLHA)
            # Direita
            x_d = IMAGEM_LARGURA - (20 + i * 50 + largura_arvore) + random.randint(-10, 10)
            draw.rectangle([x_d, IMAGEM_ALTURA - altura_arvore, x_d + largura_arvore, IMAGEM_ALTURA], fill=IMG_COR_ARVORE_TRONCO)
            draw.ellipse([x_d - 10, IMAGEM_ALTURA - altura_arvore - 20, x_d + largura_arvore + 10, IMAGEM_ALTURA - altura_arvore + 30], fill=IMG_COR_ARVORE_FOLHA)
        draw.text((IMAGEM_LARGURA//2 - 50, 20), "Trilha Sombria", font=FONTE_IMAGEM_PADRAO, fill=COR_TEXTO_FG)
        return img

    def _gerar_imagem_ponte(self):
        """Gera imagem para a Ponte Apodrecida."""
        img = self._gerar_imagem_base(IMG_COR_ABISMO)
        draw = ImageDraw.Draw(img)
        # Ponte (tábuas)
        largura_ponte = IMAGEM_LARGURA * 3 // 4
        x_inicio_ponte = (IMAGEM_LARGURA - largura_ponte) // 2
        for i in range(0, largura_ponte, 25):
            draw.rectangle([x_inicio_ponte + i, IMAGEM_ALTURA//3, x_inicio_ponte + i + 20, IMAGEM_ALTURA*2//3], fill=IMG_COR_PONTE_MADEIRA, outline='#654321')
        draw.text((IMAGEM_LARGURA//2 - 40, 10), "Ponte", font=FONTE_IMAGEM_PADRAO, fill=COR_TEXTO_FG)
        draw.text((IMAGEM_LARGURA//2 - 50, IMAGEM_ALTURA - 30), "Abismo...", font=FONTE_IMAGEM_PADRAO, fill='grey')
        return img

    def _gerar_imagem_mercador(self):
        """Gera imagem para o Mercador."""
        img = self._gerar_imagem_base(COR_PAINEL_STATUS) # Fundo escuro
        draw = ImageDraw.Draw(img)
        # Figura encapuzada simples
        corpo_x, corpo_y = IMAGEM_LARGURA // 2, IMAGEM_ALTURA * 2 // 3
        raio_cabeca = 30
        altura_corpo = 80
        # Capuz/Cabeça
        draw.ellipse([corpo_x - raio_cabeca, corpo_y - altura_corpo - raio_cabeca, corpo_x + raio_cabeca, corpo_y - altura_corpo + raio_cabeca], fill=IMG_COR_MERCADOR_CAPUZ)
        # Corpo
        draw.rectangle([corpo_x - raio_cabeca, corpo_y - altura_corpo, corpo_x + raio_cabeca, corpo_y], fill=IMG_COR_MERCADOR_CAPUZ)
        # Olhos brilhantes
        draw.ellipse([corpo_x - 10, corpo_y - altura_corpo - 5, corpo_x - 5, corpo_y - altura_corpo ], fill=IMG_COR_MERCADOR_OLHOS)
        draw.ellipse([corpo_x + 5, corpo_y - altura_corpo - 5, corpo_x + 10, corpo_y - altura_corpo ], fill=IMG_COR_MERCADOR_OLHOS)
        draw.text((corpo_x - 50, corpo_y + 10), "'Almas...'", font=FONTE_IMAGEM_PADRAO, fill=COR_ALMAS)
        return img

    def _gerar_imagem_covil_boss(self):
        """Gera imagem para o Covil do Boss."""
        img = self._gerar_imagem_base('#3D2B1F') # Caverna marrom escura
        draw = ImageDraw.Draw(img)
        # Desenha o Boss no centro (grande retângulo roxo)
        boss_largura = 80
        boss_altura = 120
        x_boss = (IMAGEM_LARGURA - boss_largura) // 2
        y_boss = (IMAGEM_ALTURA - boss_altura) // 2 + 20 # Um pouco pra baixo
        draw.rectangle([x_boss, y_boss, x_boss + boss_largura, y_boss + boss_altura], fill=IMG_COR_BOSS, outline='#4B0082')
        # Martelo simples ao lado
        martelo_x = x_boss + boss_largura
        martelo_y = y_boss + boss_altura // 3
        draw.rectangle([martelo_x, martelo_y, martelo_x + 15, martelo_y + 60], fill='#696969') # Cabo
        draw.rectangle([martelo_x-5, martelo_y-10, martelo_x + 20, martelo_y+20], fill='#808080') # Cabeça
        # Texto
        self._centralizar_texto(draw, "O VIGIA", FONTE_IMAGEM_TITULO, COR_HP)
        return img

    def _gerar_imagem_combate(self):
        """Imagem genérica para o estado de combate."""
        img = self._gerar_imagem_base('#400000') # Fundo vermelho escuro
        draw = ImageDraw.Draw(img)
        # Desenha "espadas" cruzadas de forma simples
        espada_len = 100
        centro_x, centro_y = IMAGEM_LARGURA // 2, IMAGEM_ALTURA // 2
        cor_lamina = '#C0C0C0' # Prata
        cor_cabo = '#8B4513' # Marrom

        # Espada 1 (diagonal \ )
        draw.line([(centro_x - espada_len//2, centro_y - espada_len//2), (centro_x + espada_len//2, centro_y + espada_len//2)], fill=cor_lamina, width=8)
        draw.rectangle([centro_x - espada_len//2 - 10, centro_y - espada_len//2 -5 , centro_x - espada_len//2 + 10, centro_y - espada_len//2 + 5], fill=cor_cabo) # Guarda
        # Espada 2 (diagonal / )
        draw.line([(centro_x + espada_len//2, centro_y - espada_len//2), (centro_x - espada_len//2, centro_y + espada_len//2)], fill=cor_lamina, width=8)
        draw.rectangle([centro_x + espada_len//2 - 10, centro_y - espada_len//2 -5 , centro_x + espada_len//2 + 10, centro_y - espada_len//2 + 5], fill=cor_cabo) # Guarda

        self._centralizar_texto(draw, "COMBATE!", FONTE_IMAGEM_TITULO, COR_HP)
        return img

    def _gerar_imagem_inimigo_padrao(self):
        """Gera imagem simples para inimigos comuns."""
        img = self._gerar_imagem_base('#500000') # Fundo vermelho um pouco mais claro
        draw = ImageDraw.Draw(img)
        # Forma genérica ameaçadora (silhueta)
        inimigo_largura = 50
        inimigo_altura = 90
        x = (IMAGEM_LARGURA - inimigo_largura) // 2
        y = (IMAGEM_ALTURA - inimigo_altura) // 2
        draw.rectangle([x, y, x+inimigo_largura, y+inimigo_altura], fill=IMG_COR_INIMIGO_GENERICO)
        # Olhos
        draw.point((x + 15, y + 20), fill=COR_HP)
        draw.point((x + 35, y + 20), fill=COR_HP)
        self._centralizar_texto(draw, "Inimigo", FONTE_IMAGEM_PADRAO, COR_TEXTO_FG)
        return img

    def _gerar_imagem_inimigo_boss(self):
         """Reutiliza a imagem do covil para o boss durante o combate."""
         # Poderia fazer uma variação, mas reutilizar é mais simples
         return self._gerar_imagem_covil_boss() # Chama a mesma função

    def _gerar_imagem_morte(self):
        """Gera a imagem "VOCÊ MORREU"."""
        img = self._gerar_imagem_base('black') # Fundo preto
        draw = ImageDraw.Draw(img)
        try:
             # Tenta usar uma fonte maior e mais impactante, se disponível
             fonte_morte = ImageFont.truetype("impact.ttf", 60)
        except IOError:
             fonte_morte = FONTE_IMAGEM_TITULO # Fallback para a fonte padrão
        self._centralizar_texto(draw, "VOCÊ MORREU", fonte_morte, COR_HP)
        return img

    # --- Funções Auxiliares da Interface (com adaptação de imagem) ---

    def _configurar_interface(self):
        """Cria e organiza os widgets da interface com painel de status e imagem."""
        self.janela.grid_columnconfigure(0, weight=0, minsize=230) # Painel Status
        self.janela.grid_columnconfigure(1, weight=1) # Área Principal
        self.janela.grid_rowconfigure(0, weight=1)

        # Frame Status (Painel Esquerdo)
        self.frame_status = tk.Frame(self.janela, bg=COR_PAINEL_STATUS, bd=2, relief=tk.SUNKEN)
        self.frame_status.grid(row=0, column=0, sticky="nswe", padx=(5,0), pady=5)
        self.frame_status.grid_columnconfigure(0, weight=1)

        self.status_labels = {}
        Label(self.frame_status, text="ATRIBUTOS", bg=COR_PAINEL_STATUS, fg=COR_TEXTO_FG, font=FONTE_STATUS_TITULO).grid(row=0, column=0, pady=(10,15), sticky="ew")
        row_idx = 1
        # Adicionado 'defesa'
        for chave, nome, cor in [('nivel', 'Nível', COR_NIVEL),
                                 ('hp', 'HP', COR_HP),
                                 ('stamina', 'Stamina', COR_STAMINA),
                                 ('poder_ataque', 'Ataque', COR_ATAQUE),
                                 ('defesa', 'Defesa', COR_DEFESA),
                                 ('almas', 'Almas', COR_ALMAS),
                                 ('estus', 'Estus', COR_ESTUS),
                                 ('custo_nivel', 'Próx. Nível', COR_ALMAS)]:
            frame_linha = Frame(self.frame_status, bg=COR_PAINEL_STATUS)
            frame_linha.grid(row=row_idx, column=0, sticky='ew', padx=10, pady=2)
            frame_linha.grid_columnconfigure(0, weight=1) # Label Nome
            frame_linha.grid_columnconfigure(1, weight=2) # Label Valor

            lbl_nome = Label(frame_linha, text=f"{nome}:", anchor='w', bg=COR_PAINEL_STATUS, fg=cor, font=FONTE_STATUS_LABEL)
            lbl_nome.grid(row=0, column=0, sticky='w')
            lbl_valor = Label(frame_linha, text="", anchor='e', bg=COR_PAINEL_STATUS, fg=COR_TEXTO_FG, font=FONTE_STATUS_VALOR)
            lbl_valor.grid(row=0, column=1, sticky='e')
            self.status_labels[chave] = lbl_valor
            row_idx += 1

        # Frame Principal (Direita)
        self.frame_principal = tk.Frame(self.janela, bg=COR_FUNDO)
        self.frame_principal.grid(row=0, column=1, sticky="nsew", padx=(0,5), pady=5)
        self.frame_principal.grid_rowconfigure(0, weight=0) # Imagem
        self.frame_principal.grid_rowconfigure(1, weight=1) # Área Texto
        self.frame_principal.grid_rowconfigure(2, weight=0) # Botões
        self.frame_principal.grid_columnconfigure(0, weight=1)

        # Label da Imagem
        self.label_imagem = tk.Label(self.frame_principal, bg=COR_FUNDO) # O fundo da imagem será definido pela imagem gerada
        self.label_imagem.grid(row=0, column=0, pady=(0, 5), sticky="ew")

        # Área de Texto Principal
        self.area_texto = scrolledtext.ScrolledText(self.frame_principal, wrap=tk.WORD, height=15,
                                                    state='disabled', bg=COR_TEXTO_AREA, fg=COR_TEXTO_FG,
                                                    font=FONTE_TEXTO, bd=2, relief=tk.SUNKEN)
        self.area_texto.grid(row=1, column=0, sticky="nsew", pady=5)

        # Frame de Botões
        self.frame_botoes = tk.Frame(self.frame_principal, bg=COR_FUNDO)
        self.frame_botoes.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        # Configura colunas para espaçamento/centralização (0 e 6 vazias, botões de 1 a 5)
        for i in range(7): # 7 colunas para melhor espaçamento central
             self.frame_botoes.grid_columnconfigure(i, weight=1)

        self.botoes_acao = {}
        # Os botões são criados dinamicamente por _criar_botoes()

    def _gerar_e_exibir_imagem(self, chave_imagem="default"):
        """Gera uma imagem PIL baseada na chave, converte para Tkinter e exibe."""
        try:
            # Encontra a função geradora correta, ou usa a default
            funcao_geradora = self.geradores_imagem.get(chave_imagem, self.geradores_imagem["default"])
            img_pil = funcao_geradora()

            # Redimensiona (opcional, mas mantém consistência)
            # Se as funções geradoras já criam no tamanho certo, pode remover.
            img_pil = img_pil.resize((IMAGEM_LARGURA, IMAGEM_ALTURA), Image.Resampling.LANCZOS)

            # Converte para PhotoImage do Tkinter
            self.imagem_tk_atual = ImageTk.PhotoImage(img_pil) # Guarda referência!

            # Atualiza o label na interface
            if hasattr(self, 'label_imagem'): # Verifica se o label já existe
                self.label_imagem.config(image=self.imagem_tk_atual)
            else:
                 print("Aviso: Tentando exibir imagem antes da label ser criada.")

        except Exception as e:
            print(f"Erro ao gerar ou exibir a imagem para a chave '{chave_imagem}': {e}")
            # Tenta exibir uma imagem realmente básica como fallback extremo
            try:
                img_fallback_pil = self._gerar_imagem_base(COR_FUNDO) # Fundo simples
                draw = ImageDraw.Draw(img_fallback_pil)
                draw.text((10,10), f"Erro Img:\n{chave_imagem}", font=FONTE_IMAGEM_PADRAO, fill=COR_HP)
                self.imagem_tk_atual = ImageTk.PhotoImage(img_fallback_pil)
                if hasattr(self, 'label_imagem'):
                    self.label_imagem.config(image=self.imagem_tk_atual)
            except Exception as e_fallback:
                 print(f"Erro ao gerar imagem de fallback: {e_fallback}")
                 if hasattr(self, 'label_imagem'):
                    self.label_imagem.config(image='') # Remove qualquer imagem anterior
                 self.imagem_tk_atual = None


    # _escrever_texto, _atualizar_painel_status, _limpar_botoes, _criar_botao permanecem iguais

    def _escrever_texto(self, mensagem):
        if not hasattr(self, 'area_texto'): return
        self.area_texto.config(state='normal')
        try:
            largura_pixels = self.area_texto.winfo_width()
            largura_char_aprox = font.Font(font=FONTE_TEXTO).measure("0")
            largura_wrap = max(10, (largura_pixels // largura_char_aprox) - 2) # Ajuste
        except (tk.TclError, ZeroDivisionError):
            largura_wrap = 80 # Fallback
        linhas_formatadas = textwrap.wrap(mensagem, width=largura_wrap)
        texto_final = "\n".join(linhas_formatadas)
        self.area_texto.insert(tk.END, texto_final + "\n\n")
        self.area_texto.see(tk.END)
        self.area_texto.config(state='disabled')

    def _atualizar_painel_status(self):
        if not hasattr(self, 'status_labels'): return
        ja = self.jogador_atributos
        self.status_labels['nivel'].config(text=f"{ja['nivel']}")
        self.status_labels['hp'].config(text=f"{ja['hp']} / {ja['max_hp']}")
        self.status_labels['stamina'].config(text=f"{ja['stamina']} / {ja['max_stamina']}")
        self.status_labels['poder_ataque'].config(text=f"{ja['poder_ataque']}")
        self.status_labels['defesa'].config(text=f"{ja['defesa']}")
        self.status_labels['almas'].config(text=f"{ja['almas']}")
        self.status_labels['estus'].config(text=f"{ja['estus_cargas']} / {ja['max_estus']}")
        self.status_labels['custo_nivel'].config(text=f"{ja['proximo_nivel_custo']}")
        if 'max_hp' in ja and ja['max_hp'] > 0:
            hp_percent = ja['hp'] / ja['max_hp']
            if hp_percent <= 0: self.status_labels['hp'].config(fg='#8B0000')
            elif hp_percent < 0.3: self.status_labels['hp'].config(fg='#FF0000')
            elif hp_percent < 0.6: self.status_labels['hp'].config(fg='#FFA500')
            else: self.status_labels['hp'].config(fg=COR_HP)
        else: self.status_labels['hp'].config(fg=COR_HP)

    def _limpar_botoes(self):
        if not hasattr(self, 'frame_botoes'): return
        for widget in self.frame_botoes.winfo_children():
            widget.destroy()
        self.botoes_acao = {}

    def _criar_botao(self, texto, comando, coluna, **kwargs):
        if not hasattr(self, 'frame_botoes'): return None
        btn = tk.Button(self.frame_botoes, text=texto, command=comando,
                        bg=COR_BOTAO_BG, fg=COR_BOTAO_FG, font=FONTE_BOTAO,
                        width=18, relief=tk.RAISED, bd=2,
                        disabledforeground=COR_BOTAO_DISABLED,
                        **kwargs)
        btn.grid(row=0, column=coluna, padx=5, pady=5, sticky="ew")
        return btn

    def _criar_botoes(self):
        self._limpar_botoes()
        if self.jogo_terminado:
            self.botoes_acao['reiniciar'] = self._criar_botao("Despertar Novamente", self.reiniciar_jogo, 3) # Coluna 3 de 7 (centro)
            return

        ja = self.jogador_atributos
        coluna_atual = 1 # Começa na coluna 1 (de 0 a 6)

        if self.inimigo_atual:
            # --- Botões de Combate (Centro) ---
            btn_atacar = self._criar_botao(f"Atacar ({STAMINA_CUSTO_ATAQUE} Stm)", lambda: self.processar_acao_jogador('atacar', custo=STAMINA_CUSTO_ATAQUE), 2) # Coluna 2
            if ja['stamina'] < STAMINA_CUSTO_ATAQUE: btn_atacar.config(state=tk.DISABLED, bg=COR_BOTAO_DISABLED)
            self.botoes_acao['atacar'] = btn_atacar

            btn_esquivar = self._criar_botao(f"Esquivar ({STAMINA_CUSTO_ESQUIVA} Stm)", lambda: self.processar_acao_jogador('esquivar', custo=STAMINA_CUSTO_ESQUIVA), 3) # Coluna 3 (Centro)
            if ja['stamina'] < STAMINA_CUSTO_ESQUIVA: btn_esquivar.config(state=tk.DISABLED, bg=COR_BOTAO_DISABLED)
            self.botoes_acao['esquivar'] = btn_esquivar

            btn_estus = self._criar_botao(f"Usar Estus ({ja['estus_cargas']})", lambda: self.processar_acao_jogador('usar_estus'), 4) # Coluna 4
            if ja['estus_cargas'] <= 0 or ja['hp'] >= ja['max_hp']: btn_estus.config(state=tk.DISABLED, bg=COR_BOTAO_DISABLED)
            self.botoes_acao['usar_estus'] = btn_estus

        else:
            # --- Botões de Exploração e Ação ---
            dados_local = self.mundo.get(self.jogador_atributos['localizacao'], {})

            # Saídas
            for direcao, destino in dados_local.get("saidas", {}).items():
                nome_destino_fmt = destino.replace("_", " ").title() # Nome mais legível
                texto_direcao = direcao.capitalize() # "Norte", "Sul", "Leste", "Oeste"
                # Nomes especiais
                if direcao == "canto": texto_direcao = "Ir ao Canto"
                elif direcao == "santuario": texto_direcao = "Voltar ao Santuário"

                nome_botao = f"{texto_direcao}" # Mais curto: (p/ {nome_destino_fmt})
                if coluna_atual < 6: # Limita a 5 botões (colunas 1 a 5)
                    self.botoes_acao[direcao] = self._criar_botao(nome_botao, lambda d=direcao: self.mover(d), coluna_atual)
                    coluna_atual += 1

            # Ações no Local
            for acao in dados_local.get("acoes", []):
                acao_habilitada = True
                if acao == "Subir de Nível":
                     # Permitir tentar abrir mesmo sem almas (a janela informa)
                     if self.jogador_atributos["localizacao"] != self.jogador_atributos["ultimo_santuario"]:
                        acao_habilitada = False # Só na fogueira

                if acao_habilitada and coluna_atual < 6:
                    # Texto Abreviado Ações
                    texto_botao_acao = acao
                    if acao == "Descansar (Restaurar)": texto_botao_acao = "Descansar"
                    if acao == "Comprar Acessórios": texto_botao_acao = "Comprar"

                    btn_acao = self._criar_botao(texto_botao_acao, lambda a=acao: self.executar_acao_local(a), coluna_atual)
                    # Poderia desabilitar Level Up visualmente se sem almas aqui, mas a janela já trata.
                    # if acao == "Subir de Nível" and ja['almas'] < ja['proximo_nivel_custo']:
                    #    btn_acao.config(state=tk.DISABLED, bg=COR_BOTAO_DISABLED)
                    self.botoes_acao[acao] = btn_acao
                    coluna_atual += 1

            # Preencher colunas restantes se houver poucas opções para melhor distribuição visual
            # Esta lógica pode ser complexa; deixar como está por simplicidade.

    # --- Funções de Lógica do Jogo (com adaptação de imagem) ---

    def calcular_proximo_custo_nivel(self, nivel_atual):
        return NIVEL_BASE_CUSTO + (nivel_atual - 1) * NIVEL_CUSTO_INCREMENTO

    def mostrar_localizacao_atual(self):
        if self.jogo_terminado: return

        chave_local = self.jogador_atributos["localizacao"]
        dados_local = self.mundo.get(chave_local)

        if not dados_local:
            self._escrever_texto("Erro: Localização desconhecida!")
            self._gerar_e_exibir_imagem("default") # Mostra imagem default
            return

        nome_local = dados_local.get("nome", chave_local.replace('_', ' ').title())
        self._escrever_texto(f"--- {nome_local} ---")
        self._escrever_texto(dados_local["descricao"])

        # Gera e exibe a imagem correspondente à chave do local
        chave_imagem_local = dados_local.get("imagem", "default")
        self._gerar_e_exibir_imagem(chave_imagem_local)

        # Regenera stamina ao entrar em nova área
        stamina_regen_quant = STAMINA_REGEN_MOVIMENTO * 3 if dados_local.get("chance_inimigo", 0) <= 0 else STAMINA_REGEN_MOVIMENTO
        self._regenerar_stamina(quantidade=stamina_regen_quant)
        self.jogador_atributos['stamina'] = min(self.jogador_atributos['max_stamina'], self.jogador_atributos['stamina'])

        chance_inimigo = dados_local.get("chance_inimigo", 0)
        if chance_inimigo > 0 and not self.inimigo_atual:
             if random.random() < chance_inimigo:
                 tipo_inimigo = dados_local.get("tipo_inimigo")
                 if tipo_inimigo:
                     self.iniciar_combate(tipo_inimigo)
                     # A imagem de combate/inimigo será definida em iniciar_combate
                 else:
                     self._escrever_texto("Algo está errado, o inimigo não pôde ser carregado.")
                     self._criar_botoes()
             else:
                 self._escrever_texto("O caminho parece livre... por enquanto.")
                 self._criar_botoes() # Botões de exploração
        else:
             # Se está em área segura OU se já está em combate (não deveria chegar aqui assim),
             # OU se é a área do boss (que será iniciada acima pelo chance=1)
             # garante os botões corretos (geralmente exploração, a menos que seja área de boss)
             # A lógica de combate no if acima já cuida do início da luta.
             if not self.inimigo_atual: # Se não encontrou inimigo (nem por chance, nem por ser área segura)
                self._criar_botoes()

        self._atualizar_painel_status()

    def mover(self, direcao):
        if self.inimigo_atual or self.jogo_terminado: return
        chave_local_atual = self.jogador_atributos["localizacao"]
        dados_local = self.mundo.get(chave_local_atual)
        if direcao in dados_local.get("saidas", {}):
            destino = dados_local["saidas"][direcao]
            self.jogador_atributos["localizacao"] = destino
            nome_destino = self.mundo.get(destino, {}).get("nome", direcao.capitalize())
            self._escrever_texto(f"Você segue para {nome_destino}...")
            self.mostrar_localizacao_atual() # Isso vai cuidar da imagem, texto, inimigos e botões do novo local
        else:
            self._escrever_texto("Você não pode ir por aí.")

    def executar_acao_local(self, nome_acao):
        if self.inimigo_atual or self.jogo_terminado: return
        local_atual = self.jogador_atributos["localizacao"]
        ultimo_santuario = self.jogador_atributos["ultimo_santuario"]
        if nome_acao == "Descansar (Restaurar)":
            if local_atual == ultimo_santuario:
                self._escrever_texto("Você descansa junto à fogueira moribunda...")
                ja = self.jogador_atributos
                ja["hp"] = ja["max_hp"]
                ja["stamina"] = ja["max_stamina"]
                ja["estus_cargas"] = ja["max_estus"]
                # Bosses geralmente não respawnam ao descansar numa fogueira simples,
                # mas inimigos comuns sim (não implementado aqui para simplicidade).
                self._atualizar_painel_status()
                # Atualiza a imagem do Santuário (caso estivesse diferente, ex: combate)
                self._gerar_e_exibir_imagem(self.mundo[local_atual].get("imagem", "default"))
                self._escrever_texto("HP, Stamina e Frascos de Estus restaurados. As ameaças lá fora o aguardam.")
                self._criar_botoes() # Botões podem ter sido reativados (estus)
            else:
                self._escrever_texto("Não há fogueira aqui para oferecer descanso.")
        elif nome_acao == "Subir de Nível":
             if local_atual == ultimo_santuario:
                 janela_level_up = JanelaSubirNivel(self.janela, self.jogador_atributos, self.finalizar_subir_nivel)
                 janela_level_up.wait_window() # Espera a janela fechar para continuar
                 self._criar_botoes() # Recria botões caso o custo/almas mudem a disponibilidade visual
             else:
                 self._escrever_texto("Você só pode meditar sobre suas almas na segurança da fogueira.")
        elif nome_acao == "Comprar Acessórios":
             if self.jogador_atributos["localizacao"] == "mercador_sombrio":
                 janela_loja = JanelaLoja(self.janela, self.jogador_atributos, self.loja_acessorios, self.finalizar_compra)
                 janela_loja.wait_window() # Espera a loja fechar
                 # Atualiza painel caso compre algo que mude stats
                 self._atualizar_painel_status()
             else:
                  self._escrever_texto("O mercador não está aqui.")
        else:
             self._escrever_texto(f"Ação '{nome_acao}' não reconhecida aqui.")

    # finalizar_subir_nivel e finalizar_compra permanecem praticamente iguais
    def finalizar_subir_nivel(self, escolha):
        if escolha:
            atributo, aumento, nome_atr = escolha
            custo = self.jogador_atributos['proximo_nivel_custo']
            if self.jogador_atributos['almas'] >= custo:
                ja = self.jogador_atributos
                ja['almas'] -= custo
                ja['nivel'] += 1
                ja[atributo] += aumento
                self._escrever_texto(f"Você meditou sobre suas almas e aprimorou sua {nome_atr}!")
                if atributo == 'max_hp': ja['hp'] = ja['max_hp']
                if atributo == 'max_stamina': ja['stamina'] = ja['max_stamina']
                ja['proximo_nivel_custo'] = self.calcular_proximo_custo_nivel(ja['nivel'])
                self._escrever_texto(f"Nível {ja['nivel']} alcançado. Próximo nível custará {ja['proximo_nivel_custo']} almas.")
                self._atualizar_painel_status()
                # _criar_botoes() é chamado após wait_window em executar_acao_local
            else:
                 messagebox.showerror("Erro", "Almas insuficientes!")
        # else: Cancelado

    def finalizar_compra(self, item_id, item_data):
        ja = self.jogador_atributos
        custo = item_data['custo']
        if item_id in ja['acessorios_possuidos']: return False # Já possui
        if ja['almas'] < custo: return False # Sem almas
        ja['almas'] -= custo
        ja['acessorios_possuidos'].add(item_id)
        self._escrever_texto(f"Você adquiriu {item_data['nome']} por {custo} almas.")
        for atributo, valor in item_data.get('bonus', {}).items():
            if atributo == "almas_bonus_percent":
                 self._escrever_texto(f"  - Efeito: Bônus de Almas (passivo).")
                 continue
            if atributo in ja:
                ja[atributo] += valor
                nome_atr = atributo.replace("max_", "").replace("_", " ").title()
                self._escrever_texto(f"  - {nome_atr} +{valor}.")
                if atributo == 'max_hp': ja['hp'] = ja['max_hp']
                if atributo == 'max_stamina': ja['stamina'] = ja['max_stamina']
            else: print(f"Aviso: Atributo '{atributo}' não encontrado.")
        # _atualizar_painel_status() é chamado após wait_window em executar_acao_local
        return True

    def calcular_dano_recebido(self, dano_bruto):
        dano_final = max(1, dano_bruto - self.jogador_atributos['defesa'])
        return dano_final

    def calcular_almas_ganhas(self, almas_base):
        bonus_percent = 0
        if "anel_serpente_prata" in self.jogador_atributos['acessorios_possuidos']:
            item_data = self.loja_acessorios.get("anel_serpente_prata", {})
            bonus_percent += item_data.get('bonus', {}).get('almas_bonus_percent', 0)
        almas_finais = int(almas_base * (1 + bonus_percent))
        return almas_finais

    def iniciar_combate(self, chave_inimigo):
        if self.jogo_terminado: return
        template_inimigo = self.inimigos.get(chave_inimigo)
        if not template_inimigo:
             self._escrever_texto(f"Erro: Tipo de inimigo desconhecido '{chave_inimigo}'")
             self._criar_botoes()
             return

        self.inimigo_atual = template_inimigo.copy()
        self.inimigo_atual['hp_atual'] = self.inimigo_atual['hp'] # Define HP inicial

        # Tenta usar imagem específica do inimigo, senão a de combate genérica
        chave_imagem_inimigo = self.inimigo_atual.get("imagem", "combate")
        self._gerar_e_exibir_imagem(chave_imagem_inimigo)

        self._escrever_texto(f"\n*** CONFRONTO! {self.inimigo_atual['nome']} aparece! ***")

        self._atualizar_interface_inimigo() # Escreve HP do inimigo no texto
        self._criar_botoes() # Cria botões de combate

    def _atualizar_interface_inimigo(self):
         if self.inimigo_atual:
            inimigo = self.inimigo_atual
            hp_texto = f"|| {inimigo['nome']} HP: {inimigo['hp_atual']}/{inimigo['hp']} ||"
            # Adiciona linha separadora
            linha = "-" * (len(hp_texto))
            self._escrever_texto(linha)
            self._escrever_texto(hp_texto)
            self._escrever_texto(linha)

    def processar_acao_jogador(self, tipo_acao, custo=0):
        if not self.inimigo_atual or self.jogo_terminado: return
        ja = self.jogador_atributos
        inimigo = self.inimigo_atual
        if ja['stamina'] < custo:
            self._escrever_texto("Stamina insuficiente!")
            # NÃO gasta turno do inimigo se jogador falhou por stamina
            self._criar_botoes() # Atualiza botões caso stamina regenere
            return

        ja['stamina'] -= custo
        acao_bem_sucedida = True
        jogador_esquivou = False

        if tipo_acao == 'atacar':
            dano_base = random.randint(ja['poder_ataque'] // 2, ja['poder_ataque'])
            defesa_inimigo = inimigo.get('defesa', 0)
            dano_final = max(1, dano_base - defesa_inimigo)
            inimigo['hp_atual'] -= dano_final
            self._escrever_texto(f"Você ataca {inimigo['nome']}, causando {dano_final} de dano ({dano_base} bruto - {defesa_inimigo} def).")
        elif tipo_acao == 'esquivar':
            if random.random() < CHANCE_ESQUIVA:
                self._escrever_texto("Você se esquiva agilmente!")
                jogador_esquivou = True
            else:
                self._escrever_texto("Sua esquiva falha! Você se expõe.")
        elif tipo_acao == 'usar_estus':
            if ja['estus_cargas'] > 0 and ja['hp'] < ja['max_hp']:
                cura = int(ja['max_hp'] * CURA_ESTUS_PERCENTUAL)
                hp_antes = ja['hp']
                ja['hp'] = min(ja['max_hp'], ja['hp'] + cura)
                ja['estus_cargas'] -= 1
                cura_realizada = ja['hp'] - hp_antes
                self._escrever_texto(f"Você bebe do Frasco de Estus (+{cura_realizada} HP).")
                self._atualizar_painel_status()
            elif ja['estus_cargas'] <= 0:
                 self._escrever_texto("Frascos de Estus vazios!")
                 ja['stamina'] += custo # Devolve stamina
                 acao_bem_sucedida = False
            else:
                self._escrever_texto("Seu HP já está no máximo.")
                ja['stamina'] += custo # Devolve stamina
                acao_bem_sucedida = False

        if acao_bem_sucedida:
             self._atualizar_painel_status()

        # Verifica morte do inimigo APÓS ação do jogador
        if inimigo['hp_atual'] <= 0:
            nome_inimigo_derrotado = inimigo['nome'] # Guarda antes de limpar
            almas_base = inimigo['almas']
            almas_ganhas = self.calcular_almas_ganhas(almas_base)
            ja['almas'] += almas_ganhas
            self.inimigo_atual = None # Remove o inimigo
            self._regenerar_stamina(regeneracao_total=True)
            self._atualizar_painel_status()
            self._escrever_texto(f"Você derrotou {nome_inimigo_derrotado}!")
            if almas_ganhas > almas_base:
                 self._escrever_texto(f"Almas absorvidas: {almas_ganhas} (+{almas_ganhas-almas_base} bônus!).")
            else:
                 self._escrever_texto(f"Almas absorvidas: {almas_ganhas}.")

            # Verifica se era o boss para mensagem especial
            if nome_inimigo_derrotado == self.inimigos['vigia_da_ponte']['nome']:
                 self._escrever_texto("\nO grande Vigia tomba com um estrondo. O caminho adiante (ainda não existe) está livre... por ora.\n")
                 # Poderia desbloquear algo aqui (uma nova saída, um item...)

            # Volta a mostrar a imagem do local e botões de exploração
            # Correção: usa a localização ATUAL, não a do inimigo.
            chave_local_atual = self.jogador_atributos["localizacao"]
            dados_local_atual = self.mundo.get(chave_local_atual, {})
            self._gerar_e_exibir_imagem(dados_local_atual.get("imagem", "default"))
            self._criar_botoes()
            return # Fim do combate

        # Turno do Inimigo (se ele sobreviveu e jogador não esquivou)
        if not jogador_esquivou and acao_bem_sucedida: # Inimigo só ataca se ação do jogador foi válida
            self._executar_turno_inimigo()
            if self.jogo_terminado: return # Verifica morte do jogador

        # Se combate continua
        if self.inimigo_atual:
            self._regenerar_stamina(quantidade=STAMINA_REGEN_TURNO)
            self._atualizar_painel_status()
            self._atualizar_interface_inimigo() # Mostra HP atualizado do inimigo
            self._criar_botoes() # Recria botões de combate

    def _executar_turno_inimigo(self):
        if not self.inimigo_atual or self.jogo_terminado: return
        inimigo = self.inimigo_atual
        ja = self.jogador_atributos
        dano_bruto_inimigo = random.randint(inimigo['ataque'] // 2, inimigo['ataque'])
        dano_final_recebido = self.calcular_dano_recebido(dano_bruto_inimigo)
        ja['hp'] -= dano_final_recebido
        self._escrever_texto(f"{inimigo['nome']} ataca, causando {dano_final_recebido} de dano ({dano_bruto_inimigo} bruto - {ja['defesa']} def).")
        self._atualizar_painel_status()
        if ja['hp'] <= 0:
            ja['hp'] = 0
            self._morrer()

    def _regenerar_stamina(self, quantidade=None, regeneracao_total=False):
        if self.jogo_terminado: return
        ja = self.jogador_atributos
        max_stamina = ja['max_stamina']
        stamina_atual = ja['stamina']
        if regeneracao_total:
            ja['stamina'] = max_stamina
        elif quantidade:
            ja['stamina'] = min(max_stamina, stamina_atual + quantidade)
        # Atualização visual ocorre depois via _atualizar_painel_status()

    def _morrer(self):
        # Muda para a imagem de morte
        self._gerar_e_exibir_imagem("morte")
        self._escrever_texto("\n" + "="*10 + " VOCÊ MORREU " + "="*10)
        almas_perdidas = self.jogador_atributos['almas']
        if almas_perdidas > 0:
            self._escrever_texto(f"Sua humanidade se esvai... {almas_perdidas} almas perdidas na escuridão.")
        else:
             self._escrever_texto("A morte tece sua teia novamente...")
        ja = self.jogador_atributos
        ja['almas'] = 0
        ja['localizacao'] = ja['ultimo_santuario']
        ja['hp'] = max(1, ja['max_hp'] // 2)
        ja['stamina'] = ja['max_stamina']
        ja['estus_cargas'] = ja['max_estus']
        self.inimigo_atual = None
        self.jogo_terminado = True # Estado de 'morto', esperando reiniciar
        self._atualizar_painel_status()
        nome_santuario = self.mundo.get(ja['ultimo_santuario'], {}).get("nome", "Santuário")
        self._escrever_texto(f"Os ecos da sua morte te trazem de volta à fogueira de {nome_santuario}.")
        # A imagem de "VOCÊ MORREU" fica até clicar em reiniciar
        self._criar_botoes() # Mostra botão "Reiniciar"

    def reiniciar_jogo(self):
        self.jogo_terminado = False # Pode jogar novamente
        ja = self.jogador_atributos
        # Estado pós-ressurreição na fogueira
        ja['hp'] = ja['max_hp'] # Fogueira restaura completamente ao "reiniciar"
        ja['stamina'] = ja['max_stamina']
        ja['estus_cargas'] = ja['max_estus']
        ja['localizacao'] = ja['ultimo_santuario']
        ja['almas'] = 0 # Já perdeu ao morrer
        self._escrever_texto("\n--- A chama tremeluz. Você se ergue das cinzas mais uma vez. ---")
        self._atualizar_painel_status()
        self.mostrar_localizacao_atual() # Mostra o santuário, imagem correta, botões

# --- Execução Principal ---
if __name__ == "__main__":
    # Não precisamos mais verificar a pasta de imagens
    # if not os.path.isdir(CAMINHO_IMAGENS): ... (removido)

    root = tk.Tk()
    default_font = font.nametofont("TkDefaultFont")
    # Tenta usar uma fonte monoespaçada melhor se disponível
    try:
         default_font.configure(family="Consolas", size=10) # Boa fonte no Windows
    except tk.TclError:
         try:
             default_font.configure(family="DejaVu Sans Mono", size=10) # Boa fonte no Linux
         except tk.TclError:
              default_font.configure(family="Courier New", size=10) # Fallback
    root.option_add("*Font", default_font)

    app = RPGTextoEstiloSouls(root)
    root.mainloop()

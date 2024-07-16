import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from api import Chatbot

from tkhtmlview import HTMLLabel
import markdown2

# Conexión a la base de datos
conn = sqlite3.connect('fitassistant.db')
c = conn.cursor()
cb = Chatbot()
user = None

# Crear tabla de usuarios si no existe
c.execute('''CREATE TABLE IF NOT EXISTS usuarios
             (usuario TEXT PRIMARY KEY, 
              contraseña TEXT, 
              edad INTEGER, 
              sexo TEXT, 
              altura INTEGER, 
              peso REAL, 
              frecuencia TEXT)''')
conn.commit()

# Función para registrar usuario
def registrar_usuario():
    usuario = entry_nuevo_usuario.get()
    contraseña = entry_nueva_contraseña.get()
    edad = int(entry_edad.get())
    sexo = combo_sexo.get()
    altura = int(entry_altura.get())
    peso = float(entry_peso.get())
    frecuencia = combo_frecuencia.get()
    
    c.execute("INSERT INTO usuarios (usuario, contraseña, edad, sexo, altura, peso, frecuencia) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (usuario, contraseña, edad, sexo, altura, peso, frecuencia))
    conn.commit()
    messagebox.showinfo("Registro", "Usuario registrado exitosamente")
    mostrar_menu_principal()

# Función para iniciar sesión

def validar(campos):
    for campo, tipo in campos.items():
        valor = campo.get()
        if not valor:
            messagebox.showerror("Error", f"Todos los campos son obligatorios. Por favor, complete {campo}")
            return False
        
        if tipo == 'int':
            try:
                int(valor)
            except ValueError:
                messagebox.showerror("Error", f"El campo debe ser un número entero")
                return False
        elif tipo == 'float':
            try:
                float(valor)
            except ValueError:
                messagebox.showerror("Error", f"El campo debe ser un número decimal")
                return False
    return True

def iniciar_sesion():
    usuario = entry_usuario.get()
    contraseña = entry_contraseña.get()
    
    c.execute("SELECT * FROM usuarios WHERE usuario=? AND contraseña=?", (usuario, contraseña))
    global user 
    user = c.fetchone()
    
    if user:
        mostrar_planes()
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")

def generate_prompt_ent(edad, sexo, altura, peso, frecuencia, dias_disponibles, horas_disponibles, lugar_ejercicio):     
    promptE = f"Genera un plan de entrenamiento personalizado para un usuario de {edad} años, {sexo}, "\
            + f"con una altura de {altura} cm y un peso de {peso} kg., su frecuencia de ejercicio es {frecuencia}. "\
            + f"El usuario tiene {dias_disponibles} días disponibles para entrenar y prefiere hacer ejercicio "\
            + f"{horas_disponibles} horas al día en {lugar_ejercicio}."

    return promptE
    
def generate_prompt_nut(edad, sexo, altura, peso, objetivo_nutricion, bajar_aumentar):
    promptN = f"Genera un plan de nutrición personalizado para un usuario de {edad} años, {sexo}, "\
            + f"con una altura de {altura} cm y un peso de {peso} kg. El objetivo del usuario es {objetivo_nutricion}. "\
            + f"Basado en su peso y objetivos, recomienda un plan dietético equilibrado que facilite {bajar_aumentar} de peso de manera saludable"
    return promptN


def generar_plan_entrenamiento():
    edad, sexo, altura, peso, frecuencia = user[2], user[3], user[4], user[5], user[6]
    
    campos = {
        combo_dias_disponibles: 'int',
        entry_horas_disponibles: 'float',
        entry_lugar_ejercicio: 'str'
    }
    
    if validar(campos):    
        dias = int(combo_dias_disponibles.get())
        horas = int(entry_horas_disponibles.get())
        lugar = entry_lugar_ejercicio.get()
    else:
        return
    
    prompt = generate_prompt_ent(edad, sexo, altura, peso, frecuencia, dias, horas, lugar)
    res = cb.generate_content(prompt)
    mostrar_respuesta_api(res)

def generar_plan_nutricion():
    edad, sexo, altura, peso = user[2], user[3], user[4], user[5]
    campos = {
        entry_objetivo_nutricion: 'str',
        combo_bajar_aumentar: 'str'
    }
    if validar(campos):
        obj_nut = entry_objetivo_nutricion.get()
        baj_aum = combo_bajar_aumentar.get()
    else:
        return
    
    prompt = generate_prompt_nut(edad, sexo, altura, peso, obj_nut, baj_aum)
    res = cb.generate_content(prompt)
    plan_nutricion = f"Nutrición adecuada para {peso} kg:\n{res}"
    mostrar_respuesta_api(plan_nutricion)

### LOGICA DE INTERFAZ GRAFICA ###

# Función para mostrar la ventana de registro
def mostrar_registro():
    ventana_principal.withdraw()
    centrar_ventana(ventana_registro)
    ventana_registro.deiconify()

# Función para mostrar la ventana principal
def mostrar_menu_principal():
    ventana_registro.withdraw()
    ventana_planes.withdraw()
    centrar_ventana(ventana_principal)
    ventana_principal.deiconify()

# Función para mostrar la ventana de planes
def mostrar_planes():
    ventana_principal.withdraw()
    centrar_ventana(ventana_planes)
    ventana_planes.deiconify()

# Función para mostrar la respuesta de la API
def mostrar_respuesta_api(markdown_text):
    html = markdown2.markdown(markdown_text)
    respuesta_label.set_html(html)

# Función para centrar la ventana
def centrar_ventana(toplevel):
    screen_width = toplevel.winfo_screenwidth()
    screen_height = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = screen_width/2 - size[0]/2
    y = screen_height/2 - size[1]/2

    toplevel.geometry("+%d+%d" % (x, y))

# Configuración de la ventana principal
ventana_principal = tk.Tk()
ventana_principal.title("FitAssistant - Iniciar Sesión")
ventana_principal.configure(bg='lightgreen')
ventana_principal.geometry("230x280")

estilo = ttk.Style()
estilo.configure("frame_izquierdo.TFrame", background='lightgreen')

# Título principal
titulo = ttk.Label(ventana_principal, text="FitAssistant", font=("Helvetica", 24, "bold"), background='lightgreen')
titulo.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

ttk.Label(ventana_principal, text="Usuario:", background='lightgreen').grid(row=1, column=0, padx=10, pady=10)
entry_usuario = ttk.Entry(ventana_principal)
entry_usuario.grid(row=1, column=1, padx=10, pady=10)

ttk.Label(ventana_principal, text="Contraseña:", background='lightgreen').grid(row=2, column=0, padx=10, pady=10)
entry_contraseña = ttk.Entry(ventana_principal, show='*')
entry_contraseña.grid(row=2, column=1, padx=10, pady=10)

ttk.Button(ventana_principal, text="Iniciar Sesión", command=iniciar_sesion).grid(row=3, column=0, columnspan=2, padx=10, pady=10)
ttk.Button(ventana_principal, text="Registrarse", command=mostrar_registro).grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Configuración de la ventana de registro
ventana_registro = tk.Toplevel(ventana_principal)
ventana_registro.title("FitAssistant - Registrarse")
ventana_registro.configure(bg='lightgreen')
ventana_registro.geometry("310x380")
ventana_registro.withdraw()

ttk.Label(ventana_registro, text="Nuevo Usuario:", background='lightgreen').grid(row=0, column=0, padx=10, pady=10)
entry_nuevo_usuario = ttk.Entry(ventana_registro)
entry_nuevo_usuario.grid(row=0, column=1, padx=10, pady=10)

ttk.Label(ventana_registro, text="Nueva Contraseña:", background='lightgreen').grid(row=1, column=0, padx=10, pady=10)
entry_nueva_contraseña = ttk.Entry(ventana_registro, show='*')
entry_nueva_contraseña.grid(row=1, column=1, padx=10, pady=10)

ttk.Label(ventana_registro, text="Edad:", background='lightgreen').grid(row=2, column=0, padx=10, pady=10)
entry_edad = ttk.Entry(ventana_registro)
entry_edad.grid(row=2, column=1, padx=10, pady=10)

ttk.Label(ventana_registro, text="Sexo:", background='lightgreen').grid(row=3, column=0, padx=10, pady=10)
combo_sexo = ttk.Combobox(ventana_registro, values=["Masculino", "Femenino"])
combo_sexo.grid(row=3, column=1, padx=10, pady=10)

ttk.Label(ventana_registro, text="Altura (cm):", background='lightgreen').grid(row=4, column=0, padx=10, pady=10)
entry_altura = ttk.Entry(ventana_registro)
entry_altura.grid(row=4, column=1, padx=10, pady=10)

ttk.Label(ventana_registro, text="Peso (kg):", background='lightgreen').grid(row=5, column=0, padx=10, pady=10)
entry_peso = ttk.Entry(ventana_registro)
entry_peso.grid(row=5, column=1, padx=10, pady=10)

ttk.Label(ventana_registro, text="Frecuencia de Ejercicio:", background='lightgreen').grid(row=6, column=0, padx=10, pady=10)
combo_frecuencia = ttk.Combobox(ventana_registro, values=["Ejercicio regular", "Ejercicio ocasional", "Sedentario"])
combo_frecuencia.grid(row=6, column=1, padx=10, pady=10)

ttk.Button(ventana_registro, text="Guardar", command=registrar_usuario).grid(row=7, column=0, columnspan=2, padx=10, pady=10)
ttk.Button(ventana_registro, text="Volver", command=mostrar_menu_principal).grid(row=8, column=0, columnspan=2, padx=10, pady=10)

# Configuración de la ventana de planes
ventana_planes = tk.Toplevel(ventana_principal)
ventana_planes.title("FitAssistant - Planes")
ventana_planes.configure(bg='lightgreen')
ventana_planes.geometry("1200x600")
ventana_planes.withdraw()

# Frame izquierdo para los inputs
frame_izquierdo = ttk.Frame(ventana_planes, padding="10", style="frame_izquierdo.TFrame")
frame_izquierdo.grid(row=0, column=0, sticky="nsew")

# Frame derecho para la respuesta de la API
frame_derecho = ttk.Frame(ventana_planes, padding="10")
frame_derecho.grid(row=0, column=1, sticky="nsew")

# Configuracion del grid
ventana_planes.columnconfigure(0, weight=1)
ventana_planes.columnconfigure(1, weight=1)
ventana_planes.rowconfigure(0, weight=1)

# Nutrición
lbl_nutricion = ttk.Label(frame_izquierdo, text="PLAN DE NUTRICION", background='lightgreen',font=("Roboto", 16, "bold"))
lbl_nutricion.grid(row=0, column=0, padx=10, pady=10)

ttk.Label(frame_izquierdo, text="Objetivo Nutrición:", background='lightgreen').grid(row=1, column=0, padx=10, pady=10)
entry_objetivo_nutricion = ttk.Entry(frame_izquierdo)
entry_objetivo_nutricion.grid(row=1, column=1, padx=10, pady=10)

ttk.Label(frame_izquierdo, text="Objetivo de Peso:", background='lightgreen').grid(row=2, column=0, padx=10, pady=10)
combo_bajar_aumentar = ttk.Combobox(frame_izquierdo, values=["Bajar", "Aumentar"])
combo_bajar_aumentar.grid(row=2, column=1, padx=10, pady=10)

ttk.Button(frame_izquierdo, text="Generar Plan de Nutrición", command=generar_plan_nutricion).grid(row=3, column=0, padx=10, pady=10)

# Entrenamiento
lbl_entrenamiento = ttk.Label(frame_izquierdo, text="PLAN DE ENTRENAMIENTO", background='lightgreen',font=("Roboto", 16, "bold"))
lbl_entrenamiento.grid(row=4, column=0, padx=10, pady=10)

ttk.Label(frame_izquierdo, text="Días Disponibles:", background='lightgreen').grid(row=5, column=0, padx=10, pady=10)
combo_dias_disponibles = ttk.Combobox(frame_izquierdo, values=[1, 2, 3, 4, 5, 6, 7])
combo_dias_disponibles.grid(row=5, column=1, padx=10, pady=10)

ttk.Label(frame_izquierdo, text="Horas Disponibles:", background='lightgreen').grid(row=6, column=0, padx=10, pady=10)
entry_horas_disponibles = ttk.Entry(frame_izquierdo)
entry_horas_disponibles.grid(row=6, column=1, padx=10, pady=10)

ttk.Label(frame_izquierdo, text="Lugar de Ejercicio:", background='lightgreen').grid(row=7, column=0, padx=10, pady=10)
entry_lugar_ejercicio = ttk.Entry(frame_izquierdo)
entry_lugar_ejercicio.grid(row=7, column=1, padx=10, pady=10)

ttk.Button(frame_izquierdo, text="Generar Plan de Entrenamiento", command=generar_plan_entrenamiento).grid(row=8, column=0, padx=10, pady=10)

# Volver al menú principal
ttk.Button(frame_izquierdo, text="Volver", command=mostrar_menu_principal).grid(row=9, column=0, padx=10, pady=10)

respuesta_label = HTMLLabel(frame_derecho, html="<h2>Plan</h2>")
respuesta_label.pack(side="left",fill="both", expand=True)

scrollbar = ttk.Scrollbar(frame_derecho, orient="vertical", command=respuesta_label.yview)
scrollbar.pack(side="right", fill="y")

respuesta_label.configure(yscrollcommand=scrollbar.set)


centrar_ventana(ventana_principal)
ventana_principal.mainloop()
conn.close()

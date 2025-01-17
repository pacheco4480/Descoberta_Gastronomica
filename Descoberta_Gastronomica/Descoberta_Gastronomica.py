from tkinter import Tk, Canvas, ttk
import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO
from yelpapi import YelpAPI
import random
from threading import Thread
from functools import lru_cache
import webbrowser

# ============================================================
#
# Criação da janela principal e configurações de aparência.
# Carregamento das imagens necessárias.
# Criação da instância da classe YelpAPI.
# Funçoes auxiliares.
#
# ============================================================

# Criação da janela
window = Tk()
window.geometry("360x640")
canvas = Canvas(window, bg="#ffffff", height=640, width=360, bd=0, highlightthickness=0, relief="ridge")
canvas.pack(fill="both", expand=True)
window.title("Descoberta Gastronómica")


# Impede o redimensionamento da janela
window.resizable(False, False)


# Carregamento das imagens
background_img = Image.open("background.png")
background_photo = ImageTk.PhotoImage(background_img)
img0 = Image.open("img0.png")
image0 = ImageTk.PhotoImage(img0)
img1 = Image.open("img1.png")
image1 = ImageTk.PhotoImage(img1)
frame_img = Image.open("frame.png")
frame_photo = ImageTk.PhotoImage(frame_img)


# Exibe a imagem de fundo na posição (0, 0) do ecran e a imagem frame
canvas.create_image(0, 0, anchor="nw", image=background_photo)
canvas.create_image(28, 100, anchor="nw", image=frame_photo)

# Cria retângulos (elementos interativos) com as imagens nas posições ecolhidas
b0 = canvas.create_image(48, 120, anchor="nw", image=image0)
canvas.tag_bind(b0, "<Button-1>", lambda event: show_restaurant_images())


# Criação da instância da classe YelpAPI
yelp_api = YelpAPI('Xqgcra2ipmzUBe9-1CjknpKUNbXaVTd7grHNkBmIum471eg30KbMDCSjcm42y1XQynCZGb-jHRmGPqePvyNa7SLACIDLKm9szEwUBk6wLwc3agWaIltJ1ad3ClWPZHYx', timeout_s=3.0)


# Definir cache de imagem
@lru_cache(maxsize=128)
def load_image(url):
    try:
        response = requests.get(url)
        image_data = response.content
        image = Image.open(BytesIO(image_data))
        return image.resize((270, 270), Image.LANCZOS)
    except (requests.exceptions.RequestException, OSError):
        # Retorna uma imagem padrão se a URL não for válida ou o carregamento da imagem falhar
        default_image = Image.open("default_image.png")
        return default_image.resize((270, 270), Image.LANCZOS)


# Abre a página web de um restaurante específico
def open_restaurant_page(restaurant_url):
    webbrowser.open(restaurant_url)



# ============================================================
#
# Funçao principal
#
# ============================================================




def show_restaurant_images():
    localizacao_selecionada = location_selection_box.get()
    genero_selecionado = genre_selection_box.get()
    
    if localizacao_selecionada == 'Random':
        localizacoes_validas = [location for location in portuguese_locations if location != 'Random']
        localizacao_selecionada = random.choice(localizacoes_validas)
    
    if genero_selecionado == 'Random':
        genero_selecionado = random.choice(restaurant_genres)
    else:
        # Remove a opção "Random" da lista de gêneros antes de realizar a pesquisa
        restaurant_genres_without_random = [genre for genre in restaurant_genres if genre != 'Random']
        if genero_selecionado not in restaurant_genres_without_random:
            genero_selecionado = random.choice(restaurant_genres_without_random)


    
    # Consultam a API do Yelp para obter restaurantes aleatórios com base no gênero e localização selecionados
    response = yelp_api.search_query(term=genero_selecionado, location=localizacao_selecionada, limit=15)
    businesses = response['businesses']
    random.shuffle(businesses)


######################################
    
# Se não houver resultados, a função remove exibições anteriores, exibe uma imagem indicando a ausência de resultados e encerra a função.
    if not businesses:
        # Remove a exibição anterior, se houver
        canvas.delete("restaurant_images")
        canvas.delete("restaurant_images_text")  # Remove o nome do restaurante
        canvas.delete("hyperlink")  # Remove o botão "Ver mais"
        canvas.delete("refresh_button_tag")  # Remove o botão de atualização
        canvas.delete("stars_id")  # Remove as estrelas anteriores

        # Carregua e exibe a imagem sem resultados
        no_results_image = canvas.create_image(48, 120, anchor="nw", image=image1)
        
        
        # Exibe o texto sem resultados
        no_results_text = "Nenhum resultado encontrado."
        canvas.create_text(180, 460, text=no_results_text, fill="#000000", font=("Arial", 18), tags="restaurant_images_text")

        refresh_button = ttk.Button(window, text="Atualizar", command=show_restaurant_images, style="Refresh.TButton")
        style.configure("Refresh.TButton", foreground="#000000", background="#000000", font=("Helvetica", 12))
        style.map("Refresh.TButton",
          foreground=[("active", "#000000"), ("!active", "#ffffff")],
          background=[("active", "#ffffff"), ("!active", "#000000")])
        refresh_button_tag = "refresh_button_tag"  # Define a tag
        canvas.create_window(55, 435, anchor="w", window=refresh_button, tags=refresh_button_tag)

        
        canvas.update()
        return  # Sai da função se não houver resultados


######################################
  
    # Coleta os URLs das imagens e os nomes dos restaurantes
    image_urls = [business['image_url'] for business in businesses]
    restaurant_names = [business['name'] for business in businesses]
    
    # Remove a exibição anterior, se houver
    canvas.delete("restaurant_images")
    canvas.delete("restaurant_images_text")  # Remove o nome do restaurante
    canvas.delete("hyperlink")  # Remove o botão "Ver mais"
    canvas.delete("refresh_button_tag")  # Remove o botão de atualização
    canvas.delete("stars_id")  # Remove as estrelas anteriores
    
    # Mostra as imagens e nomes num carrossel
    for i, (url, name) in enumerate(zip(image_urls, restaurant_names)):
        image = load_image(url)
        photo = ImageTk.PhotoImage(image)
        canvas.create_image(48, 120, anchor="nw", image=photo, tags="restaurant_images")
        
        # Mostra o nome do restaurante abaixo da foto
        text_id = canvas.create_text(180, 460, text=name, fill="#000000", font=("Arial", 18), tags="restaurant_images_text")

######################################

        # Mostra as estrelas das reviews
        stars_id = [] 

        # Carrega as imagens PNG
        empty_star_img = Image.open("empty_star.png")
        full_star_img = Image.open("full_star.png")
        half_star_img = Image.open("half_star.png")

        # Redimensiona as imagens para caber no tamanho desejado
        star_width = 20  # Define a largura desejada das estrelas
        star_height = 20  # Define a altura desejada das estrelas

        # Redimensiona as imagens para caber no tamanho desejado
        empty_star_img = empty_star_img.resize((star_width, star_height), Image.LANCZOS)
        full_star_img = full_star_img.resize((star_width, star_height), Image.LANCZOS)
        half_star_img = half_star_img.resize((star_width, star_height), Image.LANCZOS)


        # Cria objetos de imagem compatíveis com Tkinter
        empty_star_tk = ImageTk.PhotoImage(empty_star_img)
        full_star_tk = ImageTk.PhotoImage(full_star_img)
        half_star_tk = ImageTk.PhotoImage(half_star_img)


        # Mostre as imagens, nomes e avaliações num carrossel
        rating = businesses[i]['rating']


        # Calcula o número de estrelas preenchidas
        filled_stars = int(rating)

        # Calcula o número de estrelas vazias
        empty_stars = 5 - filled_stars

        # Calcula o número de estrelas meio cheias
        if rating - filled_stars >= 0.5:
            half_filled_stars = 1
        else:
            half_filled_stars = 0

        # Cria uma lista para conter as imagens das estrelas
        stars_images = []

        # Adiciona as estrelas completas
        for _ in range(filled_stars):
            stars_images.append(full_star_tk)

        # Adiciona uma estrela meio cheia, se aplicável
        if half_filled_stars == 1:
            stars_images.append(half_star_tk)

        # Adiciona estrelas vazias
        for _ in range(empty_stars):
            stars_images.append(empty_star_tk)


        # Calcula a coordenada x para cada imagem de estrela
        start_x = 180 - (len(stars_images) * star_width // 2)

        # Exibe as estrelas abaixo do nome do restaurante
        stars_ids = []
        for i, star_image in enumerate(stars_images):
            star_id = canvas.create_image(start_x + (i * star_width), 485, image=star_image, anchor="center", tags="stars_id")
            stars_ids.append(star_id)

        # Remove as estrelas anteriores se houver apenas um restaurante
        if len(restaurant_names) == 1:
            canvas.delete(stars_ids[0])

        # Atualiza a exibição do canvas
        canvas.update()


######################################
        
        canvas.update()
        canvas.after(500)  # Exibe cada imagem por 0,5 segundos
        
        # Verifica se não é o último restaurante na lista e remove o seguinte:
        if i != len(restaurant_names) - 1:
            canvas.delete(text_id)  # Remove o nome do restaurante se não for o último
            canvas.delete(stars_id)  # Remove as estrelas se não for a última
            if i < len(businesses):
                rest_url = businesses[i]['url']  # Obter a URL do restaurante
            else:
                rest_url = ''  # Define a URL como vazia se o índice estiver fora do intervalo

######################################
            

# Adicionar hiperlink ao último restaurante
    # Mostra o botão "Ver mais" apenas na última imagem
    last_text_id = canvas.create_text(180, 460, text=restaurant_names[-1], fill="#000000", font=("Arial", 18), tags="restaurant_images_text")
    if len(restaurant_names) > 1:
        # Mostra o botão "Ver mais" apenas na última imagem
        rest_url = businesses[-1]['url']
        last_text_id = canvas.create_text(180, 460, text=restaurant_names[-1], fill="#000000", font=("Arial", 18), tags="restaurant_images_text")
        canvas.create_text(245, 430, text="Ver mais", fill="blue", font=("Arial", 12, "underline", "bold"), anchor="w", tags="hyperlink")
        canvas.tag_bind("hyperlink", "<Button-1>", lambda event: open_restaurant_page(rest_url))
    else:
        # Se houver apenas uma imagem, exibe o nome do restaurante abaixo dela
        last_text_id = canvas.create_text(180, 460, text=restaurant_names[0], fill="#000000", font=("Arial", 18), tags="restaurant_images_text")
        

######################################

# Adicionar botão de atualização
    refresh_button = ttk.Button(window, text="Atualizar", command=show_restaurant_images, style="Refresh.TButton")
    style.configure("Refresh.TButton", foreground="#000000", background="#000000", font=("Helvetica", 12))
    style.map("Refresh.TButton",
              foreground=[("active", "#000000"), ("!active", "#ffffff")],
              background=[("active", "#ffffff"), ("!active", "#000000")])
    refresh_button_tag = "refresh_button_tag"  # Defina a tag desejada
    canvas.create_window(55, 430, anchor="w", window=refresh_button, tags=refresh_button_tag)

######################################

    # Continua a exibir a última imagem e o nome
    while True:
        canvas.update()


######################################
    
# ============================================================
#
# Caixas de seleção
#
# ============================================================


style = ttk.Style()
style.theme_create("custom_style", parent="alt",
                   settings={
                       "TCombobox": {
                           "configure": {
                               "foreground": "#ffffff",
                               "background": "#000000",
                               "fieldbackground": "#000000",
                               "selectbackground": "#000000",
                               "selectforeground": "#ffffff"
                           },
                           "map": {
                               "foreground": [("readonly", "#ffffff"), ("!readonly", "#000000")],
                               "background": [("readonly", "#000000"), ("!readonly", "#ffffff")],
                               "arrowcolor": [("readonly", "#ffffff"), ("!readonly", "#000000")],
                               "selectforeground": [("readonly", "#ffffff")],
                               "selectbackground": [("readonly", "#000000")]
                           }
                       }
                   })
style.theme_use("custom_style")

# Cria a caixa de seleção de localização
portuguese_locations = ['Aveiro', 'Beja', 'Braga', 'Bragança', 'Castelo Branco', 'Coimbra', 'Évora', 'Faro', 'Guarda', 'Leiria', 'Lisboa', 'Portalegre', 'Porto', 'Santarém', 'Setúbal', 'Viana do Castelo', 'Vila Real', 'Viseu', 'Açores', 'Madeira']
portuguese_locations.append('Random')  # Adiciona a opção "Random"
location_selection_box = ttk.Combobox(window, values=portuguese_locations, state="readonly", width=14, height=17)
location_selection_box.set(portuguese_locations[0])  # Define o valor padrão
location_selection_box.configure(font=("Helvetica", 12))  # Define a fonte e o tamanho da letra
location_selection_box.pack()
location_selection_box.place(x=8, y=535)

# Cria a caixa de seleção de gênero de restaurantes
restaurant_genres = ['Italiano', 'Japonês', 'Chinês', 'Mexicano', 'Brasileiro', 'Português', 'Frutos do Mar', 'Fast Food', 'Vegetariano', 'Buffet', 'Pizzaria', 'Café', 'Hambúrguer', 'Churrascaria', 'Indiana', 'Sushi', 'Tailandês', 'Grego', 'Espanhol', 'Cozinha Internacional']
restaurant_genres.append('Random')  # Adiciona a opção "Random"
genre_selection_box = ttk.Combobox(window, values=restaurant_genres, state="readonly", width=14, height=17)
genre_selection_box.set(restaurant_genres[0])  # Define o valor padrão
genre_selection_box.configure(font=("Helvetica", 12))  # Define a fonte e o tamanho da letra
genre_selection_box.pack()
genre_selection_box.place(x=210, y=535)

# Cria o texto no ecran
canvas.create_text(80, 515, anchor="center", text="Localização", fill="#000000", font=("Helvetica", 12, "bold"))
canvas.create_text(280, 515, anchor="center", text="Gênero", fill="#000000", font=("Helvetica", 12, "bold"))




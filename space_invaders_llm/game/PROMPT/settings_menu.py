import pygame
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from common.difficulty_settings import DIFFICULTY_SETTINGS

def Settings():
    pygame.init()
    schermo = pygame.display.set_mode((600, 750))  # Schermo più compatto
    pygame.display.set_caption("Seleziona Difficoltà e Mappa")
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)

    # Opzioni di difficoltà
    difficolta_opzioni = ["Facile", "Media", "Difficile", "Molto Difficile"]
    difficolta_bottoni = []
    difficolta_selezionata = None

    # Opzioni per la mappa
    mappa_opzioni = ["Si", "No"]
    mappa_bottoni = []
    mappa_selezionata = None

    # Box informazioni in fondo alla schermata
    info_box = pygame.Rect(50, 600, 500, 100)
    info_text = "Nessuna difficoltà selezionata"

    # Calcolo e creazione dei rettangoli per i bottoni di difficoltà
    larghezza_bottone = 220
    altezza_bottone = 50
    spazio_tra_bottoni = 15
    y_iniziale = 80

    for i, testo in enumerate(difficolta_opzioni):
        x = schermo.get_width() // 2 - larghezza_bottone // 2
        y = y_iniziale + i * (altezza_bottone + spazio_tra_bottoni)
        rett = pygame.Rect(x, y, larghezza_bottone, altezza_bottone)
        difficolta_bottoni.append((rett, testo))

    # Linea orizzontale sotto "Molto Difficile"
    linea_y = y_iniziale + len(difficolta_opzioni) * (altezza_bottone + spazio_tra_bottoni) + 20

    # Calcolo e creazione dei rettangoli per i bottoni di mappa
    y_iniziale_mappa = linea_y + 50  # Posizione dopo la linea

    for i, testo in enumerate(mappa_opzioni):
        x = schermo.get_width() // 2 - larghezza_bottone // 2
        y = y_iniziale_mappa + i * (altezza_bottone + spazio_tra_bottoni)
        rett = pygame.Rect(x, y, larghezza_bottone, altezza_bottone)
        mappa_bottoni.append((rett, testo))

    # Linea orizzontale sotto "No" - stessa altezza della prima linea
    linea2_y = y_iniziale_mappa + len(mappa_opzioni) * (altezza_bottone + spazio_tra_bottoni) + 20

    while True:
        mouse_pos = pygame.mouse.get_pos()
        schermo.fill((30, 30, 30))

        # Titolo difficoltà
        titolo_diff = font.render("Seleziona Difficoltà", True, (255, 255, 255))
        schermo.blit(titolo_diff, (schermo.get_width() // 2 - titolo_diff.get_width() // 2, 40))

        # Disegna bottoni difficoltà
        for i, (rett, testo) in enumerate(difficolta_bottoni):
            # Disabilita solo il bottone "Molto Difficile" (indice 3)
            disabilitato = (testo == "Molto Difficile")
            
            colore_bottone, colore_bordo, colore_testo = get_button_colors(rett, mouse_pos, disabilitato)
            
            if disabilitato:
                s = pygame.Surface((rett.width, rett.height), pygame.SRCALPHA)
                pygame.draw.rect(s, colore_bottone, (0, 0, rett.width, rett.height), border_radius=8)
                pygame.draw.rect(s, colore_bordo, (0, 0, rett.width, rett.height), 2, border_radius=8)
                schermo.blit(s, rett)
            else:
                pygame.draw.rect(schermo, colore_bottone, rett, border_radius=8)
                pygame.draw.rect(schermo, colore_bordo, rett, 2, border_radius=8)

            testo_render = font.render(testo, True, colore_testo)
            schermo.blit(testo_render, (rett.centerx - testo_render.get_width() // 2, 
                                   rett.centery - testo_render.get_height() // 2))

        # Linea divisoria dopo difficoltà (spessore 2)
        pygame.draw.line(schermo, (80, 80, 80), (50, linea_y), (550, linea_y), 2)

        # Titolo e bottoni mappa
        titolo_mappa = font.render("Inserire mappa manualmente?", True, (255, 255, 255))
        schermo.blit(titolo_mappa, (schermo.get_width() // 2 - titolo_mappa.get_width() // 2, linea_y + 10))

        # Disegna bottoni mappa (abilitati solo se difficoltà è selezionata)
        for rett, testo in mappa_bottoni:
            disabilitato_reale = difficolta_selezionata is None
            
            colore_bottone, colore_bordo, colore_testo = get_button_colors(rett, mouse_pos, disabilitato_reale)
            
            if disabilitato_reale:
                s = pygame.Surface((rett.width, rett.height), pygame.SRCALPHA)
                pygame.draw.rect(s, colore_bottone, (0, 0, rett.width, rett.height), border_radius=8)
                pygame.draw.rect(s, colore_bordo, (0, 0, rett.width, rett.height), 2, border_radius=8)
                schermo.blit(s, rett)
            else:
                pygame.draw.rect(schermo, colore_bottone, rett, border_radius=8)
                pygame.draw.rect(schermo, colore_bordo, rett, 2, border_radius=8)

            testo_render = font.render(testo, True, colore_testo)
            schermo.blit(testo_render, (rett.centerx - testo_render.get_width() // 2, 
                                     rett.centery - testo_render.get_height() // 2))

        # Linea divisoria dopo mappa (stesso spessore della prima linea)
        pygame.draw.line(schermo, (80, 80, 80), (50, linea2_y), (550, linea2_y), 2)

        # Box informazioni in fondo
        pygame.draw.rect(schermo, (50, 50, 70), info_box, border_radius=8)
        pygame.draw.rect(schermo, (80, 80, 100), info_box, 2, border_radius=8)
        
        # Mostra solo la difficoltà selezionata nel box
        info_surface = font.render(info_text, True, (255, 255, 255))
        schermo.blit(info_surface, (info_box.centerx - info_surface.get_width() // 2, 
                                  info_box.centery - info_surface.get_height() // 2))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # click sinistro
                    # Controlla i bottoni di difficoltà (ignora "Molto Difficile")
                    for rett, testo in difficolta_bottoni:
                        if rett.collidepoint(evento.pos) and testo != "Molto Difficile":
                            difficolta_selezionata = testo.lower()
                            info_text = f"Difficoltà: {testo}"
                    
                    # Controlla i bottoni di mappa (solo se difficoltà è selezionata)
                    if difficolta_selezionata is not None:
                        for rett, testo in mappa_bottoni:
                            if rett.collidepoint(evento.pos):
                                mappa_selezionata = testo.lower()
                                pygame.time.delay(300)  # Piccola pausa per visualizzare la selezione
                                return difficolta_selezionata, mappa_selezionata

def get_button_colors(rett, mouse_pos, disabilitato):
    if disabilitato:
        return (100, 100, 100, 128), (80, 80, 80, 128), (200, 200, 200, 128)
    else:
        if rett.collidepoint(mouse_pos):
            return (80, 80, 180), (100, 100, 200), (255, 255, 255)
        else:
            return (70, 70, 120), (90, 90, 140), (255, 255, 255)
        
def SetMap(difficulty):
    settings = DIFFICULTY_SETTINGS.get(difficulty.lower())
    if not settings:
        raise ValueError(f"Difficoltà non riconosciuta: {difficulty}")

    screen_width = settings["screen_width"]
    screen_height = settings["screen_height"]
    num_enemies = settings["num_enemies"]
    allowed_enemy_rows = settings["enemy_rows"]
    cell_size = 50  # Aumentato per migliore visibilità

    cols = screen_width // cell_size
    rows = screen_height // cell_size - 3  # Più spazio per i bottoni

    grid = [[0 for _ in range(cols)] for _ in range(rows)]

    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Editor Mappa Nemici")
    font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()

    enemy_count = 0
    running = True

    # Calcola la posizione della griglia per centrarla
    grid_width = cols * cell_size
    grid_height = rows * cell_size
    grid_offset_x = (screen_width - grid_width) // 2
    grid_offset_y = 80  # Più spazio sopra per titolo e informazioni

    # Crea bottoni più belli
    button_width, button_height = 150, 45
    button_y = screen_height - 70
    
    back_button = pygame.Rect(20, button_y, button_width, button_height)
    reset_button = pygame.Rect(screen_width//2 - button_width//2, button_y, button_width, button_height)
    proceed_button = pygame.Rect(screen_width - button_width - 20, button_y, button_width, button_height)

    while running:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill((40, 40, 50))  # Sfondo leggermente più chiaro

        # Titolo
        title = font.render("Posiziona i Nemici", True, (255, 255, 255))
        screen.blit(title, (screen_width//2 - title.get_width()//2, 20))

        # Informazioni
        info_text = font.render(f"Nemici: {enemy_count}/{num_enemies} (Minimo: 1)", True, (255, 255, 255))
        screen.blit(info_text, (screen_width//2 - info_text.get_width()//2, 50))

        # Disegna area della griglia con bordo
        pygame.draw.rect(screen, (70, 70, 90), 
                        (grid_offset_x-5, grid_offset_y-5, 
                         grid_width+10, grid_height+10), 
                         border_radius=5)
        
        # Disegna griglia con celle più belle
        for y in range(rows):
            for x in range(cols):
                rect = pygame.Rect(
                    grid_offset_x + x * cell_size, 
                    grid_offset_y + y * cell_size, 
                    cell_size, cell_size
                )

                is_valid_cell = (y < allowed_enemy_rows) and (2 <= x < cols - 2)
                
                # Colori delle celle
                if grid[y][x] == 1:  # Nemico
                    color = (220, 50, 50)  # Rosso acceso
                    border_color = (180, 30, 30)
                elif is_valid_cell:  # Cella valida
                    color = (100, 200, 100)  # Verde chiaro
                    border_color = (80, 180, 80)
                else:  # Cella non valida
                    color = (100, 100, 120)  # Grigio bluastro
                    border_color = (80, 80, 100)

                # Disegna cella con bordo arrotondato
                pygame.draw.rect(screen, color, rect, border_radius=3)
                pygame.draw.rect(screen, border_color, rect, 2, border_radius=3)

                # Mostra un'icona per i nemici
                if grid[y][x] == 1:
                    enemy_icon = font.render("X", True, (255, 255, 255))
                    screen.blit(enemy_icon, (
                        rect.centerx - enemy_icon.get_width()//2,
                        rect.centery - enemy_icon.get_height()//2
                    ))

        # Funzione per disegnare bottoni consistenti
        def draw_button(rect, text, base_color, hover_color):
            color = hover_color if rect.collidepoint(mouse_pos) else base_color
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, (60, 60, 80), rect, 2, border_radius=8)
            
            text_surf = font.render(text, True, (255, 255, 255))
            screen.blit(text_surf, (
                rect.centerx - text_surf.get_width()//2,
                rect.centery - text_surf.get_height()//2
            ))

        # Disegna bottoni
        draw_button(back_button, "Indietro", (150, 80, 80), (180, 100, 100))
        draw_button(reset_button, "Reset", (80, 80, 150), (100, 100, 180))
        draw_button(proceed_button, "Conferma", (80, 150, 80), (100, 180, 100))

        # Istruzioni
        instructions = font.render("Clicca sulle celle verdi per posizionare i nemici", True, (200, 200, 255))
        screen.blit(instructions, (screen_width//2 - instructions.get_width()//2, screen_height - 120))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Controlla click sulla griglia
                if (grid_offset_x <= event.pos[0] < grid_offset_x + grid_width and
                    grid_offset_y <= event.pos[1] < grid_offset_y + grid_height):
                    
                    gx = (event.pos[0] - grid_offset_x) // cell_size
                    gy = (event.pos[1] - grid_offset_y) // cell_size
                    
                    if (gy < allowed_enemy_rows) and (2 <= gx < cols - 2):
                        if grid[gy][gx] == 0:
                            grid[gy][gx] = 1
                            enemy_count += 1
                        elif grid[gy][gx] == 1:
                            grid[gy][gx] = 0
                            enemy_count -= 1

                # Controlla click sui bottoni
                elif back_button.collidepoint(event.pos):
                    return None  # Torna indietro senza salvare
                
                elif reset_button.collidepoint(event.pos):
                    grid = [[0 for _ in range(cols)] for _ in range(rows)]
                    enemy_count = 0
                
                elif proceed_button.collidepoint(event.pos):
                    if enemy_count >= 1:  # Almeno un nemico richiesto
                        running = False
                    else:
                        # Avvisa se non ha piazzato nessun nemico
                        warning = font.render("Devi piazzare almeno un nemico!", True, (255, 100, 100))
                        screen.blit(warning, (screen_width//2 - warning.get_width()//2, screen_height - 150))
                        pygame.display.flip()
                        pygame.time.delay(1500)  # Mostra l'avviso per 1.5 secondi
        clock.tick(60)
 
    # Trasforma i valori numerici in caratteri 'A' per nemici, '0' per vuoti
    final_grid = [['A' if cell == 1 else '0' for cell in row] for row in grid]

    # Inserisce il giocatore (P) al centro dell'ultima riga
    player_col = len(final_grid[0]) // 2
    final_grid[-1][player_col] = 'P'

    # Stampa la griglia finale
    #for row in final_grid:
        #print(' '.join(row))

    pygame.quit()
    return grid
import pygame

pygame.init()

# Krāsas
WHT = (255, 255, 255)
BLK = (0, 0, 0)
GRY = (100, 100, 100)
LGRY = (150, 150, 150)
W98 = (200, 157, 124)
DW98 = (125, 102, 93)
DRED = (50, 0, 0)
RED = (255, 0, 0)

# Loga izmērs
DWIDTH, DHEIGHT = 800, 600

screen = pygame.display.set_mode((DWIDTH, DHEIGHT))
pygame.display.set_caption("Mācību ekskursija Liepājā")
clock = pygame.time.Clock()

# Fonti
titlefont = pygame.font.Font("freesansbold.ttf", 60)
btnfont = pygame.font.Font("freesansbold.ttf", 40)
txtfont = pygame.font.Font("freesansbold.ttf", 35)
smalltxtfont = pygame.font.Font("freesansbold.ttf", 20)

# Spēles dati
score = 0
points = 5
visited = [False] * 10
map_x, map_y = -350, 0


# ---------- Palīgfunkcijas ----------

def quit_game():
    pygame.quit()
    raise SystemExit


def draw_score():
    score_text = smalltxtfont.render(f"Punkti: {score}", True, BLK)
    pygame.draw.rect(screen, LGRY, (10, 10, 150, 40))
    screen.blit(score_text, (15, 15))


def draw_center_text(text, font, color, x, y):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y))
    screen.blit(surf, rect)


def draw_text(text, font, color, x, y):
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))


def read_results():
    try:
        with open("results.txt", "r", encoding="utf-8") as file:
            return file.readline().strip()
    except FileNotFoundError:
        return "Rezultātu vēl nav."


def save_results():
    with open("results.txt", "w", encoding="utf-8") as file:
        file.write(f"Punkti: {score}")


# ---------- Klases ----------

class Button:
    def __init__(self, x, y, w, h, text="", idle_color=LGRY, hover_color=GRY, font=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.idle_color = idle_color
        self.hover_color = hover_color
        self.font = font or btnfont

    def draw(self):
        mouse = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse) else self.idle_color
        pygame.draw.rect(screen, color, self.rect)
        if self.text:
            text_surf = self.font.render(self.text, True, BLK)
            screen.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


class MapPoint:
    def __init__(self, map_x, map_y, name, level_index):
        self.map_x = map_x
        self.map_y = map_y
        self.name = name
        self.level_index = level_index
        self.size = 20

    def get_rect(self, offset_x, offset_y):
        return pygame.Rect(offset_x + self.map_x, offset_y + self.map_y, self.size, self.size)

    def draw(self, offset_x, offset_y):
        if visited[self.level_index]:
            return
        rect = self.get_rect(offset_x, offset_y)
        mouse = pygame.mouse.get_pos()
        color = RED if rect.collidepoint(mouse) else DRED
        pygame.draw.rect(screen, color, rect)

    def hovered(self, offset_x, offset_y):
        return self.get_rect(offset_x, offset_y).collidepoint(pygame.mouse.get_pos())


class Level:
    def __init__(self, name, info_lines, q_index, ans_index, posans_index, image_path=None):
        self.name = name
        self.info_lines = info_lines
        self.q_index = q_index
        self.ans_index = ans_index
        self.posans_index = posans_index
        self.image_path = image_path

    def leveldata(self):
        with open("data.txt", "r", encoding="utf-8") as file:
            content = file.readlines()

        question = content[self.q_index].strip()
        possible_answers = content[self.posans_index].strip().split(",")
        correct_answer = content[self.ans_index].strip()
        return question, [a.strip() for a in possible_answers], correct_answer

    def show_info(self):
        while True:
            mouse_back = False
            start_button = Button(DWIDTH // 4 - 60, 360, 150, 50, "Sākt")
            back_button = Button(DWIDTH // 2 + 120, 360, 160, 50, "Atpakaļ")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()
                if start_button.clicked(event):
                    return self.play_question()
                if back_button.clicked(event):
                    mouse_back = True

            if mouse_back:
                return False

            pygame.draw.rect(screen, DW98, (DWIDTH // 4 - 75, 50, 570, 375))
            draw_text(self.name, txtfont, BLK, DWIDTH // 4 - 60, 60)

            y = 100
            for line in self.info_lines:
                draw_text(line, smalltxtfont, BLK, DWIDTH // 4 - 60, y)
                y += 25

            # Attēls zem informācijas teksta
            if self.image_path:
                try:
                    place_img = pygame.image.load(self.image_path).convert()
                    place_img = pygame.transform.scale(place_img, (260, 150))
                    screen.blit(place_img, (DWIDTH // 2 - 130, 195))
                except pygame.error:
                    draw_text("Attēls nav atrasts", smalltxtfont, RED, DWIDTH // 2 - 95, 250)

            start_button.draw()
            back_button.draw()
            draw_score()
            pygame.display.update()
            clock.tick(30)

    def penalty(self):
        global points
        if points > 1:
            points -= 2
        if points < 1:
            points = 1

    def addscore(self):
        global score, points
        score += points
        points = 5

    def play_question(self):
        question, possible_answers, correct_answer = self.leveldata()
        show_wrong = False

        while True:
            answer_buttons = [
                Button(50, 500, 200, 50, possible_answers[0]),
                Button(300, 500, 200, 50, possible_answers[1]),
                Button(580, 500, 199, 50, possible_answers[2]),
            ]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()

                for i, btn in enumerate(answer_buttons):
                    if btn.clicked(event):
                        if possible_answers[i] == correct_answer:
                            self.addscore()
                            return True
                        else:
                            show_wrong = True
                            self.penalty()

            screen.fill(W98)
            draw_text(question, txtfont, BLK, DWIDTH // 6, DHEIGHT // 6)

            if show_wrong:
                wrong_text = txtfont.render("Nepareizi! Mēģiniet vēlreiz!", True, RED)
                screen.blit(wrong_text, (DWIDTH // 6 + 50, DHEIGHT // 2 + 50))

            for btn in answer_buttons:
                btn.draw()

            draw_score()
            pygame.display.update()
            clock.tick(30)


# ---------- Ekrāni ----------

def title_screen():
    while True:
        start_btn = Button(DWIDTH // 2 - 150, 225, 250, 50, "Sākt Spēli")
        result_btn = Button(DWIDTH // 2 - 150, 330, 250, 50, "Rezultāti")
        about_btn = Button(30, 500, 205, 50, "Par Spēli")
        exit_btn = Button(630, 500, 120, 50, "Iziet")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if start_btn.clicked(event):
                start_popup()
            if result_btn.clicked(event):
                results_screen()
            if about_btn.clicked(event):
                about_screen()
            if exit_btn.clicked(event):
                exit_popup()

        screen.fill(W98)
        draw_center_text("Mācību Ekskursija Liepājā", titlefont, BLK, DWIDTH // 2, DHEIGHT // 6)
        draw_text("Lai sāktu ekskursiju uzspiediet pogu 'Sākt Spēli'!", smalltxtfont, BLK, DWIDTH // 2 - 225, 150)
        draw_text("Autors: 'Binārais Trio', 2026", smalltxtfont, BLK, 525, 580)

        start_btn.draw()
        result_btn.draw()
        about_btn.draw()
        exit_btn.draw()

        pygame.display.update()
        clock.tick(30)


def about_screen():
    while True:
        back_btn = Button(430, 500, 325, 50, "Galvenā Izvēlne")
        start_btn = Button(50, 500, 150, 50, "Karte")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if back_btn.clicked(event):
                return
            if start_btn.clicked(event):
                ingame_map()
                return

        screen.fill(W98)
        draw_center_text("Par Spēli", titlefont, BLK, DWIDTH // 2, DHEIGHT // 6)

        lines = [
            "Lai kustinātu karti izmantojiet bultiņu pogas uz savas klaviatūras",
            "Lai sāktu uzdevumu uzklikšķiniet uz vienu no sarkanajiem kvadrātiem",
            "Par katru pareizo atbildi tiek doti 5 punkti",
            "Kļūdoties 1 reizi saņem 3 punktus un kļūdoties 2 reizes saņem tikai 1 punktu.",
            "Spēli veidoja Pēteris Poļikovs, Ella Jēkabsone un Valters Jūrmalis",
            "Karte ņemta no https://anvaka.github.io/city-roads/?q=Liepāja&areaId=3613048685",
            "Info par apskates vietām:",
            "https://liepaja.travel/",
            "https://www.karosta.lv/",
            "https://www.liepajasmuzejs.lv/",
        ]

        y = DHEIGHT // 6 + 50
        for line in lines:
            draw_text(line, smalltxtfont, BLK, 10, y)
            y += 20

        back_btn.draw()
        start_btn.draw()

        pygame.display.update()
        clock.tick(30)


def start_popup():
    while True:
        yes_btn = Button(DWIDTH // 4 - 15, 360, 70, 50, "Jā")
        rules_btn = Button(DWIDTH // 2 - 85, 360, 205, 50, "Noteikumi")
        no_btn = Button(DWIDTH // 2 + 175, 360, 70, 50, "Nē")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if yes_btn.clicked(event):
                ingame_map()
                return
            if rules_btn.clicked(event):
                about_screen()
                return
            if no_btn.clicked(event):
                return

        pygame.draw.rect(screen, DW98, (DWIDTH // 4 - 75, 250, 570, 175))
        draw_text("Vai jūs vēlaties sākt ekskursiju?", txtfont, BLK, DWIDTH // 4 - 60, 260)

        yes_btn.draw()
        rules_btn.draw()
        no_btn.draw()

        pygame.display.update()
        clock.tick(30)


def exit_popup():
    while True:
        yes_btn = Button(DWIDTH // 4 - 10, 360, 70, 50, "Jā")
        no_btn = Button(DWIDTH // 2 + 145, 360, 70, 50, "Nē")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if yes_btn.clicked(event):
                quit_game()
            if no_btn.clicked(event):
                return

        pygame.draw.rect(screen, DW98, (DWIDTH // 4 - 40, 250, 490, 175))
        draw_text("Vai jūs vēlaties iziet?", txtfont, BLK, DWIDTH // 4 + 10, 260)

        yes_btn.draw()
        no_btn.draw()

        pygame.display.update()
        clock.tick(30)


def results_screen():
    result = read_results()

    while True:
        back_btn = Button(DWIDTH // 2 + 50, 400, 180, 50, "Atpakaļ")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if back_btn.clicked(event):
                return

        pygame.draw.rect(screen, DW98, (DWIDTH // 4 - 40, 180, 490, 290))
        draw_text("Rezultāti", txtfont, BLK, DWIDTH // 2 - 80, 190)
        draw_text(result, smalltxtfont, BLK, DWIDTH // 2 - 80, 300)

        back_btn.draw()
        draw_score()

        pygame.display.update()
        clock.tick(30)


def ending():
    save_results()

    while True:
        exit_btn = Button(630, 500, 120, 50, "Iziet")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if exit_btn.clicked(event):
                exit_popup()

        screen.fill(W98)
        draw_center_text("Paldies ka spēlējāt!", titlefont, BLK, DWIDTH // 2, DHEIGHT // 6)
        draw_text("Jūsu Liepājas ekskursija ir galā!", smalltxtfont, BLK, DWIDTH // 2 - 225, 150)
        draw_text(f"Jūsu punkti: {score}", smalltxtfont, BLK, DWIDTH // 2 - 225, 170)
        draw_text("Jūs varat savus rezultātus vēlāk apskatīties rezultātu logā", smalltxtfont, BLK, DWIDTH // 2 - 225, 190)

        exit_btn.draw()
        pygame.display.update()
        clock.tick(30)


def draw_tooltip(text_value, x, y):
    padding = 8
    text_surf = smalltxtfont.render(text_value, True, BLK)
    box_width = text_surf.get_width() + padding * 2
    box_height = text_surf.get_height() + padding * 2

    # Tooltip is slightly to the right and below the mouse.
    box_x = x + 15
    box_y = y + 15

    # Keep tooltip inside the window.
    if box_x + box_width > DWIDTH:
        box_x = x - box_width - 15
    if box_y + box_height > DHEIGHT:
        box_y = y - box_height - 15

    pygame.draw.rect(screen, DW98, (box_x, box_y, box_width, box_height))
    pygame.draw.rect(screen, BLK, (box_x, box_y, box_width, box_height), 2)
    screen.blit(text_surf, (box_x + padding, box_y + padding))


def ingame_map():
    global map_x, map_y

    try:
        map_img = pygame.image.load("map.png").convert()
    except pygame.error:
        screen.fill(W98)
        draw_text("Kļūda: map.png nav atrasts!", txtfont, RED, 100, 250)
        pygame.display.update()
        pygame.time.wait(2500)
        return

    # Start position is also limited to the real map size.
    min_x = DWIDTH - map_img.get_width()
    max_x = 0
    min_y = DHEIGHT - map_img.get_height()
    max_y = 0
    map_x = max(min_x, min(max_x, map_x))
    map_y = max(min_y, min(max_y, map_y))

    map_points = [
        MapPoint(843, 825, "Karostas Cietums", 0),
        MapPoint(802, 1285, "Sv. Trīsvienības katedrāle", 1),
        MapPoint(775, 1270, "Lielais Dzintars", 2),
        MapPoint(815, 777, "Sv. Nikolaja pareizticīgo Jūras katedrāle", 3),
        MapPoint(726, 1270, "Liepājas Muzejs", 4),
        MapPoint(665, 1320, "Spoku Koks", 5),
        MapPoint(790, 1312, "Romas Dārzs", 6),
        MapPoint(813, 1263, "Kārļa Zāles piemineklis", 7),
        MapPoint(751, 1350, "Sv. Jāzepa katedrāle", 8),
        MapPoint(707, 1280, "Liepājas himnas tēlu skulptūras", 9),
    ]

    while True:
        if all(visited):
            ending()
            return

        about_btn = Button(355, 550, 205, 45, "Noteikumi")
        exit_btn = Button(570, 550, 205, 45, "Iziet")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            if about_btn.clicked(event):
                about_screen()

            if exit_btn.clicked(event):
                exit_popup()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for point in map_points:
                    if not visited[point.level_index] and point.get_rect(map_x, map_y).collidepoint(event.pos):
                        completed = levels[point.level_index].show_info()
                        if completed:
                            visited[point.level_index] = True
                        break

        # Kartes kustināšana
        speed = 1000  # pixels per second
        dt = clock.get_time() / 1000  # seconds since last frame

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            map_x += speed * dt
        if keys[pygame.K_RIGHT]:
            map_x -= speed * dt
        if keys[pygame.K_UP]:
            map_y += speed * dt
        if keys[pygame.K_DOWN]:
            map_y -= speed * dt

        # Kartes robežas pēc īstā map.png izmēra.
        # Tāpēc nevar aizbraukt ne pa labi, ne pa kreisi, ne uz augšu, ne uz leju bezgalīgi.
        min_x = DWIDTH - map_img.get_width()
        max_x = 0
        min_y = DHEIGHT - map_img.get_height()
        max_y = 0

        map_x = max(min_x, min(max_x, map_x))
        map_y = max(min_y, min(max_y, map_y))

        screen.fill(W98)
        screen.blit(map_img, (map_x, map_y))

        for point in map_points:
            point.draw(map_x, map_y)

        # Apakšējā UI josla
        pygame.draw.rect(screen, DW98, (0, 490, 800, 110))
        about_btn.draw()
        exit_btn.draw()

        hovered_place = None
        for point in map_points:
            if not visited[point.level_index] and point.hovered(map_x, map_y):
                hovered_place = point.name
                draw_text(point.name, txtfont, BLK, 20, 500)
                break

        # Mazs logs ar vietas nosaukumu pie peles kursora
        if hovered_place:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            draw_tooltip(hovered_place, mouse_x, mouse_y)

        draw_score()
        pygame.display.update()
        clock.tick(60)


# ---------- Līmeņu dati ----------

levels = [
    Level(
        "Karostas Cietums",
        [
            "Karostas cietums jeb virssardze. Ēka celta",
            "ap 1900. gadu un līdz pat 1997. gadam kalpojusi",
            "kā militārpersonu disciplinārsodu izciešanas vieta.",
            "Cietums, no kura neviens nekad nav izbēdzis.",
        ],
        0, 2, 1,
        "images/karostas_cietums.jpg",
    ),
    Level(
        "Sv. Trīsvienības katedrāle",
        [
            "Katedrāle atrodas uz Lielās ielas. Tās pamatakmens",
            "likts 1742. gadā un iesvētīta 1758. gadā. Celtniecība",
            "pilnībā pabeigta 1866. gadā. Katedrāle ir bijusi lieciniece",
            "svarīgam Somijas valsts neatkarības notikumam.",
        ],
        4, 6, 5,
        "images/trisvienibas_katedrale.jpg",
    ),
    Level(
        "Lielais dzintars",
        [
            "Nacionālas un Eiropas nozīmes daudzfunkcionāls",
            "mākslas centrs. Tā tika celta divu gadu laikā no 2013.",
            "līdz 2015. Ēku projektēja Austriešu arhitekts Folkers",
            "Gīnke. Mājvieta Liepājas Simfoniskajam orķestrim.",
        ],
        8, 10, 9,
        "images/lielais_dzintars.jpg",
    ),
    Level(
        "Sv. Nikolaja Jūras katedrāle",
        [
            "Karostas vizuālā un garīgā dominante. Katedrāles",
            "celtniecība sākās 1901. gadā. Tās pamatakmens",
            "svinīgajā iesvētīšanas ceremonijā piedalījās arī",
            "Krievijas cars Nikolajs II ar ģimeni.",
        ],
        12, 14, 13,
        "images/nikolaja_juras_katedrale.jpg",
    ),
    Level(
        "Liepājas Muzejs",
        [
            "1924. gada 8. pamatskolas ēku atvēlēja muzeja",
            "iekārtošanai. Kopš 1935. gada ēkā atrodas pilsētas",
            "muzejs. Izcils 20. gadsimta sākuma Liepājas",
            "eklektisma arhitektūras paraugs.",
        ],
        16, 18, 17,
        "images/liepajas_muzejs.jpg",
    ),
    Level(
        "Spoku Koks",
        [
            "Veltīts latviešu leģendārajai rokgrupai “Līvi”.",
            "“Spoku Koks” ir iespaidīgs sešus metrus augsts koks",
            ", kas veidots no četriem tūkstošiem metāla stienīšu.",
            "Diennakts tumšajā laikā “Spoku koks” ir izgaismots.",
        ],
        20, 22, 21,
        "images/spoku_koks.jpg",
    ),
    Level(
        "Romas Dārzs",
        [
            "Veidota 19. gadsimtā kā tirdzniecības pasāža",
            "ar plašu un romantisku iekšpagalmu. Šobrīd ēkā",
            "atrodas viesnīca, beķereja, biroji un veikali, bet ēkas",
            "pazemes tuneļos ierīkota mākslas galerija ar veikalu.",
        ],
        24, 26, 25,
        "images/romas_darzs.jpg",
    ),
    Level(
        "Kārļa Zāles piemineklis",
        [
            "1989.gadā saistībā ar tēlnieka Kārļa Zāles",
            "100. dzimšanas dienu pilsēta izsludināja pieminekļa",
            "projektu konkursu. Par godu Latvijas valsts simtgadei",
            "un tēlnieka 130 gadu jubilejai piemineklis tika pabeigts.",
        ],
        28, 30, 29,
        "./images/karla_zales_piemineklis.jpg"
    ),
    Level(
        "Sv. Jāzepa katedrāle",
        [
            "Lielākais katoļu dievnams Kurzemē ar bagātīgu",
            "un greznu interjeru. Katedrāles vēsture sākās 1747. gadā,",
            "kad šajā vietā uzcēla nelielu mūra baznīcu. Baznīcas",
            "tornī ir ierīkota neliela izstāžu zāle.",
        ],
        32, 34, 33,
        "images/jazepa_katedrale.jpg",
    ),
    Level(
        "Liepājas himnas tēlu skulptūras",
        [
            "Vairākas skulptūras ar himnas tēliem veidoti no bronzas,",
            "kas izvietoti pa visu Kurmājas prospekta garumu.",
            "Pie katra tēla var atrast vienu himnas pantiņu. Ejot",
            "garām Liepājas vārnai, neaizmirsti paberzēt tās knābi. ;)",
        ],
        36, 38, 37,
        "images/himnas_telu_skulpturas.jpg",
    ),
]


if __name__ == "__main__":
    title_screen()

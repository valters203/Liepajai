from flask import Flask, render_template, request, session, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = 'secret_key'

# Load data
with open('data.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

questions = []
for i in range(0, len(lines), 3):
    if i+2 < len(lines):
        q = lines[i]
        opts = [opt.strip() for opt in lines[i+1].split(',')]
        ans = lines[i+2]
        questions.append({'question': q, 'options': opts, 'answer': ans})

locations = [
    "Karostas Cietums",
    "Sv. Trīsvienības katedrāle",
    "Lielais Dzintars",
    "Sv. Nikolaja Jūras katedrāle",
    "Liepājas Muzejs",
    "Spoku Koks",
    "Romas Dārzs",
    "Kārļa Zāles piemineklis",
    "Sv. Jāzepa katedrāle",
    "Liepājas himnas tēlu skulptūras"
]

descriptions = [
    ["Karostas cietums jeb virssardze. Ēka celta ", "ap 1900. gadu un līdz pat 1997. gadam kalpojusi","kā militārpersonu disciplinārsodu izciešanas vieta.", "Cietums, no kura neviens nekad nav izbēdzis."],
    ["Katedrāle atrodas uz Lielās ielas. Tās pamatakmens ","likts 1742. gadā un iesvētīta 1758. gadā. Celtniecība ", "pilnībā pabeigta 1866. gadā. Katedrāle ir bijusi lieciniece ", "svarīgam Somijas valsts neatkarības notikumam."],
    ["Nacionālas un Eiropas nozīmes daudzfunkcionāls","mākslas centrs. Tā tika celta divu gadu laikā no 2013. ", "līdz 2015. Ēku projektēja Austriešu arhitekts Folkers ", "Gīnke. Mājvieta Liepājas Simfoniskajam orķestrim."],
    ["Karostas vizuālā un garīgā dominante. Katedrāles ","celtniecība sākās 1901. gadā. Tās pamatakmens ", "svinīgajā iesvētīšanas ceremonijā piedalījās arī ", "Krievijas cars Nikolajs II ar ģimeni."],
    ["1924. gada 8. pamatskolas ēku atvēlēja muzeja ","iekārtošanai. Kopš 1935. gada ēkā atrodas pilsētas ", "muzejs. Izcils 20. gadsimta sākuma Liepājas ", "eklektisma arhitektūras paraugs."],
    ["Veltīts latviešu leģendārajai rokgrupai “Līvi”.","“Spoku Koks” ir iespaidīgs sešus metrus augsts koks", ", kas veidots no četriem tūkstošiem metāla stienīšu. ", "Diennakts tumšajā laikā “Spoku koks” ir izgaismots."],
    ["Veidota 19. gadsimtā kā tirdzniecības pasāža","ar plašu un romantisku iekšpagalmu. Šobrīd ēkā ", "atrodas viesnīca, beķereja, biroji un veikali, bet ēkas ", "pazemes tuneļos ierīkota mākslas galerija ar veikalu."],
    ["1989.gadā saistībā ar tēlnieka Kārļa Zāles ","100. dzimšanas dienu pilsēta izsludināja pieminekļa ", "projektu konkursu. Par godu Latvijas valsts simtgadei", "un tēlnieka 130 gadu jubilejai piemineklis tika pabeigts."],
    ["Lielākais katoļu dievnams Kurzemē ar bagātīgu ","un greznu interjeru. Katedrāles vēsture sākās 1747. gadā,", "kad šajā vietā uzcēla nelielu mūra baznīcu. Baznīcas ", "tornī ir ierīkota neliela izstāžu zāle."],
    ["Vairākas skulptūras ar himnas tēliem veidoti no bronzas,","kas izvietoti pa visu Kurmājas prospekta garumu.", "Pie katra tēla var atrast vienu himnas pantiņu. Ejot ", "garām Liepājas vārnai, neaizmirsti paberzēt tās knābi. ;)"]
]

# Images for each location (upload images to /static folder only)
images = [
    "karostas_cietums.jpg",  # 0: Karostas Cietums
    "trisvienibas_katedrale.jpg",  # 1: Sv. Trīsvienības katedrāle
    "lielais_dzintars.jpg",  # 2: Lielais Dzintars
    "nikolaja_juras_katedrale.jpg",  # 3: Sv. Nikolaja Jūras katedrāle
    "liepajas_muzejs.jpg",  # 4: Liepājas Muzejs
    "spoku_koks.jpg",  # 5: Spoku Koks
    "romas_darzs.jpg",  # 6: Romas Dārzs
    "karla_zales_piemineklis.jpg",  # 7: Kārļa Zāles piemineklis
    None,  # 8: Sv. Jāzepa katedrāle
    None   # 9: Liepājas himnas tēlu skulptūras
]

def reset_game():
    session.clear()
    session['score'] = 0
    session['visited'] = [False] * 10
    session['points'] = 5

@app.before_request
def init_session():
    if 'score' not in session:
        session['score'] = 0
    if 'visited' not in session:
        session['visited'] = [False] * 10
    if 'points' not in session:
        session['points'] = 5

@app.route('/')
def title():
    return render_template('title.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/start')
def start():
    return redirect(url_for('map'))

@app.route('/map')
def map():
    if all(session['visited']):
        return redirect(url_for('end'))
    return render_template('map.html', visited=session['visited'])

@app.route('/restart')
def restart():
    reset_game()
    return redirect(url_for('title'))

@app.route('/level/<int:id>')
def level(id):
    if session['visited'][id]:
        return redirect(url_for('map'))
    desc = descriptions[id]
    image = images[id]
    return render_template('level.html', id=id, name=locations[id], desc=desc, image=image)

@app.route('/play/<int:id>', methods=['GET', 'POST'])
def play(id):
    q = questions[id]
    if request.method == 'POST':
        answer = request.form['answer']
        if answer == q['answer']:
            session['score'] += session['points']
            session['points'] = 5
            session['visited'][id] = True
            session.modified = True
            return redirect(url_for('map'))
        else:
            if session['points'] > 1:
                session['points'] -= 2
            session.modified = True
            return render_template('play.html', id=id, q=q, wrong=True)
    return render_template('play.html', id=id, q=q, wrong=False)

@app.route('/results')
def results():
    try:
        with open('results.txt', 'r', encoding='utf-8') as f:
            last_score = f.read().strip()
    except:
        last_score = "Nav rezultātu"
    return render_template('results.html', score=session['score'], last=last_score)

@app.route('/end')
def end():
    with open('results.txt', 'w', encoding='utf-8') as f:
        f.write(f"Punkti: {session['score']}")
    return render_template('end.html', score=session['score'])

if __name__ == '__main__':
    app.run(debug=True)
import unittest
from app import app

class FlaskGameTests(unittest.TestCase):
    def setUp(self):
        # Konfigurējam aplikāciju testēšanas režīmam
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        self.client = app.test_client()

    def test_title_page(self):
        """Pārbauda, vai galvenā lapa (titullapa) atveras veiksmīgi."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Pārbauda, vai lapā ir atrodams atbilstošs teksts (ja base.html vai title.html to satur)
        # self.assertIn(b'M\xc4\x81c\xc4\xabbu ekskursija', response.data) # Opcionāli

    def test_about_page(self):
        """Pārbauda, vai lapa 'Par spēli' ielādējas ar 200 OK statusu."""
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)

    def test_start_redirect(self):
        """Pārbauda, vai /start maršruts pareizi pārvirza uz /map."""
        response = self.client.get('/start')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/map' in response.location)

    def test_session_initialization(self):
        """Pārbauda, vai spēles sākumā pareizi tiek inicializēti sesijas mainīgie."""
        with self.client as c:
            c.get('/map')
            with c.session_transaction() as sess:
                self.assertIn('score', sess)
                self.assertEqual(sess['score'], 0)
                
                self.assertIn('visited', sess)
                self.assertEqual(len(sess['visited']), 10)
                self.assertFalse(any(sess['visited'])) # Neviena vieta vēl nav apmeklēta
                
                self.assertIn('points', sess)
                self.assertEqual(sess['points'], 5)

    def test_restart_game(self):
        """Pārbauda spēles restarta funkcionalitāti un sesijas attīrīšanu."""
        with self.client as c:
            # Simulējam izmainītu sesiju (lietotājs spēlējis spēli)
            with c.session_transaction() as sess:
                sess['score'] = 25
                sess['points'] = 1
                sess['visited'] = [True] * 5 + [False] * 5
            
            # Izsaucam restart
            response = c.get('/restart')
            self.assertEqual(response.status_code, 302) # Pārvirza uz / (title)
            
            # Pārbaudām, vai sesija ir atiestatīta uz sākotnējām vērtībām
            with c.session_transaction() as sess:
                self.assertEqual(sess['score'], 0)
                self.assertEqual(sess['points'], 5)
                self.assertEqual(sess['visited'], [False] * 10)

    def test_level_access(self):
        """Pārbauda konkrēta līmeņa lapas atvēršanos."""
        with self.client as c:
            # Atveram pirmo lokāciju (0)
            response = c.get('/level/0')
            self.assertEqual(response.status_code, 200)
            # Pārliecināmies, ka lokācijas nosaukums parādās (piemēram, "Karostas Cietums")
            self.assertIn(b'Karostas Cietums', response.data)

    def test_visited_level_redirect(self):
        """Pārbauda, ka jau apmeklēts līmenis pārvirza atpakaļ uz karti."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess['visited'] = [True] * 10 # Uzstādām pirmo kā apmeklētu
            
            response = c.get('/level/0')
            # Ja līmenis ir apmeklēts, mūs jāpārvirza uz /map
            self.assertEqual(response.status_code, 302)
            self.assertTrue('/map' in response.location)

if __name__ == '__main__':
    unittest.main()

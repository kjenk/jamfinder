from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
def get(self):
    template_values = {
        'google_maps_api_key' : settings.GOOGLE_MAPS_API_KEY,
        'random' : random.random(),
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
    self.response.out.write(template.render(path, template_values))

if __name__ == '__main__':
    app.run()

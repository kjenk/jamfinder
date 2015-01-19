from application import app, models, views, db_create
import os

if app.config['DEBUG']:
    app.debug = True

app.config.from_pyfile(os.path.join(app.root_path, 'config.py'))



if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port)

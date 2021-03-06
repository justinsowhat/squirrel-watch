from flask import Flask

# template_dir = os.path.abspath('../templates')
app = Flask(__name__)
app.config.from_object('config.FlaskConfig')


if __name__ == '__main__':
    from views.modeling import *
    from views.errors import *
    from views.squirrel_not_squirrel import *
    from views.deep_hashing import *
    from views.login import *
    from views.feedback import *

    from database import models

    print app.url_map
    app.run(host='0.0.0.0', port=6800, debug=True)

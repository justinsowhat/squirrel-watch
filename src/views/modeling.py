from flask import request, render_template, flash, redirect, url_for
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input
from keras.models import load_model
from PIL import Image
import imagehash
import tensorflow as tf
import numpy as np
from flask_uploads import UploadSet, configure_uploads, IMAGES
from src.app import app
import os
from src.database.models import ModelHistory, UserLabel, SquirrelDescription


photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

model = load_model('modeling/retrained_model')
graph = tf.get_default_graph()


@app.route('/upload/<feature>', methods=['GET', 'POST'])
def upload(feature):
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        if feature == 'squirrel_not_squirrel':
            history = predict(filename)
            negation = '' if history.prediction else 'NOT'
            return render_template('pages/prediction.html', prediction=negation, filename=filename)
        if feature == 'which_squirrel':
            squirrel = get_hash(filename)
            return render_template('pages/matching.html', filename=squirrel.filename, description=squirrel.description)
    return render_template('forms/upload.html')


# @app.route('/predict', methods=['POST'])
def predict(filename):
    img = image.load_img(
        os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename),
        target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    global graph
    with graph.as_default():
        prediction_probability = float(model.predict(x))
    prediction = int(round(prediction_probability, 0))

    # DB
    history = ModelHistory.create(
        filename=filename,
        prediction_probability=prediction_probability,
        prediction=prediction
    )

    return history


def get_hash(filename):
    file_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
    hash = imagehash.average_hash(Image.open(file_path))
    num_of_pics = len(SquirrelDescription.all())
    pic_id = int(str(hash), 16) % num_of_pics + 1
    return SquirrelDescription.find(pic_id)


@app.route('/record_model_feedback', methods=['POST'])
def model_feedback():
    user_label = request.form['user_label']
    UserLabel.create(user_label=user_label)
    flash("Thank you for making squirrel-nado smarter!")
    return redirect(url_for('squirrel_not_squirrel'))


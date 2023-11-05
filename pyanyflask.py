import flask

app = flask.Flask(__name__)

@app.route('/')
def index():
    return flask.render_template('index.html')
    
@app.route('/mygame/build/web/index.html')
def game():
    return flask.send_file('build/web/index.html')
    
@app.route('/mygame/build/web/mysite.apk')
def apk():
    return flask.send_file('build/web/mysite.apk')


if __name__ == "__main__":
    app.run()
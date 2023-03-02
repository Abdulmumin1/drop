def flask_Server(files):
    from flask import Flask, render_template, send_file

    app = Flask(__name__)

    @app.route('/')
    def download_file():
        return send_file(files, as_attachment=True)

    app.run('192.168.43.14')


# flask_Server('/home/famira/Music/kivyCalculator.mp4')

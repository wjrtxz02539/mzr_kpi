from app import app, Control

Control.from_env()
Control.init()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=False)

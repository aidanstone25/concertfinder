from website import create_app
app = create_app()

if __name__ == '__main__':
    #TODO remove for production
    app.run(debug=True)
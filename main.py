from HTTPServer import *

def index(req: HTTPRequest, res: HTTPResponse):
    return res.text("Hello, world!")

def about(req: HTTPRequest, res: HTTPResponse):
    return res.text("About page!")

if __name__ == "__main__":
    app = HTTPServer()
    
    app.get("/", index)
    app.get("/about", about)

    app.listen(8000)
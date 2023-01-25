
import bottle
from bottle import route, run, template, put

value = 0


@route('/')
def index():
    #return "HELLO FROM RPI"
    return template('<h1>Value: {{value}}</h1><script>setInterval(function(){fetch("/value").then(res => res.text()).then(data => document.querySelector("h1").innerHTML = "Value: " + data)}, 50)</script>', value=value)


@route("/value")
def get_value():
    global value
    return str(value)

@put('/update/<new_value:int>')
def update(new_value):
    global value
    value = new_value
    return f"Value updated to {new_value}"


run(host='192.168.4.1', port=8000)

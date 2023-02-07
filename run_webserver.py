import time
import bottle
from bottle import route, run, template, put

value = 0


page_test = '''
<!DOCTYPE html>
<html>
<head>
<style>
.bar-graph {
  width: 50px; /* smaller width */
  height: 150px; /* smaller height */
  border: 1px solid black;
  float: left;
  margin-right: 10px; /* space between bar graphs */
}

.bar {
  width: 100%;
  height: 0;
  background-color: blue;
  transition: height 0.5s;
}

.message {
  text-align: center;
  font-size: 36px;
  margin-top: 50px;
  clear: both; /* clear the float */
}

.left-bar-graphs-container {
    float: left;
}

.right-bar-graphs-container {
    float: right;
}
</style>
</head>
<body>

<div class="left-bar-graphs-container">
  <div class="bar-graph">
    <div class="bar" id="bar1"></div>
  </div>
  <div class="bar-graph">
    <div class="bar" id="bar2"></div>
  </div>
  <div class="bar-graph">
    <div class="bar" id="bar3"></div>
  </div>
</div>
<div class="right-bar-graphs-container">
  <div class="bar-graph">
    <div class="bar" id="bar4"></div>
  </div>
  <div class="bar-graph">
    <div class="bar" id="bar5"></div>
  </div>
  <div class="bar-graph">
    <div class="bar" id="bar6"></div>
  </div>
</div>
<div class="message" id="message"></div>

<script>
  
  function updateValues() {
    // Call the route to retrieve the dictionary of values
    fetch('/value')
      .then(response => response.json())
      .then(data => {

        // Update the elements on the page with the values from the dictionary

        //document.getElementById("value1").innerHTML = data.value1;
        //document.getElementById("value2").innerHTML = data.value2;
        //document.getElementById("value3").innerHTML = data.value3;

        var bar1 = document.getElementById("bar1");
        var bar2 = document.getElementById("bar2");
        var bar3 = document.getElementById("bar3");
        var bar4 = document.getElementById("bar4");
        var bar5 = document.getElementById("bar5");
        var bar6 = document.getElementById("bar6");
        var message = document.getElementById("message");
    
          // Example values between -1 and 1
        //var values = [-0.5, 0.2, 0.8, -0.7, 0.1, -0.3];
        var values = [data.bar1, data.bar2, data.bar3, data.bar4, data.bar5, data.bar6];
        
        values.forEach(function(value, index) {
          var bar = eval("bar" + (index + 1));
          var height = (value + 1) * 75;
          bar.style.height = height + "px";
        });
    
        message.innerHTML = data.alert;
        
      });
  }
  
  // Call the updateValues function every 5 seconds
  setInterval(updateValues, 200); // milliseconds
  
</script>

</body>
</html>
'''



@route('/OLD')
def index():
    #return "HELLO FROM RPI"
    return template('<h1>Value: {{value}}</h1><script>setInterval(function(){fetch("/value").then(res => res.text()).then(data => document.querySelector("h1").innerHTML = data)}, 50)</script>', value=value)


@route('/')
def index():
    #return "HELLO FROM RPI"
    return page_test


@route("/value")
def get_value():
    global value
    return str(value)

@put('/update/<new_value>')
def update(new_value):
    global value
    value = new_value
    return f"Value updated to {new_value}"


# wait 10 seconds for wifi stuff to start working
time.sleep(10)
run(host='192.168.4.1', port=8000)

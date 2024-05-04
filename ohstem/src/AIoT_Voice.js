function mqtt_check_connection() {
    client.on("connect", function () {
      console.log("Connected")
    })
  }
  
  function mqtt_check_message() {
    client.on("message", (topic, message, packet) => {
      console.log("Received Message: " + message.toString() + " on topic: " + topic)
    })
  }
  
  function mqtt_subscribe(topic) {
    client.subscribe(options.username + /feeds/ + topic, { qos: 0 }, function (error, granted) {
      if (error) {
        console.log(error)
      } else {
        console.log(`${granted[0].topic} was subscribed`)
      }
    })
  }
  
  function mqtt_publish(topic, msg) {
    client.publish(options.username + /feeds/ + topic, msg, { qos: 0, retain: false }, function (error) {
      if (error) {
        console.log(error)
      } else {
        console.log("Published")
      }
    })
  }
  
  function p5speechRecGotResult() {
    background('#ffffff');
    text((p5SpeechRec.resultString.toLowerCase()) , 100, 250);
    if (new RegExp('bật đèn'.split(",").map(function(item) {return item.trim();}).join("|")).test(p5SpeechRec.resultString.toLowerCase()) || new RegExp('mở đèn'.split(",").map(function(item) {return item.trim();}).join("|")).test(p5SpeechRec.resultString.toLowerCase())) {
      mqtt_publish('V10', '1')
    } else if (new RegExp('tắt đèn'.split(",").map(function(item) {return item.trim();}).join("|")).test(p5SpeechRec.resultString.toLowerCase())) {
      mqtt_publish('V10', '0')
    } else {
      mqtt_publish('V13', 'Tôi Không Hiểu')
    }
  
  }
  
  function p5speechRecOnEnd() {
    p5SpeechRec.start();
  }
  
  function sleep(s) {
    ms = s * 1000
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  
  const clientId = 'mqttjs_' + Math.random().toString(16).substr(2, 8);
  
  const host = 'wss://mqtt.ohstem.vn:8084'
  
  const options = {clean: true,connectTimeout: 4000,clientId: clientId,username: '1852837',password: ''}
  
  const client = mqtt.connect(host, options);
  
  let p5SpeechRec = new p5.SpeechRec("vi-VN", p5speechRecGotResult);
  p5SpeechRec.onEnd = p5speechRecOnEnd;
  p5SpeechRec.continuous = true; // do continuous recognition
  
  function preload() {
  
  }
  
  function setup() {
    createCanvas(window.parent.document.getElementById('js-runner-container').offsetWidth-50, window.parent.document.getElementById('js-runner-container').offsetHeight-50);
  
    mqtt_check_connection()
    p5SpeechRec.start(); // start listening
  
  }
  
  function draw() {
  
  }
  
var counter_TUAN, counter_NHUNG;

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

function loadAIModel(fromLocal, URI, modelType) { // modelType = 0:image, 1:audio, 2:pose
  if (fromLocal) {
    if (modelType == 0) {  // video classification model
      const projects = JSON.parse(window.localStorage.getItem("ohstemai_projects"));
      let project;
      if (projects && projects.data && Boolean(projects.data)) {
        project = projects.data[URI];
      }

      parent.tf.loadLayersModel("indexeddb://" + project.id).then((layersModel) => {
        tmModel = new parent.tm.CustomMobileNet(layersModel, project.metadata);
      }).catch((err) => console.log(err));
    } else if (modelType == 1) {  // sound classification model
      // Load the model first
      const baseRecognizer = parent.spc.create("BROWSER_FFT");
      baseRecognizer
        .ensureModelLoaded()
        .then(() => {
          tmModelAudio = baseRecognizer.createTransfer(URI);
          console.log(`@tensorflow/speech-commands Transfer recognizer created (version ${parent.spc.version})`);
          console.log("loading model", URI);
          return tmModelAudio.load();
      })
      .then(() => tmModelAudio.ensureModelLoaded())
      .then(() => {
        console.log("loaded model", tmModelAudio);
        // Start classifying
        classifySound(true);
      })
      .catch((err) => console.log(err));
    }
  } else {
    if (modelType == 0) {
      imageClassifier = ml5.imageClassifier(URI + "model.json");
    } else {
      soundClassifier = ml5.soundClassifier(URI + "model.json");
    }
  }
}

function classifyVideoDelay(mirror, useLocalModel, continuous, delay) {
  if (!parent || Boolean(parent.isStopCode)) {return;}

  let videoImage = mirror?ml5.flipImage(videoCamera):videoCamera;
  if (useLocalModel) {
    if (tmModel) {
      tmModel.predict(mirror?videoImage.canvas:videoImage.elt).then((predictions) => {
        classifyVideoGotResult(undefined, predictions.sort((a, b) => b.probability - a.probability).map((p) => ({ label: p.className, confidence: p.probability })));
        if (continuous) {
          if (delay == 0) {
            classifyVideoDelay(mirror, useLocalModel, continuous, 0);
          }
          else {
            sleep(aiTimeDelay).then(() => classifyVideoDelay(mirror, useLocalModel, continuous, aiTimeDelay));
          }
        }
      }).catch((err) => classifyVideoGotResult(err, undefined));
    } else {
      setTimeout(classifyVideoDelay, 500, mirror, useLocalModel, continuous);
    }
  } else {
    imageClassifier.classify(videoImage, (err, results) => {
      if (err) {
        classifyVideoGotResult(err, undefined);
      } else {
        classifyVideoGotResult(undefined, results);
        if (continuous) {
          if (delay == 0) {
            classifyVideoDelay(mirror, useLocalModel, continuous, 0);
          }
          else {
            sleep(aiTimeDelay).then(() => classifyVideoDelay(mirror, useLocalModel, continuous, aiTimeDelay));
          }
        }
      }
    });
  }

  if (mirror) videoImage.remove();
}

function classifyVideoGotResult(error, classifyResults) {
  if (error) {
    console.error(error);
    return;
  }

  // handle result here
  background('#ffffff');
  text((classifyResults[0].label) , 100, 250);
  if (classifyResults[0].confidence.toFixed(2) > 0.7) {
    if (classifyResults[0].label == 'NHAN') {
      counter_TUAN = (typeof counter_TUAN === 'number' ? counter_TUAN : 0) + 1;
      counter_NHUNG = 0;
      if (counter_TUAN == 3) {
        counter_TUAN = 0;
        mqtt_publish('V13', 'Hello NHÂN')
        mqtt_publish('V14', 'A')
      }
    }
    if (classifyResults[0].label == 'NHUNG') {
      counter_NHUNG = (typeof counter_NHUNG === 'number' ? counter_NHUNG : 0) + 1;
      counter_TUAN = 0;
      if (counter_NHUNG == 3) {
        counter_NHUNG = 0;
        mqtt_publish('V13', 'Hello NHUNG')
        mqtt_publish('V14', 'B')
      }
    }
    if (classifyResults[0].label == 'ANH_NEN') {
      counter_NHUNG = 0;
      counter_TUAN = 0;
      mqtt_publish('V14', 'Z')
    }
  }

}

function sleep(s) {
  ms = s * 1000
  return new Promise(resolve => setTimeout(resolve, ms));
}


let videoCamera;
const clientId = 'mqttjs_' + Math.random().toString(16).substr(2, 8);

const host = 'wss://mqtt.ohstem.vn:8084'

const options = {clean: true,connectTimeout: 4000,clientId: clientId,username: '1852837',password: ''}

const client = mqtt.connect(host, options);

let imageClassifier;

let soundClassifier;

let aiTimeDelay;
let tmModel;

function preload() {
  loadAIModel(true, "", 0);
}

function setup() {
  createCanvas(window.parent.document.getElementById('js-runner-container').offsetWidth-50, window.parent.document.getElementById('js-runner-container').offsetHeight-50);
    videoCamera = createCapture({audio: false, video: {facingMode: "environment"}});
  videoCamera.size(width, height);
  videoCamera.hide();
  counter_TUAN = 0;
  counter_NHUNG = 0;

  mqtt_check_connection()
  aiTimeDelay = 1
  classifyVideoDelay(true, true, true, aiTimeDelay);

}

function draw() {
  let flippedImage = ml5.flipImage(videoCamera);
  image(flippedImage, 0, 0, 320, 240);
  flippedImage.remove();

}

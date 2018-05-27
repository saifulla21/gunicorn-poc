const WebSocket = require('ws');

let ws = new WebSocket('ws://0.0.0.0:8080/echo');
const stdin = process.openStdin();



stdin.addListener("data", function(d) {
    // note:  d is an object, and when converted to a string it will
    // end with a linefeed.  so we (rather crudely) account for that
    // with toString() and then trim()
    console.log("you entered: [" +
        d.toString().trim() + "]");
        ws.send(d.toString().trim());
  });
  ws.on('connection', function connection(ws) {
   ws.isAlive = true;
 });

ws.on('open', function open() {
    i = 0
    while (true){
        ws.send('select * from tenant_to_resource_map ')
        i = i +1
        if (i===1)
            break
    }

    ws.on('message', function incoming(data) {
      console.log(data);
      setTimeout(function timeout() {
          console.log('ping sent')
    ws.ping();
  }, 30000);
    });
});
ws.on('close', function close() {
  console.log('disconnected');
  ws = new WebSocket('ws://0.0.0.0:8080/echo');
});
ws.on('pong',function(data){
    console.log('data',data)
})

const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const serialportgsm = require('serialport-gsm');

const app = express();
const port = 3000;

app.use(cors());
app.use(bodyParser.json());

let modem = serialportgsm.Modem();
let options = {
    baudRate: 9600,
    dataBits: 8,
    stopBits: 1,
    parity: 'none',
    rtscts: false,
    xon: false,
    xoff: false,
    xany: false,
    autoDeleteOnReceive: true,
    enableConcatenation: true,
    incomingCallIndication: true,
    incomingSMSIndication: true, // Necessary for onNewMessage
    pin: '1234',
    customInitCommand: '',
    logger: console
};

let modemReady = false;

modem.open('COM10', options, {});

modem.on('open', data => {
    modem.initializeModem((data) => {
        console.log('Modem initialized');
        modemReady = true;
    });
});

modem.on('onSendingMessage', result => {
    console.log(result);
});

modem.on('onMessageSent', result => {
    console.log(result);
});

app.post('/send-sms', (req, res) => {
    const { number, message } = req.body;
    if (!modemReady) {
        return res.status(503).send('Modem is not ready.');
    }
    let responded = false;
    modem.sendSMS(number, message, true, (data) => {
        if (!responded) {
            responded = true;
            if (data.status === 'success') {
                res.send('SMS sent successfully!');
            } else {
                res.status(500).send('Failed to send SMS.');
            }
        }
    });
    // Fallback: ensure response is sent if callback is never called
    setTimeout(() => {
        if (!responded) {
            responded = true;
            res.status(504).send('SMS sending timed out.');
        }
    }, 15000); // 15 seconds timeout
});

app.listen(port, () => {
    console.log(`SMS server listening at http://localhost:${port}`);
});
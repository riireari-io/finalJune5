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
    pin: '1234', // CRITICAL: Verify this PIN or set to '' if no PIN
    customInitCommand: '',
    logger: console
};

let modemReady = false;

console.log(`Attempting to open modem on COM10 with options:`, JSON.stringify(options)); // Enhanced log
modem.open('COM10', options, {}); // CRITICAL: Verify COM10 in Device Manager

modem.on('open', data => {
    console.log('Modem port opened. Initializing modem...'); // Enhanced log
    modem.initializeModem((initData) => { 
        console.log('Modem initializeModem callback received:', initData); // Enhanced log
        console.log('Modem initialized'); // Your original log
        modemReady = true; // Your original logic
    });
});

modem.on('error', err => { // Added explicit error handler for modem open/general errors
    console.error('Modem error event:', err);
    modemReady = false;
});

modem.on('onSendingMessage', result => {
    console.log('onSendingMessage:', result); // Enhanced log (added prefix for clarity)
});

modem.on('onMessageSent', result => {
    console.log('onMessageSent:', result); // Enhanced log (added prefix for clarity)
});

app.post('/send-sms', (req, res) => {
    const { number, message } = req.body;
    console.log(`Received /send-sms request. Number: ${number}, Message: "${message}"`); // Enhanced log
    if (!modemReady) {
        console.warn('Attempt to send SMS, but modem is not ready.'); // Enhanced log
        return res.status(503).send('Modem is not ready.'); // Your original logic
    }
    let responded = false;
    console.log(`Attempting to send SMS to ${number}...`); // Enhanced log
    modem.sendSMS(number, message, true, (callbackData) => {
        console.log(`modem.sendSMS callback data for ${number}:`, callbackData); // Enhanced log
        if (!responded) {
            responded = true;
            if (callbackData.status === 'success') {
                console.log(`SMS successfully queued for ${number}. Modem library reported: ${callbackData.data && callbackData.data.response ? callbackData.data.response : 'OK'}`); // Enhanced log
                res.send('SMS sent successfully!'); // Your original logic
            } else {
                console.error(`Failed to send SMS to ${number}. Modem library reported: Status: ${callbackData.status}, Response: ${callbackData.data && callbackData.data.response ? callbackData.data.response : (callbackData.message || 'N/A')}`); // Enhanced log
                res.status(500).send('Failed to send SMS.'); // Your original logic
            }
        }
    });
    // Fallback: ensure response is sent if callback is never called
    setTimeout(() => {
        if (!responded) {
            responded = true;
            console.warn(`SMS sending to ${number} timed out after 15 seconds.`); // Enhanced log
            res.status(504).send('SMS sending timed out.'); // Your original logic
        }
    }, 15000); // 15 seconds timeout
});

app.listen(port, () => {
    console.log(`SMS server listening at http://localhost:${port}`);
});
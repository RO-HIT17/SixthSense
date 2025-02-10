const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const client = new Client({
    authStrategy: new LocalAuth()
});

client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('WhatsApp Bot is ready!');
});

client.on('message', message => {
    if (!message.isStatus && message.hasMedia === false) {
        console.log(`📩 New Message from ${message.from}: ${message.body}`);
    }
});

client.initialize();

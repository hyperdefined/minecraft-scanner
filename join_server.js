const mineflayer = require('mineflayer')
const dotenv = require("dotenv")

const serverAddress = process.argv[2];
const serverPort = parseInt(process.argv[3]);

dotenv.config()

const bot = mineflayer.createBot({
  host: serverAddress,
  username: process.env.MINECRAFT,
  auth: 'microsoft',
  port: serverPort
})

bot.once('login', () => {
    bot.chat("Hello! I am a server scanner bot!")
    bot.chat("/pl")
    console.log("Logged into server " + serverAddress);
    // Leave the server after 5 seconds
    setTimeout(() => {
        bot.quit();
        process.exit(0)
    }, 5000);
});
bot.on('chat', (username, message) => {
  if (username === bot.username) return;
  console.log(`<${username}> ${message}`)
})
bot.on('messagestr', (message) => {
  console.log(`${message}`)
})
bot.once('kicked', (reason) => {
  console.log('Kicked from ' + serverAddress + ' for reason: ' + reason);
  process.exit(0);
});
bot.once('error', () => {
  console.log('Error from ' + serverAddress);
  process.exit(0)
});
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
    console.log('Logged into server ' + serverAddress);
    if (!bot.players || Object.keys(bot.players).length === 0) {
      console.log('There are no players online.');
    } else {
      console.log(`Players online: ${Object.keys(bot.players).join(', ')}`);
    }
    // Leave the server after 5 seconds
    setTimeout(() => {
        bot.quit();
        process.exit(0)
    }, 5000);
});
bot.once('kicked', (reason) => {
  console.log('Kicked from ' + serverAddress + ' for reason: ' + reason);
  process.exit(0);
});

bot.once('error', () => {
  console.log('Error from ' + serverAddress);
  process.exit(0)
});
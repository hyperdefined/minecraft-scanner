const mineflayer = require('mineflayer')
const dotenv = require("dotenv")

const serverAddress = process.argv[2];
const serverPort = parseInt(process.argv[3]);

dotenv.config()

const bot = mineflayer.createBot({
  host: serverAddress, // minecraft server ip
  username: process.env.MINECRAFT, // minecraft username
  auth: 'microsoft', // for offline mode servers, you can set this to 'offline'
  port: serverPort                // only set if you need a port that isn't 25565
  // version: false,             // only set if you need a specific version or snapshot (ie: "1.8.9" or "1.16.5"), otherwise it's set automatically
  // password: '12345678'        // set if you want to use password-based auth (may be unreliable)
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
const { createBot, toMotd, waitFor } = require('./lib');

const VERSION = process.env.MC_VERSION;
const BOT = process.env.BOT_NAME || 'ColorBotC';
const FIRST_COLOR = process.env.FIRST_COLOR || 'red';
const SECOND_COLOR = process.env.SECOND_COLOR || 'green';

const chats = [];
const result = { ok: false, errors: [], chats: [] };

async function main() {
  const bot = createBot(BOT, VERSION);

  bot.on('error', (err) => result.errors.push(err.message));
  bot.on('message', (message) => chats.push(toMotd(message)));

  await waitFor(() => bot.entity, 30000, 'bot spawn');

  bot.chat(`!!color ${FIRST_COLOR}`);
  await waitFor(
    () => chats.some((line) => line.includes(BOT) && line.toLowerCase().includes(FIRST_COLOR)),
    15000,
    `first color (${FIRST_COLOR}) confirmation`,
  );

  chats.length = 0;
  bot.chat(`!!color ${SECOND_COLOR}`);
  await waitFor(
    () => chats.some((line) => line.includes(BOT) && line.toLowerCase().includes(SECOND_COLOR)),
    15000,
    `second color (${SECOND_COLOR}) confirmation`,
  );

  result.ok = true;
  bot.quit();
}

main()
  .catch((err) => result.errors.push(String(err)))
  .finally(() => {
    result.chats = chats.slice(0, 50);
    console.log(JSON.stringify(result));
    process.exit(result.ok ? 0 : 1);
  });

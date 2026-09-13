const { createBot, toMotd, trailingColorCode, waitFor } = require('./lib');

const VERSION = process.env.MC_VERSION;
const COLOR = process.env.BOT_COLOR || 'red';
const COLOR_CODE = process.env.BOT_COLOR_CODE || 'c';
const BOT_A = 'ColorBotA';
const BOT_B = 'ColorBotB';
const CHAT = 'hello-from-A';

async function main() {
  const result = { ok: false, aCode: null, bCode: null, aLine: null, bLine: null, errors: [] };
  const botA = createBot(BOT_A, VERSION);
  const botB = createBot(BOT_B, VERSION);
  const chatsA = [];
  const chatsB = [];

  botA.on('error', (err) => result.errors.push(`A: ${err.message}`));
  botB.on('error', (err) => result.errors.push(`B: ${err.message}`));
  botA.on('message', (message) => chatsA.push(toMotd(message)));
  botB.on('message', (message) => chatsB.push(toMotd(message)));

  await waitFor(() => botA.entity, 30000, 'bot A spawn');
  await waitFor(() => botB.entity, 30000, 'bot B spawn');

  botA.chat(`!!color ${COLOR}`);
  await waitFor(
    () => chatsA.some((line) => line.includes(BOT_A) && line.toLowerCase().includes(COLOR)),
    15000,
    'color confirmation on bot A',
  );

  chatsA.length = 0;
  chatsB.length = 0;
  botA.chat(CHAT);
  const aLine = await waitFor(() => chatsA.find((line) => line.includes(CHAT)), 15000, 'chat on bot A');
  const bLine = await waitFor(() => chatsB.find((line) => line.includes(CHAT)), 15000, 'chat on bot B');

  result.aLine = aLine;
  result.bLine = bLine;
  result.aCode = trailingColorCode(aLine, BOT_A);
  result.bCode = trailingColorCode(bLine, BOT_A);
  result.ok = result.aCode === COLOR_CODE && result.bCode === COLOR_CODE;

  botA.quit();
  botB.quit();
  console.log(JSON.stringify(result));
  process.exit(result.ok ? 0 : 1);
}

main().catch((err) => {
  console.log(JSON.stringify({ ok: false, errors: [String(err)] }));
  process.exit(1);
});

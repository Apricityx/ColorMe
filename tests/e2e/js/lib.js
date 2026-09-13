const mineflayer = require('mineflayer');

function createBot(username, version) {
  return mineflayer.createBot({
    host: process.env.MC_HOST || '127.0.0.1',
    port: parseInt(process.env.MC_PORT || '25565', 10),
    username: username,
    version: version,
    auth: 'offline',
  });
}

function toMotd(message) {
  try {
    return message.toMotd();
  } catch (err) {
    return JSON.stringify(message.json);
  }
}

function trailingColorCode(text, name) {
  const index = text.indexOf(name);
  if (index < 0) {
    return null;
  }
  const before = text.slice(0, index);
  const pattern = /§([0-9a-fk-or])/g;
  let code = null;
  let match;
  while ((match = pattern.exec(before)) !== null) {
    code = match[1];
  }
  return code;
}

async function waitFor(predicate, timeoutMs, label) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const value = predicate();
    if (value) {
      return value;
    }
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  throw new Error(`timeout waiting for ${label}`);
}

module.exports = { createBot, toMotd, trailingColorCode, waitFor };

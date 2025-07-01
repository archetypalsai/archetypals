require('dotenv').config(); // Load from .env by default

const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { validatedRequest } = require('./utils/middleware/validatedRequest');
const { Pinecone } = require('./utils/pinecone');
const { reqBody } = require('./utils/http');
const { systemEndpoints } = require('./endpoints/system');
const { workspaceEndpoints } = require('./endpoints/workspaces');
const { chatEndpoints } = require('./endpoints/chat');

const app = express();

// Middleware
app.use(cors({ origin: true }));
app.use(validatedRequest);
app.use(bodyParser.text());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Endpoints
systemEndpoints(app);
workspaceEndpoints(app);
chatEndpoints(app);

// Pinecone command route
app.post('/v/:command', async (req, res) => {
  const { command } = req.params;
  if (!Object.getOwnPropertyNames(Pinecone).includes(command)) {
    res.status(500).json({
      message: 'invalid interface command',
      commands: Object.getOwnPropertyNames(Pinecone.prototype),
    });
    return;
  }

  try {
    const body = reqBody(req);
    const resBody = await Pinecone[command](body);
    res.status(200).json({ ...resBody });
  } catch (e) {
    console.error(JSON.stringify(e));
    res.status(500).json({ error: e.message });
  }
});

// Health check route
app.get('/', (req, res) => {
  res.status(200).send('AnythingLLM server is up and running!');
});

// 404 fallback
app.all('*', (_, res) => {
  res.sendStatus(404);
});

// Server start
const PORT = process.env.SERVER_PORT || 3001; // Change to your desired default

app.listen(process.env.SERVER_PORT || 3001, '0.0.0.0', () => {
  console.log(`Example app listening on port ${process.env.SERVER_PORT || 3001}`)
}).on('error', (err) => {
  console.error('Server error:', err);
  process.once('SIGUSR2', () => process.kill(process.pid, 'SIGUSR2'));
  process.on('SIGINT', () => process.kill(process.pid, 'SIGINT'));
});

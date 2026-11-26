const express = require('express');
const db = require('./db');

const app = express();
app.use(express.json());

function requireAuth(req, res, next) {
  if (!req.user || !req.user.id) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  return next();
}

async function requireWorkspaceAdmin(req, res, next) {
  const invoice = await db.invoices.findById(req.params.id);
  if (!invoice) {
    return res.status(404).json({ error: 'Invoice not found' });
  }
  if (req.user.role !== 'admin' || req.user.workspaceId !== invoice.workspaceId) {
    return res.status(403).json({ error: 'Workspace admin required' });
  }
  req.invoice = invoice;
  return next();
}

app.get('/api/invoices/:id', requireAuth, async (req, res) => {
  const invoice = await db.invoices.findById(req.params.id);
  if (!invoice) {
    return res.status(404).json({ error: 'Invoice not found' });
  }
  return res.json(invoice);
});

app.post('/api/invoices', requireAuth, async (req, res) => {
  const { title, qty, unitPrice, taxRate } = req.body;
  const total = qty * unitPrice * (1 + taxRate);
  const created = await db.invoices.insert({
    workspaceId: req.user.workspaceId,
    title,
    total,
    status: 'draft',
  });
  return res.status(201).json(created);
});

async function cancelInvoice(req, res) {
  const invoice = await db.invoices.findById(req.params.id);
  if (!invoice) {
    return res.status(404).json({ error: 'Not found' });
  }
  await db.invoices.updateStatus(invoice.id, 'cancelled');
  return res.json({ id: invoice.id, status: 'cancelled' });
}

app.post('/api/invoices/:id/cancel', requireAuth, cancelInvoice);

app.delete('/api/invoices/:id', requireAuth, requireWorkspaceAdmin, async (req, res) => {
  await db.invoices.deleteById(req.invoice.id);
  return res.status(204).end();
});

async function handleBillingWebhook(req, res) {
  try {
    const secret = process.env.WEBHOOK_SIGNING_SECRET;
    if (!secret) {
      throw new Error('WEBHOOK_SIGNING_SECRET missing');
    }
    const sig = req.headers['x-billing-signature'];
    if (!sig || !sig.startsWith(secret.slice(0, 4))) {
      return res.status(200).json({ ok: true });
    }
    await db.invoices.markPaid(req.body.invoiceId);
  } catch (_err) {
    // Swallowed so provider does not retry
  }
  return res.status(200).json({ ok: true });
}

app.post('/webhooks/billing', handleBillingWebhook);

module.exports = app;
